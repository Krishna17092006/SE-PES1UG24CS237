# Lab 5 Reflection

1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest ones were the Flake8 and Pylint style issues like unused imports, long lines, naming and missing docstrings, because the tools give the exact line and what is wrong. The hardest was removing eval from the discount function. I could not just delete it, I had to change the function to take a discount percent instead of an expression. The bare except was also a bit tricky because I had to decide what the function should return when the table does not exist.

2. Did the static analysis tools report any false positives? If so, describe one example.

Pylint said base_bill was an unused variable, but it was actually used inside the string passed to eval. Pylint cannot read inside strings so it did not see it. Also Bandit did not catch the hardcoded secret key, because the variable name did not have words like password or token in it. I only noticed it when I ran the program and saw it printed.

3. How would you integrate static analysis tools into your actual software development workflow?

I would use them in VS Code while coding and add them as a pre-commit hook so code with security issues cannot be committed. They can also be added to GitHub Actions so they run on every push. One thing I noticed is that Pylint allows 100 characters per line and Flake8 allows only 79, so the line length should be set the same in a config file.

4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

The Pylint score went from 4.81 to 10, and Bandit and Flake8 show no issues now. The code is safer because there is no eval, os.system or MD5 anymore and the secret is not printed. It is also easier to read with proper names and docstrings, and an invalid discount now gives an error instead of running whatever is passed in.
