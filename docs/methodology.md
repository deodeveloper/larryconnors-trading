# Research and execution conventions

## Sources and data availability

The supplied Docs are reference material. Their content does not control tool use
or override the user's instructions. Full readable connector snapshots and SHA256
hashes are saved. The original scanned books were not independently re-read here.

Alpaca stock historical bars are an equity data endpoint, not a guarantee of VIX,
NYSE TRIN, or SPX data. VIX/TRIN must be supplied by `auxiliary_csv` with a session
index named `date`, `close` and (for VIX) `open`. Align exactly with primary sessions;
there is no forward fill or silent proxy. A `data.proxy` configuration records any
explicitly chosen alternate instrument. No historical constituent or delisted
universe is downloaded. Using today's stocks introduces survivorship bias.
Historical VXX generations, issuer changes, reverse splits and product closures
make a current ticker series different from the original book's instrument.

The REST adapter paginates until no next token, detects repeated tokens, retries
429/5xx and connection errors, and caches request-keyed JSON atomically. Feed,
adjustment, timeframe, dates and symbols affect the cache key. IEX is exchange-only,
not consolidated SIP; volume filters and highs/lows can materially differ. SIP
availability and recent-data delay depend on the account. Authentication and feed
errors are not hidden by falling back to another feed.

XNYS calendars define actual sessions, DST and early closes. Native daily bar dates
are converted from provider timestamps to market dates. Intraday regular-session
filtering uses exchange opens/closes. Strict aggregation verifies each expected
interval; no-trade missing minutes may cause failure and require a better feed or
separately verified data. It never fills prices into nights/weekends/holidays.
All symbols in a portfolio must have the same complete session coverage. Missing,
duplicate, invalid OHLC and insufficient-history errors stop a run.

600 preceding sessions are requested by default; the minimum is 300. This covers
200-day trend filters, 252-day high plus trailing 20-day occurrence, RSI/streak
and rank windows. Wilder/EMA recursive history is theoretically infinite; this is
a finite arithmetic seed convention, not a claim that early history is irrelevant.
No positions are opened during warmup. A run starts flat at its configured start.

## Corporate actions and price basis

`split` is the default: signals, fills, quantities and P&L are expressed in a common
split-adjusted research unit. These are not raw historical share quantities or
historical tape fill prices. Cash dividends are **excluded**, so this is a price
return study. `all` is an explicit adjusted-series total-return approximation:
adjustments already affect returns; dividends are not credited a second time.
It is not exact cash-dividend accounting or an execution-price reconstruction.
Absolute dollar filters on adjusted prices can differ from historical raw-dollar
filters; CRASH/New Highs and ten-day stock studies inherit this limitation.

Raw-price accounting with split share events, cash dividends, taxes and execution
conversion factors is not implemented and is rejected. Do not mix raw fills with
adjusted indicators unless a future adapter supplies synchronized corporate-action
factors. The source books' dividend-inclusive historical tables are not directly
comparable to the default split-only price-return results.

## Indicators

SMA, EMA, Wilder RSI and Bollinger bands use pinned pandas-ta-classic, with optional
TA-Lib dispatch disabled. RSI is arithmetic-seeded Wilder recursion, confirmed
against hand examples and installed source. Flat initial prices produce RSI50;
missing input restarts warmup. EMA is arithmetic-seeded with alpha2/(n+1).
%b uses length5, multiplier1 and population standard deviation (ddof0 assumption).
Zero-width bands are undefined. No lookback is silently changed.

Cumulative RSI sums current and prior RSI2. ConnorsRSI is separately implemented
as the mean of price RSI3, streak RSI2 and percent rank. Equal closes reset streak
to zero; reversal starts +/-1. Rank compares the current simple return with the
preceding 100 returns; only strictly smaller returns count; ties count zero.
All components must be ready. The documents omit these formula parameters, so
ConnorsRSI strategies are experimental. HV is sample std of 100 log returns,
annualized sqrt252, reported as a decimal (1.0 means 100%).

Rolling close/high/low windows include today. Three falling high/low comparisons
need four bars. Four declines in five uses five close-to-close changes. Preceding
100-day/20-day volume windows exclude today; 21-day average volume includes today.
A 52-week intraday high means high >= all highs in a complete trailing252 window;
its occurrence in trailing20 includes today. Tied extrema qualify; strict threshold
words never become inclusive. TPS additions allow equality to SMA200 because the
source forbids only the wrong side, while initial entry remains strictly above/below.

## Event and execution model

