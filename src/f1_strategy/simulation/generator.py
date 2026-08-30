from itertools import product

from f1_strategy.simulation.constraints import StrategyConstraints
from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound


class StrategyGenerator:

    def __init__(
        self,
        number_of_laps: int,
        initial_fuel_mass_kg: float | None = None,
        fuel_consumption_per_lap_kg: float = 2.0,
        constraints: StrategyConstraints | None = None,
    ):
        if number_of_laps <= 1:
            raise ValueError(
                "Number of laps must be greater than one"
            )

        if initial_fuel_mass_kg is not None:
            if initial_fuel_mass_kg <= 0:
                raise ValueError(
                    "Initial fuel mass must be positive"
                )

            if fuel_consumption_per_lap_kg <= 0:
                raise ValueError(
                    "Fuel consumption per lap must be positive"
                )

            if fuel_consumption_per_lap_kg > initial_fuel_mass_kg:
                raise ValueError(
                    "Fuel consumption cannot exceed initial fuel mass"
                )

        self.number_of_laps = number_of_laps
        self.initial_fuel_mass_kg = initial_fuel_mass_kg
        self.fuel_consumption_per_lap_kg = (
            fuel_consumption_per_lap_kg
        )
        self.constraints = constraints

    def _compound_pair_is_valid(
        self,
        first_compound: TireCompound,
        second_compound: TireCompound,
    ) -> bool:
        if self.constraints is None:
            return True

        return self.constraints.are_compounds_valid(
            [
                Stint(
                    tire=Tire(first_compound),
                    number_of_laps=1,
                ),
                Stint(
                    tire=Tire(second_compound),
                    number_of_laps=1,
                ),
            ]
        )

    def _stint_lengths_are_valid(
        self,
        first_stint_laps: int,
        second_stint_laps: int,
    ) -> bool:
        if self.constraints is None:
            return True

        return (
            self.constraints.is_stint_length_valid(
                first_stint_laps
            )
            and self.constraints.is_stint_length_valid(
                second_stint_laps
            )
        )

    def _pit_stop_count_is_valid(
        self,
        number_of_pit_stops: int,
    ) -> bool:
        if self.constraints is None:
            return True

        return self.constraints.is_pit_stop_count_valid(
            number_of_pit_stops
        )

    def generate_two_stint_strategies(
        self,
    ) -> list[RaceStrategy]:

        strategies = []

        number_of_pit_stops = 1

        if not self._pit_stop_count_is_valid(
            number_of_pit_stops
        ):
            return strategies

        for first_compound, second_compound in product(
            TireCompound,
            repeat=2,
        ):
            for first_stint_laps in range(
                1,
                self.number_of_laps,
            ):
                second_stint_laps = (
                    self.number_of_laps
                    - first_stint_laps
                )

                if not self._stint_lengths_are_valid(
                    first_stint_laps,
                    second_stint_laps,
                ):
                    continue

                first_tire = Tire(first_compound)
                second_tire = Tire(second_compound)

                first_stint = Stint(
                    tire=first_tire,
                    number_of_laps=first_stint_laps,
                )

                second_stint = Stint(
                    tire=second_tire,
                    number_of_laps=second_stint_laps,
                )

                pit_stop = PitStop(20.0)

                fuel = None

                if self.initial_fuel_mass_kg is not None:
                    fuel = Fuel(
                        initial_mass_kg=self.initial_fuel_mass_kg,
                        consumption_per_lap_kg=(
                            self.fuel_consumption_per_lap_kg
                        ),
                    )

                strategy = RaceStrategy(
                    stints=[
                        first_stint,
                        second_stint,
                    ],
                    pit_stops=[
                        pit_stop,
                    ],
                    fuel=fuel,
                )

                if (
                    self.constraints is not None
                    and not self.constraints.is_valid(
                        strategy
                    )
                ):
                    continue

                strategies.append(strategy)

        return strategies