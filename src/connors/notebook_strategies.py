"""Named callables used by the three book notebooks (no duplicated signal logic)."""

from dataclasses import dataclass
from enum import Enum
from .strategies import resolve


class PositionType(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class BookStrategy:
    name: str
    long_id: str | None = None
    short_id: str | None = None

    def __call__(
        self,
        position_type=PositionType.LONG,
        parameters=None,
        allow_experimental=False,
        variant=None,
    ):
        direction = PositionType(position_type).value
        strategy_id = self.long_id if direction == "long" else self.short_id
        if strategy_id is None:
            raise ValueError(f"{self.name} has no documented {direction} rules")
        spec, params = resolve(variant or strategy_id, parameters, allow_experimental)
        if spec["id"] != strategy_id:
            raise ValueError(f"Variant {variant} does not belong to {strategy_id}")
        return spec, params


high_low_strategy = BookStrategy(
    "3-Day High/Low", "hpe.high_low.long", "hpe.high_low.short"
)
rsi_25_75_strategy = BookStrategy("RSI 25 / RSI 75", "hpe.rsi4.long", "hpe.rsi4.short")
r3_strategy = BookStrategy("R3", "hpe.r3.long", "hpe.r3.short")
percent_b_strategy = BookStrategy(
    "Bollinger %b", "hpe.percent_b.long", "hpe.percent_b.short"
)
multiple_days_strategy = BookStrategy(
    "Multiple Days Down / Up", "hpe.multiple_days.long", "hpe.multiple_days.short"
)
rsi_sma_strategy = BookStrategy(
    "RSI 10/6 / 90/94 with SMA exit", "hpe.rsi2_scale.long", "hpe.rsi2_scale.short"
)
tps_strategy = BookStrategy("TPS", "hpe.tps.long", "hpe.tps.short")
rsi_under_5_strategy = BookStrategy("2-Period RSI Under 5", "short_term.rsi2")
cumulative_rsi_strategy = BookStrategy("Cumulative RSI", "short_term.cumulative")
double_seven_strategy = BookStrategy("Double 7's", "short_term.double7")
vix_rsi_strategy = BookStrategy("VIX RSI", "short_term.vix")
trin_strategy = BookStrategy("TRIN", "short_term.trin")
sp_short_strategy = BookStrategy("S&P Short", short_id="short_term.sp_short")
ten_day_low_strategy = BookStrategy(
    "Ten-Day Closing Low / Five-Day Hold", "short_term.ten_day"
)
overnight_strategy = BookStrategy("Overnight SPY", "short_term.overnight")
powerzones_strategy = BookStrategy("RSI PowerZones", "buy_fear.powerzones")
crash_strategy = BookStrategy("CRASH", short_id="buy_fear.crash")
vol_panics_strategy = BookStrategy("Vol Panics", short_id="buy_fear.vol_panics")
vxx_trend_strategy = BookStrategy("VXX Trend", short_id="buy_fear.vxx_trend")
new_highs_strategy = BookStrategy("Trading New Highs", "buy_fear.new_highs")
terror_gaps_strategy = BookStrategy("Terror Gaps", "buy_fear.terror_gaps")
