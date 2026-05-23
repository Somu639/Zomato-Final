from zm.cli import cmd_check, cmd_demo_models


def test_cmd_check_runs():
    assert cmd_check() == 0


def test_cmd_demo_models_runs(capsys):
    assert cmd_demo_models() == 0
    captured = capsys.readouterr()
    assert "Bangalore" in captured.out
    assert "family-friendly" in captured.out
