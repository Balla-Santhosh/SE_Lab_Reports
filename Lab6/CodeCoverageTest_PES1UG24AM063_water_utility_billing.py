"""
Lab 6 - Code (Line) Coverage Tests
Name : Balla Santhosh
SRN  : PES1UG24AM063
Module under test: water_utility_billing.py

Goal: execute every line of the module at least once (>= 90% line coverage).
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