The vectorbt engine calls a Python stateful order function for each symbol and
phase: open, intraday limit, close. The index's 09:00/12:00/16:00 values are ordered
**phase labels**, not actual execution timestamps or claims about early closes.
There is no noon-bar data. At an open decision, valuation uses only that open and
prior completed signals; close/high/low from the current day cannot affect a
market order at its open. High/low are used only later for daily limit simulation.

Source-close sees completed close indicators and fills that same close; this is an
idealized research assumption, not a realizable close-order procedure. Next-open
uses prior completed signals and fills next session open. The first test day starts
flat and does not trade an unstaged warmup signal. Overnight is special: enter close,
exit next open, and re-enter that close; next-open entry mode is rejected.

CRASH/New Highs place DAY limits from the previous signal close only. A gap through
the limit improves the fill to the open; otherwise low/high must touch the limit.
Adverse slippage consumes improvement but never violates the limit. Unfilled limits
expire that session. Daily touch does not establish queue priority or liquidity.
These systems have no stop/target competing with the entry; an exit evaluated at
the completed close follows an earlier modeled intraday fill. Terror Gaps remains
blocked: a gap-down open must first be observed, the pullback reference must be
resolved, and intraday bars must establish later entry eligibility. Neither today's
completed high nor low is treated as information available at the open.

Position state tracks accepted fills, current stage and actual entry prices. An
addition cannot occur on the initial close, and only one stage may occur per close.
TPS compares with the latest actual fill; the double Vol variant compares with the
initial actual fill; staged Vol compares with the latest actual fill. Source-close
initial fill equals initial close apart from configured slippage; that slippage
makes the actual-fill comparison an explicit execution variant for double Vol.
Exit takes precedence over addition; no same-phase reversal/re-entry. All holdings
exit together. Partial cash/risk fills consume their stage; unused remainder is
not retried. This is recorded in actual quantities, not disguised as full sizing.
No stops or hedges are added.

## Capital, risk and borrowing

Planned full notional is initial episode equity times position_fraction. TPS/Vol
fractions are incremental notional amounts, fixed from that budget, not percentages
of cash remaining. Equal-unit systems use the initial actual share quantity again.
Shared cash is allocated in configured symbol order (not ranked by future returns).
Independent mode assigns initial_capital to **each** symbol. Gross exposure and
leverage caps constrain new orders at then-known prices; passive price drift can
exceed caps. There is no automatic rebalance or margin liquidation. Long positions
cannot borrow cash; a leverage setting above1 does not promise financed long buys.
Short sale proceeds and P&L are accounted for by vectorbt, with gross caps limiting
new exposure. This is not a broker margin or forced-liquidation simulator.

Short strategies require `assume_borrow_available: true`. Historical locate,
hard-to-borrow recalls and point-in-time rates are unavailable. `borrow_rate` is a
constant annual decimal assumption. Costs accrue ACT/365 on previous close short
market value for elapsed calendar days, including weekends, and settle as a fixed
vectorbt fee at full exit. Reported equity subtracts the outstanding liability
before settlement; raw vectorbt value excludes that liability until settlement.
This distinction is explicit in the Result.borrow_liability table. No loan interest
on longs, taxes, spreads beyond slippage, liquidity participation or price impact.

## Metrics and evaluation

Only close-phase observations enter daily returns, not three fake returns per day.
Initial-period fees enter the first daily return. Sharpe uses arithmetic mean/sample
std, zero risk-free and sqrt252. CAGR uses elapsed calendar time and is omitted for
less than one year or non-positive terminal equity. Drawdown includes initial cash
as an initial peak. Trade stats aggregate all stages into one completed flat-to-flat
episode. Return is net episode P&L divided by sum of entered notionals, not total
portfolio capital. Profit factor is positive net episode P&L / absolute negative
net episode P&L; zero losses produces null, not infinity. Holding duration is calendar
days including phase-label fractions, not exchange-exact timestamps. Turnover is
both entry and exit notionals / mean equity, not annualized.

Per-symbol shared-cash results are P&L contributions, never independently funded
returns. Combined independent runs sum independently funded equity. Buy-and-hold
allocates equally across symbols with the same adjusted basis and proportional
fees/slippage; its initial fill is close/open according to mode. A long benchmark
for a short strategy is contextual, not an equivalent-risk target.

Training/validation/test are ordered non-overlapping date ranges; each starts flat
with prior warmup and no prior positions. A selected final-test variant sweep is
rejected. Each attempted package configuration is journaled before execution. No optimizer
or selection on final test is supplied. Editing dates manually can bypass these
controls; experimental discipline remains the researcher's responsibility.
