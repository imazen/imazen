# Python 3.11+ is required (tomllib); uv supplies it where the system Python is older.
py := "uv run --no-project --python 3.12"

# Fetch the inventory and registry facts, then rebuild README.md and llms.txt.
refresh:
    GITHUB_TOKEN=$(gh auth token) {{py}} tools/build.py --refresh

# Rebuild from the cached data/ files.
build:
    {{py}} tools/build.py

# Also write dist/llms-full.txt with every listed README inlined.
full:
    {{py}} tools/build.py --full

# Fail if crates.io has a crate owned by lilith that the catalog neither lists nor leaves out (needs `just refresh` first).
check:
    {{py}} tools/check_crates.py
