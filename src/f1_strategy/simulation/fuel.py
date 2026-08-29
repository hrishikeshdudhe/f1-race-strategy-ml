class Fuel:

    def __init__(
        self,
        initial_mass_kg: float,
        consumption_per_lap_kg: float,
    ):

        if initial_mass_kg <= 0:
            raise ValueError(
                "Initial fuel mass must be positive"
            )

        if consumption_per_lap_kg <= 0:
            raise ValueError(
                "Fuel consumption per lap must be positive"
            )

        if consumption_per_lap_kg > initial_mass_kg:
            raise ValueError(
                "Fuel consumption cannot exceed initial fuel mass"
            )

        self.initial_mass_kg = initial_mass_kg
        self.consumption_per_lap_kg = consumption_per_lap_kg
        self.remaining_mass_kg = initial_mass_kg

    def consume_one_lap(self) -> None:

        self.remaining_mass_kg = max(
            0.0,
            self.remaining_mass_kg
            - self.consumption_per_lap_kg,
        )

    def remaining_fuel_kg(self) -> float:

        return self.remaining_mass_kg

    def consumed_fuel_kg(self) -> float:

        return (
            self.initial_mass_kg
            - self.remaining_mass_kg
        )

    def copy(self) -> "Fuel":

        copied_fuel = Fuel(
            initial_mass_kg=self.initial_mass_kg,
            consumption_per_lap_kg=self.consumption_per_lap_kg,
        )

        copied_fuel.remaining_mass_kg = self.remaining_mass_kg

        return copied_fuel