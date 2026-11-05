# Issues Found and Fixed — `library_system.py`

**Name:** Balla Santhosh  **SRN:** PES1UG24AM063
**Repo:** L5_01_library_fines (Library Fine and Book Renewal System)

Line numbers refer to the **original** starter file. Reports are in `reports/before/` and `reports/after/`.

| Score | Before | After |
|-------|--------|-------|
| Pylint | 6.07/10 (22 messages) | **10.00/10** |
| Bandit | 2 issues (1 Medium, 1 Low) | **0 issues** |
| Flake8 | 14 violations | **0 violations** |

## High / medium severity

| # | Issue | Type | Line(s) | Tool / Code | Description | Fix Approach |
|---|-------|------|---------|-------------|-------------|--------------|
| 1 | Use of `eval` | Security | 45 | Bandit B307 (Medium), Pylint W0123 | `fine_from_rule` runs `eval()` on a rule string, so any Python code passed in as a "rule" would be executed (code injection). | Replaced with a small safe evaluator: parse with `ast.parse(..., mode="eval")` and walk the tree, allowing only numeric constants, the name `days` and `+ - * /`. Anything else raises `ValueError`. |
| 2 | Mutable default argument | Bug | 9, 12 | Pylint W0102 | `dates=[]` is created once and shared across calls, so loan dates leak between students (output showed "loan dates on record: 1, 2, 3" for three different students). | Default changed to `None`, new list created inside the function; the list is returned so the caller can keep it. |
| 3 | Bare `except` + `pass` | Bug / Security | 21–22 | Bandit B110 (Low), Pylint W0702, Flake8 E722 | Swallows every exception (even `KeyboardInterrupt`) silently, so returning a book that was never borrowed gives no feedback. | Catch only `KeyError` and `ValueError` and print a clear "No loan of … found" message. |
| 4 | Global state mutated by renewal | Bug | 27–30 | Pylint W0603 | `renewBook` used `global FINE_PER_DAY` and permanently raised the fine rate for **every** student after one long renewal (fine for 5 days became 15 instead of 10). | `FINE_PER_DAY` is now a true constant. `renew_book` returns the rate for that loan only, and `calculate_fine` takes an optional `fine_per_day`. |
| 5 | `global loans` rebinding in `load_records` | Design | 35 | Pylint W0603 | Rebinding the module dict via `global` is fragile and hides side effects. | Mutate in place with `loans.clear(); loans.update(data)` — no `global` needed. |
| 6 | Files opened without `with` / encoding | Bug (resource leak) | 34, 40 | Pylint R1732, W1514 | If `json` raised, the file would never be closed; the encoding depended on the OS. | `with open(file, ..., encoding="utf-8")` plus `json.load` / `json.dump`. Missing or corrupt file is handled with a message. |

## Logic bugs found by running the program (not flagged by any tool)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 7 | Negative fines | Logic | 24–25 | `calculate_fine(-3)` returned `-9`, i.e. the library owes the student money. | Clamp with `max(0, days_overdue)`. |
| 8 | Crash on bad input | Robustness | 62–63 | Typing `abc` at the prompt crashed with `ValueError`. | Wrap `int()` in `try/except ValueError`, fall back to 0 with a message. |
| 9 | Non-string book id accepted | Validation | 56 | `4521` (an int) was stored as a book id. | `add_book_loan` rejects non-`str` book ids with a message. |
| 10 | Empty student id ignored silently | Validation | 10–11 | `add_book_loan("", ...)` just returned with no feedback. | Print a message explaining the loan was not recorded. |

## Low severity / style

| # | Issue | Type | Line(s) | Tool / Code | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 11 | Unused import `os` | Style | 2 | Pylint W0611, Flake8 F401 | Removed. |
| 12 | Missing module/function docstrings | Style | 1, all functions | Pylint C0114, C0116 | Added docstrings everywhere. |
| 13 | `renewBook` not snake_case | Style | 27 | Pylint C0103 | Renamed to `renew_book`. |
| 14 | `%` formatting / string concatenation | Style | 14, 31 | Pylint C0209 | Converted to f-strings. |
| 15 | Iterating dict keys then indexing | Style | 49–50 | Pylint C0206 style | `for student, books in loans.items()`. |
| 16 | `main()` runs on import | Style | 68 | — | Wrapped in `if __name__ == "__main__":`. |
| 17 | Missing 2 blank lines | Formatting | 9–52, 68 | Flake8 E302, E305 | Two blank lines around every top-level definition. |
| 18 | Lines too long | Formatting | 14, 31 | Flake8 E501 | Split long f-strings / expressions under 79 chars. |

## Commits

1. `Fix Bandit issues` — safe AST evaluator replacing `eval`; specific exceptions instead of try/except/pass.
2. `Fix Pylint issues` — docstrings, mutable default, no `global`, `with`/encoding, snake_case, f-strings, unused import; plus logic fixes 7–10.
3. `Fix Flake8 issues` — PEP 8 blank lines and line lengths.
