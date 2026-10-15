# Patch

#### Fixed

- **`watch pr` retries when its `gh api graphql` poll takes longer than 30 seconds.** It used to exit 1 with a `TimeoutExpired` traceback, ending the wait.
