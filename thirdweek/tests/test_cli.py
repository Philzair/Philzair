from pathlib import Path
import os
import subprocess
import sys


PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT / "Myapp.py"


def run_app(tmp_path, *arguments):
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(APP), *map(str, arguments)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )


def test_cli_requires_range_in_generation_mode(tmp_path):
    result = run_app(tmp_path, "-n", 2)
    assert result.returncode == 2
    assert "-r" in result.stderr


def test_cli_generates_exercises_and_answers(tmp_path):
    result = run_app(tmp_path, "-n", 20, "-r", 10)
    assert result.returncode == 0
    exercises = (tmp_path / "Exercises.txt").read_text(encoding="utf-8").splitlines()
    answers = (tmp_path / "Answers.txt").read_text(encoding="utf-8").splitlines()
    assert len(exercises) == len(answers) == 20
    assert exercises[0].startswith("1. ") and exercises[0].endswith(" =")


def test_cli_grades_files(tmp_path):
    exercise_file = tmp_path / "questions.txt"
    answer_file = tmp_path / "answers.txt"
    exercise_file.write_text("1. 1 + 2 =\n2. 1/2 + 1/3 =\n", encoding="utf-8")
    answer_file.write_text("1. 3\n2. 1/2\n", encoding="utf-8")
    result = run_app(tmp_path, "-e", exercise_file, "-a", answer_file)
    assert result.returncode == 0
    assert (tmp_path / "Grade.txt").read_text(encoding="utf-8") == (
        "Correct: 1 (1)\nWrong: 1 (2)\n"
    )


def test_cli_rejects_incomplete_grading_arguments(tmp_path):
    result = run_app(tmp_path, "-e", "questions.txt")
    assert result.returncode == 2
    assert "-e" in result.stderr and "-a" in result.stderr
