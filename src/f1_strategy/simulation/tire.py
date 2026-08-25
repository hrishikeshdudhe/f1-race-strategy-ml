from enum import Enum


class TireCompound(Enum):
    SOFT = ("soft", -1.0, 0.08)
    MEDIUM = ("medium", -0.5, 0.05)
    HARD = ("hard", 0.0, 0.03)

    def __init__(
        self,
        label: str,
        pace_offset: float,
        degradation_rate: float,
    ):
        self.label = label
        self.pace_offset = pace_offset
        self.degradation_rate = degradation_rate

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
            + self.compound.degradation_rate * self.age
        )