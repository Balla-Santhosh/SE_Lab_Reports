"""
Lab 7 - Fixed (hardened) processor.py
Name : Balla Santhosh
SRN  : PES1UG24AM063

Bugs found by Hypothesis fuzzing and how they are fixed:
  sanitize_meter_id
    - None / non-string input -> AttributeError on .strip()      => return ""
    - whitespace left behind after removing prefix symbols        => strip AFTER removal
  parse_consumption_readings
    - None / non-string input -> AttributeError on .split()       => return []
    - empty string / empty element ("1,,3") -> ValueError          => skip empty tokens
    - non-numeric tokens ("abc", "1.5") -> ValueError              => skip invalid tokens
    - surrounding spaces (" 10 , 20") handled                       => strip each token
  format_billing_summary
    - None / non-string input -> AttributeError on .split()       => "Invalid record"
    - too few fields ("", "Name") -> IndexError                     => "Invalid record"
    - empty / non-numeric / negative usage -> ValueError            => "Invalid record"
    - empty name or zone                                            => "Unknown"
"""

INVALID_RECORD = "Invalid record: expected format Name:Usage:Zone with a non-negative integer usage"


def sanitize_meter_id(meter_id):
    if not isinstance(meter_id, str):
        return ""
    for ch in ['!', '@', '#', '$', '%']:
        meter_id = meter_id.replace(ch, '')
    # strip after removing symbols (and after upper(), which can change characters)
    return meter_id.upper().strip()


def parse_consumption_readings(readings_csv):
    if not isinstance(readings_csv, str):
        return []
    readings = []
    for token in readings_csv.split(','):
        token = token.strip()
        if not token:
            continue
        try:
            readings.append(int(token))
        except ValueError:
            # skip malformed values instead of crashing
            continue
    return readings


def format_billing_summary(account_record):
    if not isinstance(account_record, str):
        return INVALID_RECORD
    parts = account_record.split(':')
    if len(parts) != 3:
        return INVALID_RECORD
    customer_name = parts[0].strip() or "Unknown"
    zone = parts[2].strip() or "Unknown"
    try:
        units = int(parts[1].strip())
    except ValueError:
        return INVALID_RECORD
    if units < 0:
        return INVALID_RECORD
    return f"Customer {customer_name} billed {units * 2} USD in {zone}"


def main():
    print("==== Running sanitize_meter_id ====")
    raw_id = input("Enter a meter ID with prefixes (!,@,#,$,%): ")
    clean_id = sanitize_meter_id(raw_id)
    print("Sanitized Meter ID:", clean_id)

    print("\n==== Running parse_consumption_readings ====")
    csv_input = input("Enter consumption readings (e.g. 10,25,30): ")
    readings_list = parse_consumption_readings(csv_input)
    print("Parsed Readings:", readings_list)

    print("\n==== Running format_billing_summary ====")
    summary_input = input("Enter account record (Name:Usage:Zone): ")
    summary = format_billing_summary(summary_input)
    print("Billing Summary:", summary)


if __name__ == "__main__":
    main()
