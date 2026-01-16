name: Security Audit

on:
  schedule:
    - cron: "0 21 * * *"   # 毎日21時（日本時間6時）
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Run security audit
        run: pip-audit
