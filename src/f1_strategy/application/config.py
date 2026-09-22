from dataclasses import dataclass


@dataclass(frozen=True)
class RaceStrategyApplicationConfig:
    """Configuration for the integrated F1 strategy application."""

    number_of_laps: int = 50
    base_lap_time: float = 90.0

    test_size: float = 0.2
    random_state: int = 42

    n_estimators: int = 100
    learning_rate: float = 0.05
    max_depth: int = 3

    pit_stop_time_seconds: float = 20.0

    def __post_init__(self) -> None:
        """Validate application configuration."""

        if self.number_of_laps <= 1:
            raise ValueError(
                "number_of_laps must be greater than one"
            )

        if self.base_lap_time <= 0.0:
            raise ValueError(
                "base_lap_time must be greater than zero"
            )

        if not 0.0 < self.test_size < 1.0:
            raise ValueError(
                "test_size must be between zero and one"
            )

        if self.n_estimators <= 0:
            raise ValueError(
                "n_estimators must be greater than zero"
            )

        if self.learning_rate <= 0.0:
            raise ValueError(
                "learning_rate must be greater than zero"
            )

        if self.max_depth <= 0:
            raise ValueError(
                "max_depth must be greater than zero"
            )

        if self.pit_stop_time_seconds < 0.0:
            raise ValueError(
                "pit_stop_time_seconds must not be negative"
            )