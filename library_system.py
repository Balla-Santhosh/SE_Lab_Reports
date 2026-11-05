"""Library Fine and Book Renewal System.

A small tracker for a campus library: records which student has borrowed
which book, works out overdue fines, handles renewals and saves the loan
records to a JSON file.
"""
import ast
import json
import operator
from datetime import datetime

# Module-level state (mutated in place, never rebound)
loans = {}
FINE_PER_DAY = 2
LONG_RENEWAL_DAYS = 14

def add_book_loan(student_id, book_id, dates=None):
    """Record that student_id has borrowed book_id and return the loan dates list."""
    if dates is None:
        dates = []
    if not student_id:
        print(f"Cannot record loan of {book_id}: student id is missing")
        return dates
    if not isinstance(book_id, str):
        print(f"Cannot record loan for {student_id}: book id {book_id!r} must be a string")
        return dates
    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [book_id]
    print(f"{student_id} borrowed {book_id} (loan dates on record: {len(dates)})")
    return dates

def return_book(student_id, book_id):
    """Remove book_id from the loans of student_id."""
    try:
        loans[student_id].remove(book_id)
        if len(loans[student_id]) == 0:
            del loans[student_id]
    except (KeyError, ValueError):
        print(f"No loan of {book_id} found for {student_id}")

def calculate_fine(days_overdue, fine_per_day=FINE_PER_DAY):
    """Return the fine for days_overdue days; negative days are treated as zero."""
    return max(0, days_overdue) * fine_per_day

def renew_book(student_id, book_id, extra_days):
    """Renew a loan and return the fine rate that applies to this loan only."""
    fine_per_day = FINE_PER_DAY
    if extra_days > LONG_RENEWAL_DAYS:
        fine_per_day = FINE_PER_DAY + 1
    print(f"Renewed {book_id} for {student_id} by {extra_days} days (fine rate: {fine_per_day}/day)")
    return fine_per_day

def load_records(file="loans.json"):
    """Load loan records from a JSON file into the module-level loans dict."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        print(f"Could not load records from {file}: {err}")
        return
    loans.clear()
    loans.update(data)

def save_records(file="loans.json"):
    """Save the module-level loans dict to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(loans, f)

_ALLOWED_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

def _eval_node(node, days):
    """Evaluate a parsed fine-rule node, allowing only numbers, 'days' and + - * /."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, days)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "days":
        return days
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.left, days), _eval_node(node.right, days))
    raise ValueError("Unsupported expression in fine rule")

def fine_from_rule(rule, days):
    """Compute a fine from a simple arithmetic rule such as 'days * 2 + 10'."""
    return _eval_node(ast.parse(rule, mode="eval"), days)

def print_report():
    """Print every student and the books they currently have on loan."""
    print("Loan Report")
    for student, books in loans.items():
        print(student, "->", books)

def main():
    """Run a short demonstration of the library system."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", 4521)  # rejected: book id must be a string
    return_book("S999", "B-NONE")
    rate = renew_book("S101", "B-ALGO", 21)
    print("Fine for 5 days (S101 after long renewal):", calculate_fine(5, rate))
    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))
    raw = input("Days overdue for S102 (press Enter for 0): ").strip() or "0"
    try:
        days = int(raw)
    except ValueError:
        print(f"'{raw}' is not a whole number, using 0")
        days = 0
    print("S102 owes:", calculate_fine(days))
    save_records()
    load_records()
    print_report()

if __name__ == "__main__":
    main()
