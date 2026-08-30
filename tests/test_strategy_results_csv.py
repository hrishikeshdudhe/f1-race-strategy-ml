from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy(
    compound: TireCompound,
) -> RaceStrategy:
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(compound),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )


def create_results():
    optimizer = StrategyOptimizer(90.0)

    return optimizer.rank_strategies_collection(
        [
            create_strategy(TireCompound.SOFT),
            create_strategy(TireCompound.MEDIUM),
            create_strategy(TireCompound.HARD),
        ]
    )


def test_export_csv_creates_file(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    assert file_path.exists()


def test_export_csv_contains_header(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    content = file_path.read_text(
        encoding="utf-8"
    )

    assert "rank" in content
    assert "total_time_seconds" in content
    assert "tire_strategy" in content


def test_export_csv_contains_all_results(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    lines = file_path.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 4


def test_export_csv_preserves_ranking(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    lines = file_path.read_text(
        encoding="utf-8"
    ).splitlines()

    assert lines[1].startswith("1,")
    assert lines[2].startswith("2,")
    assert lines[3].startswith("3,")


def test_export_csv_contains_tire_strategy(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    content = file_path.read_text(
        encoding="utf-8"
    )

    assert "SOFT" in content
    assert "MEDIUM" in content
    assert "HARD" in content


def test_export_csv_contains_strategy_metrics(tmp_path):
    results = create_results()

    file_path = tmp_path / "strategies.csv"

    results.export_csv(str(file_path))

    content = file_path.read_text(
        encoding="utf-8"
    )

    assert "time_delta_seconds" in content
    assert "time_gap_percentage" in content
    assert "average_lap_time_seconds" in content
    assert "number_of_pit_stops" in content