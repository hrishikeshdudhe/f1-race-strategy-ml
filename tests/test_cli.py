import sys

from f1_strategy.application.cli import main


def test_cli_runs_with_custom_configuration(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "f1-strategy",
            "--laps",
            "30",
            "--base-lap-time",
            "92",
            "--pit-stop-time",
            "25",
        ],
    )

    main()

    output = capsys.readouterr().out

    assert "Laps: 30" in output
    assert "Base lap time: 92.0 s" in output
    assert "Pit stop time: 25.0 s" in output
    assert "ML-selected strategy" in output
    assert "Actual fastest candidate" in output
    assert "Selection performance" in output


def test_cli_runs_with_default_configuration(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["f1-strategy"],
    )

    main()

    output = capsys.readouterr().out

    assert "Laps: 50" in output
    assert "Base lap time: 90.0 s" in output
    assert "Pit stop time: 20.0 s" in output
    assert "Strategy: SOFT -> SOFT" in output
    assert "Gap to fastest candidate: 0.000 s" in output