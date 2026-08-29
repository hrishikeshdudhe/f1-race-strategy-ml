from enum import Enum


class RaceCondition(Enum):

    GREEN = ("green", 1.00)
    YELLOW = ("yellow", 1.10)
    VSC = ("vsc", 1.20)
    SAFETY_CAR = ("safety_car", 1.30)

    @property
    def label(self) -> str:
        return self.value[0]

    @property
    def lap_time_multiplier(self) -> float:
        return self.value[1]