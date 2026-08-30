from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.stint import Stint


def create_strategy(
    first_compound: TireCompound,
    second_compound: TireCompound,
) -> RaceStrategy:
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(first_compound),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(second_compound),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )


def test_rank_strategies_assigns_first_rank_to_fastest():
    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        [
            strategy_a,
            strategy_b,
        ]
    )

    assert results[0].rank == 1
    assert results[1].rank == 2


def test_rank_strategies_assigns_sequential_ranks():
    strategies = [
        create_strategy(
            TireCompound.SOFT,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.MEDIUM,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.HARD,
            TireCompound.SOFT,
        ),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert [result.rank for result in results] == [
        1,
        2,
        3,
    ]


def test_strategy_result_without_ranking_has_no_rank():
    strategy = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    result = optimizer.evaluate_detailed(
        [strategy]
    )[0]

    assert result.rank is None


def test_rank_strategies_returns_fastest_first():
    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        [
            strategy_a,
            strategy_b,
        ]
    )

    assert results[0].strategy is strategy_b
    assert results[1].strategy is strategy_a