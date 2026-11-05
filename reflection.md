# Reflection — Lab 5: Static Code Analysis

**Name:** Balla Santhosh  **SRN:** PES1UG24AM063

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 formatting issues (missing blank lines, long lines), the unused `os` import, missing docstrings and the `renewBook` → `renew_book` rename. They are mechanical, the tool gives the exact line, and the fix cannot change behaviour.

The hardest was the `eval()` call in `fine_from_rule` (Bandit B307). Bandit suggests `ast.literal_eval`, but that only accepts literals and cannot evaluate a rule like `days * 2 + 10`. I had to write a small evaluator that parses the rule with `ast` and allows only numbers, the variable `days`, and `+ - * /`. The global `FINE_PER_DAY` was also tricky: Pylint only said "using the global statement", but the real problem was a logic bug — one long renewal permanently raised the fine for every student — and fixing it meant changing how the fine rate flows between `renew_book` and `calculate_fine`.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Not strict false positives, but some findings needed judgement. Bandit rated try/except/pass (B110) only **Low** severity, yet in this program it hid a real problem (returning a book never borrowed gave no feedback). Pylint's `global-statement` warning on `load_records` is a style concern rather than a bug — the code worked — but removing it made the side effect clearer. The opposite problem was more important: the tools **missed** real bugs. None of them flagged negative fines (`calculate_fine(-3)` returning `-9`), the crash on non-numeric input, or an integer book id being accepted. I found those only by running the program, which shows static analysis complements testing rather than replacing it.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor on save, and use a `pre-commit` hook so Flake8, Pylint and Bandit run before every commit.
- **CI:** add a GitHub Actions job that runs all three on every push and pull request, and fails the build if Bandit reports any Medium/High issue, Flake8 reports any violation, or the Pylint score drops below a threshold (e.g. 9.5).
- **Configuration:** keep shared settings in `pyproject.toml` / `.flake8` / `.pylintrc` so the whole team uses the same rules, and use `# nosec` or `# pylint: disable=` only with a comment explaining why.
- Pair this with unit tests, since the logic bugs here were invisible to the tools.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Scores:** Pylint 6.07 → 10.00; Bandit 2 issues → 0; Flake8 14 violations → 0.
- **Security:** arbitrary code can no longer be executed through a fine rule.
- **Correctness:** loan dates no longer leak between students (mutable default fixed); a renewal no longer changes the fine rate for everyone; fines are never negative.
- **Robustness:** invalid input, missing/corrupt `loans.json`, and invalid ids now produce clear messages instead of crashes or silent failures; files are always closed.
- **Readability:** docstrings on every function, consistent snake_case names, f-strings and PEP 8 layout make the code much easier to read and review, and `main()` no longer runs when the module is imported.
