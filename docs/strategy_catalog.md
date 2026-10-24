# Source-linked strategy catalog

Full readable snapshots: docs/sources. Machine catalog: strategy_catalog.json. All strict thresholds, source variants and implementation assumptions remain explicit.

## hpe.high_low.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE 3-Day High/Low Method

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND close < SMA5 AND 3 consecutive (high < prior high AND low < prior low)

**Exit Rules**: close > SMA5

**Scale In Rules**: aggressive only: one equal unit when close is worse than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.high_low.long", "hpe.high_low.long.aggressive"]

Parameters: `{"aggressive": false}`

## hpe.rsi4.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit) [Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: HPE RSI 25 & RSI 75

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND RSI4 < entry

**Exit Rules**: RSI4 > exit

**Scale In Rules**: aggressive only: one equal unit when RSI4 crosses strict add threshold

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.rsi4.long", "hpe.rsi4.long.aggressive", "powerzones25"]

Parameters: `{"aggressive": false, "entry": 25, "add": 20, "exit": 55}`

## hpe.r3.long — experimental

R3 first reading vs preceding reading unresolved; explicitly selected interpretation required

[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE R3 Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND 3 consecutive RSI2 changes < 0 AND RSI2[t-offset] < 60 AND RSI2 < 10

**Exit Rules**: RSI2 > 70

**Scale In Rules**: aggressive only: one equal unit at worse close than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.r3.long", "hpe.r3.long.aggressive"]

Parameters: `{"aggressive": false, "r3_interpretation": "first_declining_reading"}`

## hpe.percent_b.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE %b Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND 3 consecutive %b < .20

**Exit Rules**: %b > .80

**Scale In Rules**: aggressive only: one equal unit on later %b < .20 long / > .80 short

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books", "Band standard-deviation divisor not in document; population ddof=0 recorded"]

**Named Variants**: ["hpe.percent_b.long", "hpe.percent_b.long.aggressive"]

Parameters: `{"aggressive": false, "length": 5, "std": 1, "ddof": 0}`

## hpe.multiple_days.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE Multiple Days Down / Multiple Days Up

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND close < SMA5 AND at least count of last window close changes < 0

**Exit Rules**: close > SMA5

**Scale In Rules**: aggressive only: one equal unit at worse close than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.multiple_days.long", "hpe.multiple_days.long.aggressive"]

Parameters: `{"aggressive": false, "window": 5, "count": 4}`

## hpe.rsi2_scale.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE RSI 10/6 & RSI 90/94 Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND RSI2 < entry

**Exit Rules**: close > SMA5

**Scale In Rules**: one equal unit when RSI2 < add

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.rsi2_scale.long", "rsi2_10_7", "rsi2_9_4", "rsi2_5_2"]

Parameters: `{"aggressive": false, "entry": 10, "add": 6}`

## hpe.tps.long — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit) [Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: HPE TPS — Time, Price, Scale-in

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: long

**Entry Rules**: close > SMA200 AND two consecutive RSI2 < 25

**Exit Rules**: RSI2 > 70

**Scale In Rules**: 10/20/30/40% planned notional; later worse close than latest actual fill; forbid wrong side of SMA200

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books", "Buy the Fear volume variant uses average of preceding 20 sessions >=250000; source does not explicitly distinguish average from every-day minimum"]

**Named Variants**: ["hpe.tps.long", "tps_volume_long"]

Parameters: `{"aggressive": false}`

## hpe.high_low.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE 3-Day High/Low Method

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND close > SMA5 AND 3 consecutive (high > prior high AND low > prior low)

**Exit Rules**: close < SMA5

**Scale In Rules**: aggressive only: one equal unit when close is worse than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.high_low.short", "hpe.high_low.short.aggressive"]

Parameters: `{"aggressive": false}`

## hpe.rsi4.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE RSI 25 & RSI 75

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND RSI4 > entry

**Exit Rules**: RSI4 < exit

**Scale In Rules**: aggressive only: one equal unit when RSI4 crosses strict add threshold

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.rsi4.short", "hpe.rsi4.short.aggressive"]

Parameters: `{"aggressive": false, "entry": 75, "add": 80, "exit": 45}`

## hpe.r3.short — experimental

R3 first reading vs preceding reading unresolved; explicitly selected interpretation required

[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE R3 Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND 3 consecutive RSI2 changes > 0 AND RSI2[t-offset] > 40 AND RSI2 > 90

**Exit Rules**: RSI2 < 30

**Scale In Rules**: aggressive only: one equal unit at worse close than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.r3.short", "hpe.r3.short.aggressive"]

Parameters: `{"aggressive": false, "r3_interpretation": "first_declining_reading"}`

## hpe.percent_b.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE %b Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND 3 consecutive %b > .80

**Exit Rules**: %b < .20

**Scale In Rules**: aggressive only: one equal unit on later %b < .20 long / > .80 short

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books", "Band standard-deviation divisor not in document; population ddof=0 recorded"]

**Named Variants**: ["hpe.percent_b.short", "hpe.percent_b.short.aggressive"]

Parameters: `{"aggressive": false, "length": 5, "std": 1, "ddof": 0}`

## hpe.multiple_days.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE Multiple Days Down / Multiple Days Up

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND close > SMA5 AND at least count of last window close changes > 0

**Exit Rules**: close < SMA5

**Scale In Rules**: aggressive only: one equal unit at worse close than initial actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.multiple_days.short", "hpe.multiple_days.short.aggressive"]

Parameters: `{"aggressive": false, "window": 5, "count": 4}`

## hpe.rsi2_scale.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

**Name**: HPE RSI 10/6 & RSI 90/94 Strategy

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND RSI2 > entry

**Exit Rules**: close < SMA5

**Scale In Rules**: one equal unit when RSI2 > add

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["hpe.rsi2_scale.short"]

Parameters: `{"aggressive": false, "entry": 90, "add": 94}`

## hpe.tps.short — ready



[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit) [Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: HPE TPS — Time, Price, Scale-in

**Universe**: Non-leveraged, non-inverse ETFs; original 20 ETF membership not supplied

**Direction**: short

**Entry Rules**: close < SMA200 AND two consecutive RSI2 > 75

**Exit Rules**: RSI2 < 30

**Scale In Rules**: 10/20/30/40% planned notional; later worse close than latest actual fill; forbid wrong side of SMA200

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books", "Buy the Fear volume variant uses average of preceding 20 sessions >=250000; source does not explicitly distinguish average from every-day minimum"]

**Named Variants**: ["hpe.tps.short", "tps_volume_short"]

Parameters: `{"aggressive": false}`

## short_term.rsi2 — ready



[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: The 2-Period RSI Under 5 on the S&P 500

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: close > SMA200 AND RSI2 < 5

**Exit Rules**: close > SMA5

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.rsi2"]

Parameters: `{}`

## short_term.cumulative — experimental

Entry timing unstated; execution mode is explicit research assumption

[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: Cumulative RSI — Two-Day Variants

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: close > SMA200 AND RSI2[t]+RSI2[t-1] < threshold

**Exit Rules**: RSI2 > 65

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.cumulative", "cumulative50"]

Parameters: `{"threshold": 35}`

## short_term.double7 — ready



[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: Double 7’s Strategy

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: close > SMA200 AND close == rolling_min(close,7)

**Exit Rules**: close == rolling_max(close,7)

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.double7"]

Parameters: `{}`

## short_term.vix — ready

Requires supplied auxiliary CSV; no automatic proxy

[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: VIX RSI Strategy

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: SPY close > SMA200 AND VIX RSI2 > 90 AND VIX open > prior VIX close AND SPY RSI2 < 30

**Exit Rules**: SPY RSI2 > 65

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.vix"]

Parameters: `{}`

## short_term.trin — ready

Requires supplied auxiliary CSV; no automatic proxy

[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: TRIN Strategy

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: SPY close > SMA200 AND SPY RSI2 < 50 AND three consecutive TRIN close > 1

**Exit Rules**: SPY RSI2 > 65

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.trin"]

Parameters: `{}`

## short_term.sp_short — ready



[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: S&P Short Strategy

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: short

**Entry Rules**: close < SMA200 AND at least four consecutive positive close changes

**Exit Rules**: close < SMA5

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.sp_short"]

Parameters: `{}`

## short_term.ten_day — ready



[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: Ten-Day Closing Low — Five-Day Hold

**Universe**: Stocks; historical point-in-time universe and delisted membership must be supplied

**Direction**: long

**Entry Rules**: close == rolling_min(close,10) AND close > SMA200 AND mean(volume[t-100:t-1]) >= 250000 AND close > 5

**Exit Rules**: five sessions after entry, close; next-open variant described in methodology

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books", "Source-close exit five sessions after actual entry; next-open variant evaluates five-session hold at close and exits following open"]

**Named Variants**: ["short_term.ten_day"]

Parameters: `{}`

## short_term.overnight — ready



[Source short_term](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

**Name**: Overnight SPY Holding Test

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: every session close

**Exit Rules**: next session open

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: Source-close entry, next session open exit; next_open entry mode intentionally rejected

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["short_term.overnight"]

Parameters: `{}`

## buy_fear.powerzones — ready



[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: RSI PowerZones

**Universe**: SPY / equity ETFs or explicitly documented market application; SPX not assumed tradable

**Direction**: long

**Entry Rules**: close > SMA200 AND RSI4 < entry

**Exit Rules**: RSI4 > 55

**Scale In Rules**: one equal unit on later RSI4 < add

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.powerzones"]

Parameters: `{"entry": 30, "add": 25, "exit": 55}`

## buy_fear.crash — experimental

ConnorsRSI(3,2,100), strict less-than percent rank and HV conventions are explicit assumptions absent in document

[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: CRASH

**Universe**: Stocks; historical point-in-time universe and delisted membership must be supplied

**Direction**: short

**Entry Rules**: close > 5 AND mean(volume,21) >= 1000000 AND HV100 >= hv_min AND ConnorsRSI >= 90; next-day sell limit close*(1+limit_pct)

**Exit Rules**: ConnorsRSI < exit

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.crash", "crash5", "crash_exit20", "crash_hv60", "crash_hv80"]

Parameters: `{"limit_pct": 0.03, "exit": 30, "hv_min": 1.0}`

## buy_fear.vol_panics — ready



[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: Vol Panics

**Universe**: VXX; historical note/product changes disclosed

**Direction**: short

**Entry Rules**: close > SMA5 AND RSI4 > 70

**Exit Rules**: close < SMA5, or named RSI4 < 20 variant

**Scale In Rules**: basic 100%; double 50/50 equal shares above first actual entry; staged 20/30/50 or 10/20/30/40 notional above latest actual entry

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.vol_panics", "vol_double", "vol235", "vol1234", "vol_rsi_exit"]

Parameters: `{"stages": [1.0], "exit_kind": "sma"}`

## buy_fear.vxx_trend — ready



[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: VXX Trend Strategy

**Universe**: VXX; historical note/product changes disclosed

**Direction**: short

**Entry Rules**: MA10 < MA30 AND prior MA10 >= prior MA30

**Exit Rules**: MA10 > MA30 AND prior MA10 <= prior MA30

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.vxx_trend", "vxx_ema"]

Parameters: `{"ma": "sma"}`

## buy_fear.new_highs — experimental

ConnorsRSI(3,2,100), strict less-than percent rank and HV conventions are explicit assumptions absent in document

[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: Trading New Highs

**Universe**: Stocks; historical point-in-time universe and delisted membership must be supplied

**Direction**: long

**Entry Rules**: close > 5 AND mean(volume,21) > 1000000 AND trailing20 contains high==rolling_max(high,252) AND ConnorsRSI < 15; next-day buy limit close*(1-limit_pct)

**Exit Rules**: ConnorsRSI > 70

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.new_highs", "new_highs10"]

Parameters: `{"limit_pct": 0.07}`

## buy_fear.terror_gaps — blocked

Reference price unspecified; daily bars cannot validate post-open sequence. No executable implementation.

[Source buy_fear](https://docs.google.com/document/d/1MzbEHZr38_fwsD82O456i8YsoCz5A87QVm7S5Gl660Y/edit)

**Name**: Terror Gaps

**Universe**: ETFs including leveraged ETFs

**Direction**: long

**Entry Rules**: prior ConnorsRSI < 5; observe gap-down open; further percentage pullback reference unresolved

**Exit Rules**: ConnorsRSI > 70

**Scale In Rules**: none

**Comparisons**: Above/below strict; at high/low inclusive; at least >=. See rules.

**Signal Timing**: completed daily close

**Execution Timing**: source_close idealized or next_open timing variant; next-day limits expire at session end

**Sizing**: User-configured planned full notional fixed at episode entry; source unit systems use equal shares; TPS/Vol staged allocations use incremental notional fractions

**Assumptions**: ["No stops; exit takes precedence over add; at most one stage per close; no same-close re-entry", "SMA/rolling extrema include current bar; preceding volume excludes current bar", "Portfolio sizing and costs are research configuration, not supplied by books"]

**Named Variants**: ["buy_fear.terror_gaps"]

Parameters: `{"pullback": 0.01}`

## blocked.cumulative45_conflict — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

Parameters: `{}`

## blocked.stock_cumulative — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

Parameters: `{}`

## blocked.vix_stretches — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

Parameters: `{}`

## blocked.end_of_month — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit)

Parameters: `{}`

## blocked.hpe_promotional_systems — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

Parameters: `{}`

## blocked.tps235 — blocked

Incomplete/conflicting source; see source notes. No guessed runnable rules.

[Source ](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

Parameters: `{}`

## blocked.multiple_days_4_or_5_of_6 — blocked

Mentioned variation does not settle exactly 4/5 vs at least4 inclusion of six declining days; primary four-of-five remains runnable

[Source hpe](https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit)

Parameters: `{}`

## Named variants

```json
{
  "hpe.high_low.long": {
    "strategy": "hpe.high_low.long",
    "parameters": {
      "aggressive": false
    }
  },
  "hpe.high_low.long.aggressive": {
    "strategy": "hpe.high_low.long",
    "parameters": {
      "aggressive": true
    }
  },
  "hpe.rsi4.long": {
    "strategy": "hpe.rsi4.long",
    "parameters": {
      "aggressive": false,
      "entry": 25,
      "add": 20,
      "exit": 55
    }
  },
  "hpe.rsi4.long.aggressive": {
    "strategy": "hpe.rsi4.long",
    "parameters": {
      "aggressive": true,
      "entry": 25,
      "add": 20,
      "exit": 55
    }
  },
  "hpe.r3.long": {
    "strategy": "hpe.r3.long",
    "parameters": {
      "aggressive": false,
      "r3_interpretation": "first_declining_reading"
    }
  },
  "hpe.r3.long.aggressive": {
    "strategy": "hpe.r3.long",
    "parameters": {
      "aggressive": true,
      "r3_interpretation": "first_declining_reading"
    }
  },
  "hpe.percent_b.long": {
    "strategy": "hpe.percent_b.long",
    "parameters": {
      "aggressive": false,
      "length": 5,
      "std": 1,
      "ddof": 0
    }
  },
  "hpe.percent_b.long.aggressive": {
    "strategy": "hpe.percent_b.long",
    "parameters": {
      "aggressive": true,
      "length": 5,
      "std": 1,
      "ddof": 0
    }
  },
  "hpe.multiple_days.long": {
    "strategy": "hpe.multiple_days.long",
    "parameters": {
      "aggressive": false,
      "window": 5,
      "count": 4
    }
  },
  "hpe.multiple_days.long.aggressive": {
    "strategy": "hpe.multiple_days.long",
    "parameters": {
      "aggressive": true,
      "window": 5,
      "count": 4
    }
  },
  "hpe.rsi2_scale.long": {
    "strategy": "hpe.rsi2_scale.long",
    "parameters": {
      "aggressive": false,
      "entry": 10,
      "add": 6
    }
  },
  "hpe.tps.long": {
    "strategy": "hpe.tps.long",
    "parameters": {
      "aggressive": false
    }
  },
  "hpe.high_low.short": {
    "strategy": "hpe.high_low.short",
    "parameters": {
      "aggressive": false
    }
  },
  "hpe.high_low.short.aggressive": {
    "strategy": "hpe.high_low.short",
    "parameters": {
      "aggressive": true
    }
  },
  "hpe.rsi4.short": {
    "strategy": "hpe.rsi4.short",
    "parameters": {
      "aggressive": false,
      "entry": 75,
      "add": 80,
      "exit": 45
    }
  },
  "hpe.rsi4.short.aggressive": {
    "strategy": "hpe.rsi4.short",
    "parameters": {
      "aggressive": true,
      "entry": 75,
      "add": 80,
      "exit": 45
    }
  },
  "hpe.r3.short": {
    "strategy": "hpe.r3.short",
    "parameters": {
      "aggressive": false,
      "r3_interpretation": "first_declining_reading"
    }
  },
  "hpe.r3.short.aggressive": {
    "strategy": "hpe.r3.short",
    "parameters": {
      "aggressive": true,
      "r3_interpretation": "first_declining_reading"
    }
  },
  "hpe.percent_b.short": {
    "strategy": "hpe.percent_b.short",
    "parameters": {
      "aggressive": false,
      "length": 5,
      "std": 1,
      "ddof": 0
    }
  },
  "hpe.percent_b.short.aggressive": {
    "strategy": "hpe.percent_b.short",
    "parameters": {
      "aggressive": true,
      "length": 5,
      "std": 1,
      "ddof": 0
    }
  },
  "hpe.multiple_days.short": {
    "strategy": "hpe.multiple_days.short",
    "parameters": {
      "aggressive": false,
      "window": 5,
      "count": 4
    }
  },
  "hpe.multiple_days.short.aggressive": {
    "strategy": "hpe.multiple_days.short",
    "parameters": {
      "aggressive": true,
      "window": 5,
      "count": 4
    }
  },
  "hpe.rsi2_scale.short": {
    "strategy": "hpe.rsi2_scale.short",
    "parameters": {
      "aggressive": false,
      "entry": 90,
      "add": 94
    }
  },
  "hpe.tps.short": {
    "strategy": "hpe.tps.short",
    "parameters": {
      "aggressive": false
    }
  },
  "short_term.rsi2": {
    "strategy": "short_term.rsi2",
    "parameters": {}
  },
  "short_term.cumulative": {
    "strategy": "short_term.cumulative",
    "parameters": {
      "threshold": 35
    }
  },
  "short_term.double7": {
    "strategy": "short_term.double7",
    "parameters": {}
  },
  "short_term.vix": {
    "strategy": "short_term.vix",
    "parameters": {}
  },
  "short_term.trin": {
    "strategy": "short_term.trin",
    "parameters": {}
  },
  "short_term.sp_short": {
    "strategy": "short_term.sp_short",
    "parameters": {}
  },
  "short_term.ten_day": {
    "strategy": "short_term.ten_day",
    "parameters": {}
  },
  "short_term.overnight": {
    "strategy": "short_term.overnight",
    "parameters": {}
  },
  "buy_fear.powerzones": {
    "strategy": "buy_fear.powerzones",
    "parameters": {
      "entry": 30,
      "add": 25,
      "exit": 55
    }
  },
  "buy_fear.crash": {
    "strategy": "buy_fear.crash",
    "parameters": {
      "limit_pct": 0.03,
      "exit": 30,
      "hv_min": 1.0
    }
  },
  "buy_fear.vol_panics": {
    "strategy": "buy_fear.vol_panics",
    "parameters": {
      "stages": [
        1.0
      ],
      "exit_kind": "sma"
    }
  },
  "buy_fear.vxx_trend": {
    "strategy": "buy_fear.vxx_trend",
    "parameters": {
      "ma": "sma"
    }
  },
  "buy_fear.new_highs": {
    "strategy": "buy_fear.new_highs",
    "parameters": {
      "limit_pct": 0.07
    }
  },
  "buy_fear.terror_gaps": {
    "strategy": "buy_fear.terror_gaps",
    "parameters": {
      "pullback": 0.01
    }
  },
  "cumulative50": {
    "strategy": "short_term.cumulative",
    "parameters": {
      "threshold": 50
    }
  },
  "powerzones25": {
    "strategy": "hpe.rsi4.long",
    "parameters": {
      "aggressive": true,
      "entry": 25,
      "add": 20,
      "exit": 55
    }
  },
  "tps_volume_long": {
    "strategy": "hpe.tps.long",
    "parameters": {
      "aggressive": false,
      "volume_filter": true
    }
  },
  "tps_volume_short": {
    "strategy": "hpe.tps.short",
    "parameters": {
      "aggressive": false,
      "volume_filter": true
    }
  },
  "vol_double": {
    "strategy": "buy_fear.vol_panics",
    "parameters": {
      "stages": [
        0.5,
        0.5
      ],
      "exit_kind": "sma",
      "equal_units": true
    }
  },
  "vol235": {
    "strategy": "buy_fear.vol_panics",
    "parameters": {
      "stages": [
        0.2,
        0.3,
        0.5
      ],
      "exit_kind": "sma"
    }
  },
  "vol1234": {
    "strategy": "buy_fear.vol_panics",
    "parameters": {
      "stages": [
        0.1,
        0.2,
        0.3,
        0.4
      ],
      "exit_kind": "sma"
    }
  },
  "vol_rsi_exit": {
    "strategy": "buy_fear.vol_panics",
    "parameters": {
      "stages": [
        1.0
      ],
      "exit_kind": "rsi"
    }
  },
  "vxx_ema": {
    "strategy": "buy_fear.vxx_trend",
    "parameters": {
      "ma": "ema"
    }
  },
  "crash5": {
    "strategy": "buy_fear.crash",
    "parameters": {
      "limit_pct": 0.05,
      "exit": 30,
      "hv_min": 1.0
    }
  },
  "crash_exit20": {
    "strategy": "buy_fear.crash",
    "parameters": {
      "limit_pct": 0.03,
      "exit": 20,
      "hv_min": 1.0
    }
  },
  "crash_hv60": {
    "strategy": "buy_fear.crash",
    "parameters": {
      "limit_pct": 0.03,
      "exit": 30,
      "hv_min": 0.6
    }
  },
  "crash_hv80": {
    "strategy": "buy_fear.crash",
    "parameters": {
      "limit_pct": 0.03,
      "exit": 30,
      "hv_min": 0.8
    }
  },
  "new_highs10": {
    "strategy": "buy_fear.new_highs",
    "parameters": {
      "limit_pct": 0.1
    }
  },
  "rsi2_10_7": {
    "strategy": "hpe.rsi2_scale.long",
    "parameters": {
      "entry": 10,
      "add": 7
    }
  },
  "rsi2_9_4": {
    "strategy": "hpe.rsi2_scale.long",
    "parameters": {
      "entry": 9,
      "add": 4
    }
  },
  "rsi2_5_2": {
    "strategy": "hpe.rsi2_scale.long",
    "parameters": {
      "entry": 5,
      "add": 2
    }
  }
}
```
