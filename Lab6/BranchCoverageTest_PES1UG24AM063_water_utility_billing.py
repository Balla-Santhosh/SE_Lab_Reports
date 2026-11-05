"""
Lab 6 - Branch Coverage Tests
Name : Balla Santhosh
SRN  : PES1UG24AM063
Module under test: water_utility_billing.py

Goal: make every decision (if / for / elif) evaluate both True and False
(>= 90% branch coverage). Builds on the code-coverage tests and adds the
missing False-side branches.
"""
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def make_account(usage_blocks, is_active=True, is_commercial=False, has_leak_waiver=False):
    return {
        "is_active": is_active,
        "is_commercial": is_commercial,
        "has_leak_waiver": has_leak_waiver,
        "usage_blocks": usage_blocks,
    }


# ---------------- calculate_water_bill ----------------

def test_single_active_residential():
    # starter test: 10 + 30*1.5 = 55
    result = calculate_water_bill([make_account([30])], 10.0)
    assert result["total_billed"] == 55.0
    assert result["status"] == "NORMAL"


def test_invalid_accounts_type_raises():
    with pytest.raises(ValueError):
        calculate_water_bill("not a list", 10.0)


def test_inactive_account_is_skipped():
    # only inactive account -> nothing billed -> NO_ACTIVITY
    result = calculate_water_bill([make_account([30], is_active=False)], 0.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_non_positive_usage_is_flagged_and_skipped():
    # 0 and -5 are skipped; 20*1.5 = 30 ; total = 10 + 30
    result = calculate_water_bill([make_account([0, -5, 20])], 10.0)
    assert result["total_billed"] == 40.0


def test_medium_usage_tier():
    # 60 -> 2.5 rate : 10 + 150 = 160
    result = calculate_water_bill([make_account([60])], 10.0)
    assert result["total_billed"] == 160.0


def test_residential_over_100_breaks_loop():
    # 120*4.5 = 540, then break (the 30 block is never billed)
    result = calculate_water_bill([make_account([120, 30])], 10.0)
    assert result["total_billed"] == 550.0


def test_commercial_over_100_uses_commercial_rate():
    # 200*3.5 = 700 ; 10 + 700 = 710
    result = calculate_water_bill([make_account([200], is_commercial=True)], 10.0)
    assert result["total_billed"] == 710.0


def test_leak_waiver_applied_above_200():
    # 10 + 60*2.5 + 50*1.5 = 235 -> waiver -50 = 185
    result = calculate_water_bill([make_account([60, 50], has_leak_waiver=True)], 10.0)
    assert result["total_billed"] == 185.0


def test_excessive_flags_status():
    # six non-positive blocks -> 6 flags > 5
    result = calculate_water_bill([make_account([0, 0, 0, -1, -1, -1])], 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


# ---------------- check_meter_tampering ----------------

def test_tampering_no_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_tampering_suspected_two_consecutive_negatives():
    assert check_meter_tampering([[5, -1, -2, 3]]) == "TAMPER_SUSPECTED"


def test_tampering_clear():
    assert check_meter_tampering([[5, -1, 4, 2]]) == "CLEAR"


# ---------------- extra tests for missing branches ----------------

def test_negative_base_fee_raises():
    # second half of the `or` in the validation check
    with pytest.raises(ValueError):
        calculate_water_bill([], -1.0)


def test_empty_accounts_list_no_activity():
    # outer for-loop body never executes
    result = calculate_water_bill([], 0.0)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


def test_leak_waiver_not_applied_at_or_below_200():
    # waiver present but total = 10 + 40*1.5 = 70  (<= 200) -> no deduction
    result = calculate_water_bill([make_account([40], has_leak_waiver=True)], 10.0)
    assert result["total_billed"] == 70.0


def test_leak_waiver_boundary_exactly_200():
    # 100 is NOT > 100, so mid tier: 100*2.5 = 250 (> 200) -> waiver -> 200
    result = calculate_water_bill([make_account([100], has_leak_waiver=True)], 0.0)
    assert result["total_billed"] == 200.0
    # exactly 200 is not > 200, so no waiver: 50 + 60*2.5 = 200
    result = calculate_water_bill([make_account([60], has_leak_waiver=True)], 50.0)
    assert result["total_billed"] == 200.0


def test_missing_keys_use_defaults():
    # account with no keys -> is_active defaults to False -> skipped
    assert calculate_water_bill([{}], 10.0)["status"] == "NO_ACTIVITY"
    # active but no usage_blocks -> only the base fee
    result = calculate_water_bill([{"is_active": True}], 10.0)
    assert result == {"total_billed": 10.0, "status": "NORMAL"}


def test_tier_boundaries_50_and_100():
    # 50 -> low tier (1.5), 51 -> mid tier (2.5), 100 -> mid tier, 101 -> high
    assert calculate_water_bill([make_account([50])], 0.0)["total_billed"] == 75.0
    assert calculate_water_bill([make_account([51])], 0.0)["total_billed"] == 127.5
    assert calculate_water_bill([make_account([100])], 0.0)["total_billed"] == 250.0
    assert calculate_water_bill([make_account([101], is_commercial=True)], 0.0)["total_billed"] == 353.5


def test_commercial_over_100_continues_loop():
    # commercial does NOT break: 150*3.5 + 20*1.5 = 525 + 30 ; +10 base
    result = calculate_water_bill([make_account([150, 20], is_commercial=True)], 10.0)
    assert result["total_billed"] == 565.0


def test_exactly_five_flags_is_not_excessive():
    # 5 flags is not > 5 ; a positive block keeps total > 0 -> NORMAL
    result = calculate_water_bill([make_account([0, 0, 0, 0, 0, 10])], 0.0)
    assert result["status"] == "NORMAL"


def test_multiple_accounts_mixed():
    accounts = [
        make_account([30]),                         # 10 + 45 = 55
        make_account([30], is_active=False),        # skipped
        make_account([200], is_commercial=True),    # 10 + 700 = 710
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result == {"total_billed": 765.0, "status": "NORMAL"}


def test_tampering_empty_meter_and_multiple_meters():
    # meter with no readings -> inner loop skipped ; second meter tampered
    assert check_meter_tampering([[], [1, 2]]) == "CLEAR"
    assert check_meter_tampering([[1, 2], [-1, -1]]) == "TAMPER_SUSPECTED"


def test_tampering_single_negative_not_suspected():
    assert check_meter_tampering([[-1]]) == "CLEAR"
    assert check_meter_tampering([[0, -3, 0, -3]]) == "CLEAR"
