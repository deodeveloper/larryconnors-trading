# Short Term Trading Strategies That Work — Clear Entry and Exit Rules

Source: https://docs.google.com/document/d/1aIOvM_YQpMVRlTOkTYumFFm5qzOdUQizo5ubrBOvaws/edit
Modified: 2026-10-24T02:45:44.737Z
Retrieved via Google Drive connector, 2026-10-23 (America/Los_Angeles).

﻿Short Term Trading Strategies That Work
Strategies with clear entry and exit signals
Larry Connors & Cesar Alvarez • Source edition: copyright 2009
Scope and notation
This reference contains six strategy families with specified entry and exit signals, followed by two explicitly defined trading tests. General trading principles, incomplete stock-specific specifications, and conflicting formulas are omitted from the rule sections. Rules are paraphrased without changing their numerical thresholds.
Source: Short Term Trading Strategies That Work: A Quantified Guide to Trading Stocks and ETFs. The inspected PDF has 174 pages, with all 15 table-of-contents chapters present. Printed and PDF page numbers differ.
RSI(2) = 2-period Relative Strength Index. SMA(5) and SMA(200) = 5-day and 200-day simple moving averages. An up close means today’s close is higher than the preceding trading day’s close. Closing highs and lows refer to closing prices, not intraday highs or lows. Preserve strict “above” and “below” comparisons. Where the source explicitly requires execution on the close, that timing is stated below.
1. The 2-Period RSI Under 5 on the S&P 500
Direction: Long. Source: Chapter 9, printed page 62 / PDF page 82.
Entry
1. The S&P 500 is above its 200-day moving average.
2. The S&P 500 RSI(2) closes below 5.
3. Buy the S&P on that close.
Exit
Exit when the S&P closes above its 5-period moving average.
The chapter discusses SPY and E-mini applications. No scale-in condition is specified in these rules.
2. Cumulative RSI — Two-Day Variants
Direction: Long. Source: Chapter 9, printed pages 66–70 / PDF pages 86–90.
Entry
1. The security is above its 200-day moving average.
2. Calculate RSI(2) for each day.
3. Add today’s RSI(2) and the preceding trading day’s RSI(2).
4. Buy when this two-day sum is below the selected threshold: 35 for the first SPY example, or 50 for the looser SPY variation.
Exit
Exit when RSI(2) closes above 65.
These are two parameter variants of one strategy family. Choose one threshold before applying the rules. The entry uses the sum of two daily RSI(2) readings, not a two-period RSI recalculated over another timeframe. The numbered source rules specify the buy condition but do not separately state the entry order’s execution time; no fill convention is added here. The source permits alternative exits, but this reference retains its stated RSI(2) > 65 exit.
3. Double 7’s Strategy
Direction: Long. Source: Chapter 10, printed page 76 / PDF page 96.
Entry
1. SPY is above its 200-day moving average.
2. SPY closes at a 7-day closing low.
3. Buy on that closing signal.
Exit
Sell the long position when SPY closes at a 7-day closing high.
The chapter also demonstrates QQQQ, FXI, and EWZ. The 7-day low/high conditions concern closing prices. No scale-in rule is supplied.
4. VIX RSI Strategy
Direction: Long the market. Source: Chapter 12, printed page 96 / PDF page 116.
Entry
1. SPY is above its 200-period moving average.
2. The RSI(2) of VIX is greater than 90.
3. Today’s VIX open is greater than yesterday’s VIX close.
4. The RSI(2) of SPY is below 30.
5. When all conditions hold, buy on the close.
Exit
Exit when SPY RSI(2) closes above 65.
Use separate RSI calculations for VIX and SPY. The source does not label the VIX RSI condition as yesterday’s RSI. The chapter allows SPX as a simpler market-signal alternative.
5. TRIN Strategy
Direction: Long the market. Source: Chapter 12, printed page 100 / PDF page 120.
Entry
1. SPY is above its 200-day moving average.
2. The market’s RSI(2) is below 50.
3. TRIN closes above 1.00 for three consecutive days.
4. When all three conditions hold, buy on the close.
Exit
Exit on the close when SPY RSI(2) is above 65.
TRIN is the Arms Index based on NYSE advancing and declining issues and volume. The three consecutive readings must each be above 1.00.
6. S&P Short Strategy
Direction: Short. Source: Chapter 12, printed pages 106–107 / PDF pages 126–127.
Entry
1. SPY or SPX is below its 200-day moving average.
2. The market closes higher than the preceding trading day for four or more consecutive days.
3. Sell short on the close.
Exit
Cover the short position when SPY closes below its 5-period moving average.
There is no RSI entry condition or scale-in condition in this rule set.
Additional trading tests with explicit entry and exit
The following two items are included because their trade entry and exit are clearly stated. The book presents them as tests, rather than separately named flagship systems.
7. Ten-Day Closing Low — Five-Day Hold
Direction: Long stocks. Source: Chapter 8, printed page 46 / PDF page 66.
1. The stock closes at a 10-day closing low.
2. The stock is above its 200-day simple moving average.
3. Average daily volume over the preceding 100 trading days is at least 250,000 shares.
4. The stock price is greater than $5.
5. Buy on the close.
Exit: Sell on the close five trading days later.
This is the baseline pullback test. Next-day limit-entry variants are omitted here because the source does not fully specify their fill and holding-period conventions.
8. Overnight SPY Holding Test
Direction: Long SPY. Source: Chapter 7, printed page 37 / PDF page 55.
Entry: Buy SPY on the close each trading day.
Exit: Sell on the next trading day’s open.
The test does not add a moving-average, RSI, or other signal filter. The chapter separately compares buying at the open and selling at the same day’s close; that daytime comparison is not included as a selected strategy.
Source notes
Excluded for incomplete or inconsistent rules: the Chapter 12 Cumulative RSI variation below 45 (two days of RSI(3) in the numbered rule versus three days of RSI(2) in the surrounding explanation); the stock-specific Cumulative RSI subsection (sum length and volume averaging window not restated); the VIX Stretches system (inconsistent “above 65” versus “65 or more” exit wording); and the End of the Month study (no single mandatory entry date). General VIX guidance, standalone RSI screens, psychology, and exit-only methods are not presented as complete systems here.
The rules above do not add stop-loss orders, profit targets, scale-ins, portfolio sizing, transaction costs, or intraday execution logic that the selected source passages do not specify. Most reported research ends in 2007; this is a source reference, not updated performance evidence.
