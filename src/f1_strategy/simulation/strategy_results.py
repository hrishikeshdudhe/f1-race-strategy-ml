import csv

from f1_strategy.simulation.strategy_result import StrategyResult


class StrategyResults:

    def __init__(
        self,
        results: list[StrategyResult],
    ):
        self.results = results

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, index: int) -> StrategyResult:
        return self.results[index]

    def best(self) -> StrategyResult:
        if not self.results:
            raise ValueError(
                "At least one strategy result is required"
            )

        return min(
            self.results,
            key=lambda result: result.total_time_seconds,
        )

    def top_n(
        self,
        number: int,
    ) -> list[StrategyResult]:
        if number < 0:
            raise ValueError(
                "Number of results cannot be negative"
            )

        return self.results[:number]

    def count(self) -> int:
        return len(self.results)

    def fastest_time_seconds(self) -> float:
        return self.best().total_time_seconds

    def report(
        self,
        number: int | None = None,
    ) -> str:
        if not self.results:
            return "No strategy results."

        if number is None:
            selected_results = self.results
        else:
            selected_results = self.top_n(number)

        lines = [
            "F1 Strategy Report",
            "==================",
            "",
            f"Strategies evaluated: {len(self.results)}",
            (
                f"Fastest race time: "
                f"{self.fastest_time_seconds():.2f} s"
            ),
            "",
            (
                "Rank | Race Time | Gap | Gap % | "
                "Tires | Stints | Pit Stops"
            ),
            (
                "-----|------------|-----|-------|"
                "-------|--------|----------"
            ),
        ]

        for result in selected_results:
            rank = (
                str(result.rank)
                if result.rank is not None
                else "-"
            )

            tires = " -> ".join(
                compound.upper()
                for compound in result.tire_compounds
            )

            lines.append(
                f"{rank:>4} | "
                f"{result.total_time_seconds:>10.2f} | "
                f"+{result.time_delta_seconds:>4.2f} | "
                f"+{result.time_gap_percentage:>5.3f}% | "
                f"{tires:<15} | "
                f"{result.number_of_stints:^6} | "
                f"{result.number_of_pit_stops:^9}"
            )

        return "\n".join(lines)

    def export_csv(
        self,
        file_path: str,
    ) -> None:
        fieldnames = [
            "rank",
            "total_time_seconds",
            "time_delta_seconds",
            "time_gap_percentage",
            "time_gap_to_next_seconds",
            "average_lap_time_seconds",
            "total_laps",
            "number_of_stints",
            "number_of_pit_stops",
            "pit_stop_time_seconds",
            "tire_strategy",
            "stint_laps",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for result in self.results:
                writer.writerow(
                    {
                        "rank": result.rank,
                        "total_time_seconds": (
                            result.total_time_seconds
                        ),
                        "time_delta_seconds": (
                            result.time_delta_seconds
                        ),
                        "time_gap_percentage": (
                            result.time_gap_percentage
                        ),
                        "time_gap_to_next_seconds": (
                            result.time_gap_to_next_seconds
                        ),
                        "average_lap_time_seconds": (
                            result.average_lap_time_seconds
                        ),
                        "total_laps": result.total_laps,
                        "number_of_stints": (
                            result.number_of_stints
                        ),
                        "number_of_pit_stops": (
                            result.number_of_pit_stops
                        ),
                        "pit_stop_time_seconds": (
                            result.pit_stop_time_seconds
                        ),
                        "tire_strategy": (
                            result.tire_strategy
                        ),
                        "stint_laps": ",".join(
                            str(laps)
                            for laps in result.stint_laps
                        ),
                    }
                )