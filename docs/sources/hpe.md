# HPE

Source: https://docs.google.com/document/d/161M2Z5ze16FslfrpoesJEQpSwBll5RS8KBR9I3dAop8/edit
Modified: 2026-10-22T06:40:39.684Z
Retrieved via Google Drive connector, 2026-10-23 (America/Los_Angeles).

﻿HPE
High Probability ETF Trading — Strategy Reference
Source and verified coverage
Source: High Probability ETF Trading: 7 Professional Strategies to Improve Your ETF Trading, Larry Connors and Cesar Alvarez, copyright 2009.
The inspected local copy contains 130 scanned PDF pages. All seven strategy chapters, including TPS, are present with entry and exit rules; none is a table-of-contents-only entry. The earlier 20-page description does not apply to this copy.
File inspected: /Users/bijaydeo/Downloads/HPE.pdf. The earlier /mnt/data/HPE.pdf upload was unavailable in this desktop session, so byte-for-byte identity with that upload was not established. Printed page numbers and PDF page numbers differ.
How to read the rules
The rules below preserve the source’s numerical conditions while paraphrasing its prose. SMA(5) and SMA(200) are 5-day and 200-day simple moving averages. RSI(2) and RSI(4) mean 2-period and 4-period RSI. Signals and executions use the daily close. “Above” and “below” are strict comparisons, not inclusive thresholds. A second unit means one additional unit while the position is open.
1. HPE 3-Day High/Low Method
Rule locations: printed pages 10 and 16; PDF pages 16 and 22.
Long entry: Close above SMA(200) and below SMA(5). For three consecutive days ending today, both the daily high and daily low must be below the preceding day’s corresponding high and low. Buy at today’s close.
Aggressive long addition: Buy a second unit on a subsequent close below the initial entry price. Long exit: Price closes above SMA(5).
Short entry: Close below SMA(200) and above SMA(5). For three consecutive days ending today, both the high and low must exceed the preceding day’s corresponding high and low. Short at today’s close.
Aggressive short addition: Short a second unit on a subsequent close above the initial entry price. Short exit: Price closes below SMA(5).
Implementation detail: Three consecutive high/low comparisons require four trading days of data.
2. HPE RSI 25 & RSI 75
Rule locations: printed pages 24 and 30; PDF pages 29 and 35.
Long entry: Close above SMA(200) and RSI(4) closes below 25. Buy on the close. Aggressive addition: Buy a second unit when RSI(4) closes below 20 while holding the position. Exit when RSI(4) closes above 55.
Short entry: Close below SMA(200) and RSI(4) closes above 75. Short on the close. Aggressive addition: Short a second unit when RSI(4) closes above 80 while holding the position. Exit when RSI(4) closes below 45.
The numbers 25 and 75 are RSI thresholds, not lookback periods.
3. HPE R3 Strategy
Rule locations: printed pages 37–38 and 43; PDF pages 42–43 and 48.
Long entry: Close above SMA(200); RSI(2) declines three consecutive days; the book describes the first day’s decline as being “from below 60”; today’s RSI(2) closes below 10. Buy on the close.
Aggressive long addition: Buy a second unit on a subsequent close below the initial entry price. Long exit: RSI(2) closes above 70.
Short entry: Close below SMA(200); RSI(2) rises three consecutive days; the book describes the first day’s rise as being “from above 40”; today’s RSI(2) closes above 90. Short on the close.
Aggressive short addition: Short a second unit on a subsequent close above the initial entry price. Short exit: RSI(2) closes below 30.
Source ambiguity: The numbered rules use “from below/above,” while the examples describe the first declining day’s RSI reading below 60 and the first rising day’s RSI reading above 40. Preserve this distinction when translating the strategy into code rather than silently requiring the prior day’s RSI to satisfy the threshold.
4. HPE %b Strategy
Rule locations: printed pages 50 and 55; PDF pages 55 and 60. Indicator settings: printed page 111; PDF page 115.
Use Bollinger Bands with length 5 and standard deviation multiplier 1. Formula: %b = (Close − Lower Band) / (Upper Band − Lower Band).
Long entry: Close above SMA(200), with %b closing below 0.20 for three consecutive days. Buy on the third close. Aggressive addition: Add a second unit on a later day when %b again closes below 0.20. Exit when %b closes above 0.80.
Short entry: Close below SMA(200), with %b closing above 0.80 for three consecutive days. Short on the third close. Aggressive addition: Short another unit on a later day when %b again closes above 0.80. Exit when %b closes below 0.20.
The addition depends on %b, not a worse entry price. The long example adds even though price rises that day. The chapter presents an aggressive version with a second unit; it does not specify an unlimited series of additions.
5. HPE Multiple Days Down / Multiple Days Up
Rule locations: printed pages 62 and 68; PDF pages 67 and 73. Correct abbreviations: MDD and MDU (not MPU).
MDD long entry: Close above SMA(200), below SMA(5), and lower than the preceding day’s close on at least four of the past five trading days. Buy on the close.
Aggressive long addition: Buy a second unit on a subsequent close below the initial entry price. Long exit: Price closes above SMA(5).
MDU short entry: Close below SMA(200), above SMA(5), and higher than the preceding day’s close on at least four of the past five trading days. Short on the close, as confirmed by the examples.
Aggressive short addition: Short a second unit on a subsequent close above the initial entry price. Short exit: Price closes below SMA(5).
Mentioned variation: Four or five declining days out of six, separate from the primary four-of-five specification.
6. HPE RSI 10/6 & RSI 90/94 Strategy
Rule locations: printed pages 76 and 81; PDF pages 81 and 86.
Long entry: Close above SMA(200) and RSI(2) below 10. Buy on the close. Add a second unit when RSI(2) closes below 6. Exit when price closes above SMA(5).
Short entry: Close below SMA(200) and RSI(2) above 90. Short on the close. Add a second unit when RSI(2) closes above 94. Exit when price closes below SMA(5).
The second unit is part of the stated strategy, rather than separately labeled an aggressive version. The exit uses price versus SMA(5), not an RSI threshold. Mentioned long threshold variants include 10/7, 9/4, and 5/2, with analogous short-side variations.
7. HPE TPS — Time, Price, Scale-in
Rule locations: printed pages 89–90 and 95; PDF pages 94–95 and 100. The chapter supplies the basic 1-2-3-4 version, not the complete TPS research.
Long rules
Initial entry: ETF above SMA(200), with RSI(2) below 25 for two consecutive closes. Buy 10% of the intended full position on the second close.
Scale-in: On a later close below the most recent actual entry price, add 20% of the intended full position. On another later qualifying close below the latest entry price, add 30%. On another later qualifying close below the latest entry price, add 40%.
Exit: Sell the entire held position when RSI(2) closes above 70, whether 10%, 30%, 60%, or 100% has been allocated.
Printed footnote: Do not take a new position when the ETF closes below SMA(200); this footnote is attached to the scale-in steps.
Short rules
Initial entry: ETF below SMA(200), with RSI(2) above 75 for two consecutive closes. Short 10% of the intended full position on the second close.
Scale-in: On a later close above the most recent actual entry price, short another 20% of the intended full position. On another later qualifying close above the latest entry price, short another 30%. On another later qualifying close above the latest entry price, short another 40%.
Exit: Cover the entire held position when RSI(2) closes below 30, regardless of how many additions occurred.
Printed footnote: Do not take a new position when the ETF closes above SMA(200); this footnote is attached to the scale-in steps.
TPS implementation details
The allocations are percentages of the planned full position, producing cumulative exposure of 10% → 30% → 60% → 100%. Additions occur sequentially on later qualifying days and need not be consecutive. Compare with the last actual entry price, not the original entry or average cost. Later additions depend on price; the rules do not require a new two-day RSI setup.
The source prints “75%” in the short-entry rule; this is the RSI threshold of 75. Handwritten notes appear beside the printed TPS rules in this scanned copy; the extraction above relies on the printed rules and footnotes.
Other mentions without complete rules
The concluding discussion and promotional course descriptions mention directional arbitrage, directional pairs arbitrage, structural arbitrage, covered calls, credit spreads, ratio spreads, debit spreads, “rolling SPYs,” “RSI 30-70 for ETFs,” and a TPS 2-3-5 allocation variant. The PDF does not provide complete executable entry and exit rules for these mentions.
Chapters 1, 9, and 10 contain the introduction, “Think Deeper,” and “Putting the High Probability ETF Trading Pieces Together.” These chapters are present but do not add an eighth fully specified core system. The glossary and promotional back matter are also present.
Historical test context
The book’s tests run through December 31, 2008 and use a universe of 20 non-leveraged, non-inverse ETFs. The tests are simulated, exclude commissions and slippage, account for dividends and splits, and do not use stop-loss orders. These are descriptions of the source tests, not updated performance results.
Chapter location reference


Chapter / strategy
	Printed start
	PDF start
	Status
	2 · 3-Day High/Low
	9
	15
	Rules present
	3 · RSI 25 / RSI 75
	23
	28
	Rules present
	4 · R3
	37
	42
	Rules present
	5 · %b
	49
	54
	Rules present
	6 · MDU / MDD
	61
	66
	Rules present
	7 · RSI 10/6 / 90/94
	75
	80
	Rules present
	8 · TPS
	87
	92
	Basic rules present
