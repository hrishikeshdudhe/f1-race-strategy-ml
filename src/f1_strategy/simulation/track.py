class Track:
    def __init__(
        self,
        name: str,
        length_km: float,
        number_of_laps: int,
        average_speed_kmh: float,
    ):
        if length_km <= 0:
            raise ValueError("Track length must be greater than zero.")

        if number_of_laps <= 0:
            raise ValueError("Number of laps must be greater than zero.")

        if average_speed_kmh <= 0:
            raise ValueError("Average speed must be greater than zero.")

        self.name = name
        self.length_km = length_km
        self.number_of_laps = number_of_laps
        self.average_speed_kmh = average_speed_kmh

    def lap_time_seconds(self) -> float:
        return (self.length_km / self.average_speed_kmh) * 3600