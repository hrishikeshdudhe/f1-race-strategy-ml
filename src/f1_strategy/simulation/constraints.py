from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import TireCompound


class StrategyConstraints:

    def __init__(
        self,
        minimum_stint_laps: int = 1,
        maximum_stint_laps: int | None = None,
        minimum_pit_stops: int = 0,
        maximum_pit_stops: int | None = None,
        required_compounds: set[TireCompound] | None = None,
    ):
        if minimum_stint_laps <= 0:
            raise ValueError(
                "Minimum stint laps must be positive"
            )

        if (
            maximum_stint_laps is not None
            and maximum_stint_laps <= 0
        ):
            raise ValueError(
                "Maximum stint laps must be positive"
            )

        if (
            maximum_stint_laps is not None
            and minimum_stint_laps > maximum_stint_laps
        ):
            raise ValueError(
                "Minimum stint laps cannot exceed maximum stint laps"
            )

        if minimum_pit_stops < 0:
            raise ValueError(
                "Minimum pit stops cannot be negative"
            )

        if (
            maximum_pit_stops is not None
            and maximum_pit_stops < 0
        ):
            raise ValueError(
                "Maximum pit stops cannot be negative"
            )

        if (
            maximum_pit_stops is not None
            and minimum_pit_stops > maximum_pit_stops
        ):
            raise ValueError(
                "Minimum pit stops cannot exceed maximum pit stops"
            )

        if required_compounds is not None:
            if not required_compounds:
                raise ValueError(
                    "Required compounds cannot be empty"
                )

            if not all(
                isinstance(compound, TireCompound)
                for compound in required_compounds
            ):
                raise ValueError(
                    "Required compounds must contain TireCompound values"
                )

        self.minimum_stint_laps = minimum_stint_laps
        self.maximum_stint_laps = maximum_stint_laps
        self.minimum_pit_stops = minimum_pit_stops
        self.maximum_pit_stops = maximum_pit_stops
        self.required_compounds = required_compounds

    def is_stint_length_valid(
        self,
        number_of_laps: int,
    ) -> bool:
        if number_of_laps < self.minimum_stint_laps:
            return False

        if (
            self.maximum_stint_laps is not None
            and number_of_laps > self.maximum_stint_laps
        ):
            return False

        return True

    def is_pit_stop_count_valid(
        self,
        number_of_pit_stops: int,
    ) -> bool:
        if number_of_pit_stops < self.minimum_pit_stops:
            return False

        if (
            self.maximum_pit_stops is not None
            and number_of_pit_stops > self.maximum_pit_stops
        ):
            return False

        return True

    def are_compounds_valid(
        self,
        stints: list[Stint],
    ) -> bool:
        if self.required_compounds is None:
            return True

        used_compounds = {
            stint.tire.compound
            for stint in stints
        }

        return self.required_compounds.issubset(
            used_compounds
        )

    def is_valid(
        self,
        strategy: RaceStrategy,
    ) -> bool:
        for stint in strategy.stints:
            if not self.is_stint_length_valid(
                stint.number_of_laps
            ):
                return False

        if not self.is_pit_stop_count_valid(
            len(strategy.pit_stops)
        ):
            return False

        if not self.are_compounds_valid(
            strategy.stints
        ):
            return False

        return True