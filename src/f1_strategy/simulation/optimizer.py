from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy


class StrategyOptimizer:

    def __init__(
        self,
        base_lap_time: float,
        race_condition_schedule: RaceConditionSchedule | None = None,
    ):
        self.base_lap_time = base_lap_time
        self.race_condition_schedule = (
            race_condition_schedule
        )

    def _copy_strategy(
        self,
        strategy: RaceStrategy,
    ) -> RaceStrategy:

        copied_stints = []

        for stint in strategy.stints:

            copied_tire = stint.tire.copy()

            copied_stints.append(
                Stint(
                    tire=copied_tire,
                    number_of_laps=stint.number_of_laps,
                    fuel=None,
                    fuel_time_penalty_per_kg=(
                        stint.fuel_time_penalty_per_kg
                    ),
                    race_condition=stint.race_condition,
                )
            )

        copied_pit_stops = [
            PitStop(
                pit_stop.time_seconds()
            )
            for pit_stop in strategy.pit_stops
        ]

        copied_fuel = None

        if strategy.fuel is not None:
            copied_fuel = strategy.fuel.copy()

        return RaceStrategy(
            stints=copied_stints,
            pit_stops=copied_pit_stops,
            fuel=copied_fuel,
        )

    def evaluate(
        self,
        strategies: list[RaceStrategy],
    ) -> list[tuple[RaceStrategy, float]]:

        results = []

        for strategy in strategies:

            strategy_copy = self._copy_strategy(
                strategy
            )

            time = strategy_copy.total_time_seconds(
                self.base_lap_time,
                self.race_condition_schedule,
            )

            results.append(
                (strategy, time)
            )

        return results

    def rank_strategies(
        self,
        strategies: list[RaceStrategy],
    ) -> list[tuple[RaceStrategy, float]]:

        results = self.evaluate(strategies)

        return sorted(
            results,
            key=lambda result: result[1],
        )

    def find_fastest(
        self,
        strategies: list[RaceStrategy],
    ) -> tuple[RaceStrategy, float]:

        if not strategies:
            raise ValueError(
                "At least one strategy is required"
            )

        results = self.evaluate(strategies)

        return min(
            results,
            key=lambda result: result[1],
        )
