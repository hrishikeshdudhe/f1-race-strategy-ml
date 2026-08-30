from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.strategy_results import StrategyResults


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

    def _evaluate_strategy(
        self,
        strategy: RaceStrategy,
    ) -> StrategyResult:
        strategy_copy = self._copy_strategy(
            strategy
        )

        time = strategy_copy.total_time_seconds(
            self.base_lap_time,
            self.race_condition_schedule,
        )

        return StrategyResult(
            strategy=strategy,
            total_time_seconds=time,
            race_condition_schedule=(
                self.race_condition_schedule
            ),
            base_lap_time=self.base_lap_time,
        )

    def evaluate(
        self,
        strategies: list[RaceStrategy],
    ) -> list[tuple[RaceStrategy, float]]:
        results = []

        for strategy in strategies:
            result = self._evaluate_strategy(
                strategy
            )

            results.append(
                (
                    strategy,
                    result.total_time_seconds,
                )
            )

        return results

    def evaluate_detailed(
        self,
        strategies: list[RaceStrategy],
    ) -> list[StrategyResult]:
        return [
            self._evaluate_strategy(strategy)
            for strategy in strategies
        ]

    def rank_strategies(
        self,
        strategies: list[RaceStrategy],
    ) -> list[StrategyResult]:
        results = self.evaluate_detailed(
            strategies
        )

        ranked_results = sorted(
            results,
            key=lambda result: result.total_time_seconds,
        )

        if not ranked_results:
            return []

        fastest_time = (
            ranked_results[0].total_time_seconds
        )

        for rank, result in enumerate(
            ranked_results,
            start=1,
        ):
            result.rank = rank

            result.time_delta_seconds = (
                result.total_time_seconds
                - fastest_time
            )

        for index, result in enumerate(
            ranked_results
        ):
            if index < len(ranked_results) - 1:
                next_result = ranked_results[
                    index + 1
                ]

                result.time_gap_to_next_seconds = (
                    next_result.total_time_seconds
                    - result.total_time_seconds
                )
            else:
                result.time_gap_to_next_seconds = 0.0

        return ranked_results

    def rank_strategies_collection(
        self,
        strategies: list[RaceStrategy],
    ) -> StrategyResults:
        ranked_results = self.rank_strategies(
            strategies
        )

        return StrategyResults(
            ranked_results
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