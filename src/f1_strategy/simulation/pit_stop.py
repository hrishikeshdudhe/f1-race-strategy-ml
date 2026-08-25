class PitStop:

    def __init__(self, duration_seconds: float):
        if duration_seconds <= 0:
            raise ValueError("Pit stop duration must be positive")

        self.duration_seconds = duration_seconds

    def time_seconds(self) -> float:
        return self.duration_seconds