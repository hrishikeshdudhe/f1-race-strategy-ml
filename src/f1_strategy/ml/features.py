from f1_strategy.simulation.strategy import RaceStrategy


class StrategyFeatureExtractor:
    """Convert a race strategy into numerical ML features."""

    def extract(
        self,
        strategy: RaceStrategy,
    ) -> dict[str, float]:
        """Extract numerical features from a race strategy."""

        stint_laps = [
            float(stint.number_of_laps)
            for stint in strategy.stints
        ]

        features = {
            "number_of_stints": float(
                len(strategy.stints)
            ),
            "number_of_pit_stops": float(
                len(strategy.pit_stops)
            ),
            "total_laps": float(
                strategy.total_laps()
            ),
            "pit_stop_time_seconds": float(
                sum(
                    pit_stop.time_seconds()
                    for pit_stop in strategy.pit_stops
                )
            ),
            "soft_stints": 0.0,
            "medium_stints": 0.0,
            "hard_stints": 0.0,
            "average_stint_laps": 0.0,
            "shortest_stint_laps": 0.0,
            "longest_stint_laps": 0.0,
            "stint_lap_range": 0.0,
        }

        for stint in strategy.stints:
            compound = stint.tire.compound.label

            if compound == "soft":
                features["soft_stints"] += 1.0

            elif compound == "medium":
                features["medium_stints"] += 1.0

            elif compound == "hard":
                features["hard_stints"] += 1.0

        for index, stint in enumerate(
            strategy.stints,
            start=1,
        ):
            features[
                f"stint_{index}_laps"
            ] = float(
                stint.number_of_laps
            )

        if stint_laps:
            features[
                "average_stint_laps"
            ] = (
                sum(stint_laps)
                / len(stint_laps)
            )

            features[
                "shortest_stint_laps"
            ] = min(stint_laps)

            features[
                "longest_stint_laps"
            ] = max(stint_laps)

            features[
                "stint_lap_range"
            ] = (
                max(stint_laps)
                - min(stint_laps)
            )

        return features