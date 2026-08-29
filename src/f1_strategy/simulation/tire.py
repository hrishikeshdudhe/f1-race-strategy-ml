from enum import Enum


class TireCompound(Enum):

    SOFT = ("soft", -1.0, 0.08)
    MEDIUM = ("medium", -0.5, 0.05)
    HARD = ("hard", 0.0, 0.03)

    @property
    def label(self) -> str:
        return self.value[0]

    @property
    def pace_offset(self) -> float:
        return self.value[1]

    @property
    def degradation_rate(self) -> float:
        return self.value[2]

    @property
    def lap_time_delta(self) -> float:
        return self.pace_offset


class Tire:

    def __init__(self, compound: TireCompound, age: int = 0):

        if age < 0:
            raise ValueError("Tire age cannot be negative")

        self.compound = compound
        self.age = age

    def age_one_lap(self) -> None:
        self.age += 1

    def performance_delta(self) -> float:
        return (
            self.compound.pace_offset
            + self.age * self.compound.degradation_rate
        )

    def copy(self) -> "Tire":
        return Tire(
            compound=self.compound,
            age=self.age,
        )