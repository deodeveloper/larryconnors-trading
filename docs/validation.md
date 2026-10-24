# Validation record

Executed on 2026-10-23, CPython 3.12.14 / macOS arm64.

- 35 deterministic tests passed; full output in test-results.txt.
- 107 named-variant/execution-mode smoke runs completed, including experimental
  specifications with explicit opt-in and synthetic auxiliary inputs. This is
  code coverage, not strategy efficacy or external-data validation.
- Synthetic CLI example, multi-variant CLI, source-close and next-open execution,
  and local notebook research cells ran successfully.
- Both notebooks passed nbformat validation. Local notebook execution used Python
  execution of research cells, not a hosted Jupyter kernel; HTML display was checked
  as an artifact. Hosted Google Colab and Colab Secrets were not directly tested.
- `pip check` found no broken dependencies. Wheel and source distributions built.
- Linux x86_64 / CPython3.12 wheel resolution completed under constraints.txt with
  manylinux_2_28 and manylinux2014 platform tags. pip's cross-platform resolution
  still evaluates some host environment markers, so this is not a full Linux or
  Colab runtime test. Installed local package imports and execution were tested.
- Browser visual preview could not run: the in-app browser policy rejects file:
  URLs. HTML/CSV/JSON structure and chart payloads were checked locally; no claim
  of screenshot-based visual QA is made.
- Authenticated Alpaca API calls were not made. Pagination, cache and timestamp
  handling were checked with mocked endpoint responses. No credentials were read
  or placed in project files. Auxiliary VIX/TRIN and real-market performance remain
  unverified. All sample performance is synthetic.

The tests exercise strict thresholds, Wilder/ConnorsRSI hand examples, rank ties,
cumulative sums, bands, historical volatility, extrema window inclusion,
consecutive-day patterns, calendar/session coverage, early closes, limit touch,
gap improvement, order expiry, next-open shifting, actual-fill comparisons,
TPS sequencing/trend restrictions, capital/cost constraints, complete exits,
short P&L, borrow accrual, independent cash and episode aggregation.

Selected vectorbt results reconcile to transparent cash/share arithmetic in
`tests/test_execution.py`: sum of signed fill cash flows plus fees, with all scale-ins
aggregated into one flat-to-flat trade. Tests also change a future bar and assert
prior orders remain unchanged.

Known upstream deprecation warnings concern pandas-ta-classic's dayofyear use and
exchange-calendar/pandas timezone conversion; they do not cause test failures.
