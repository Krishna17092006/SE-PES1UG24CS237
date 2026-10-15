# Lab 5 - Issues Found

Pylint score: 4.81 -> 10.00
Bandit: 5 issues -> 0
Flake8: 9 issues -> 0

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| os.system call (B605) | Security - High | 58 | Runs a shell command with the filename added to it, so it can be used for command injection | Removed os.system and used print instead |
| MD5 hash (B324) | Security - High | 47 | MD5 is a weak hash and should not be used | Changed it to sha256 |
| eval used (B307) | Security - Medium | 42 | eval runs whatever string is passed to it, so any code could be run through the promo expression | Changed the function to take a discount percent (0-100) instead of an expression |
| Secret key printed | Security | 71, 80 | The POS secret token is hardcoded and printed in the output. No tool caught this, I saw it when I ran the program | Read it from an environment variable and only print whether it is set |
| Mutable default argument (W0102) | Bug | 15 | order_log=[] is the same list for every call | Changed the default to None and create the list inside the function |
| Bare except with pass (B110, E722) | Bug | 26-27 | Hides all errors and the caller does not know if the order was voided or not | Catch only KeyError and return True/False |
| random used for PIN (B311) | Security - Low | 51 | random is predictable so it is not safe for a PIN | Used the secrets module |
| Kitchen export has settled orders | Bug | 54-57 | The README says active orders go to the kitchen but the code wrote all orders | Only write the orders that are not settled |
| Unused variables and import (W0612, W0611, F841, F401) | Code quality | 6, 31, 41, 63 | math, service_tax, base_bill and t are never used | Removed them |
| Naming, docstrings and style (C0103, C0116, C0121, C0209, E501, W292) | Style | Many | camelCase function names, no docstrings, == None, % formatting, long lines, no newline at end of file | Renamed to snake_case, added docstrings, used is None and f-strings, split long lines |
