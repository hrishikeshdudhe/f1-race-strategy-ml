from itertools import product

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

    def generate_two_stint_strategies(
        self,
    ) -> list[RaceStrategy]:

        strategies = []

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
                    stints=[first_stint, second_stint],
                    pit_stops=[pit_stop],
                    fuel=fuel,
                )

                strategies.append(strategy)

        return strategies