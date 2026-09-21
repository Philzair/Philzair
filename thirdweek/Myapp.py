#!/usr/bin/env python3
"""Command-line entry point for arithmetic exercise generation and grading."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from arithmetic import ExerciseGenerator, format_fraction, format_grade_line, grade


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("必须是正整数") from error
    if value < 1:
        raise argparse.ArgumentTypeError("必须是正整数")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Myapp",
        description="生成小学四则运算题目，或批改已有答案。",
    )
    parser.add_argument("-n", type=positive_int, default=10, metavar="数量", help="生成题目数量（默认 10）")
    parser.add_argument("-r", type=positive_int, metavar="范围", help="题目中数值及分母的上限（不包含）")
    parser.add_argument("-e", type=Path, metavar="题目文件", help="待批改的题目文件")
    parser.add_argument("-a", type=Path, metavar="答案文件", help="待批改的答案文件")
    return parser


def generate_files(count: int, number_range: int) -> None:
    expressions = ExerciseGenerator(number_range).generate(count)
    exercise_lines = [f"{i}. {expression.render()} =" for i, expression in enumerate(expressions, 1)]
    answer_lines = [f"{i}. {format_fraction(expression.value)}" for i, expression in enumerate(expressions, 1)]
    Path("Exercises.txt").write_text("\n".join(exercise_lines) + "\n", encoding="utf-8")
    Path("Answers.txt").write_text("\n".join(answer_lines) + "\n", encoding="utf-8")


def grade_files(exercise_path: Path, answer_path: Path) -> None:
    exercises = exercise_path.read_text(encoding="utf-8-sig").splitlines()
    answers = answer_path.read_text(encoding="utf-8-sig").splitlines()
    correct, wrong = grade(exercises, answers)
    content = f"{format_grade_line('Correct', correct)}\n{format_grade_line('Wrong', wrong)}\n"
    Path("Grade.txt").write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    grading = args.e is not None or args.a is not None

    if grading and (args.e is None or args.a is None):
        parser.error("批改模式必须同时给出 -e 和 -a")
    if grading and args.r is not None:
        parser.error("批改模式不能同时使用 -r")
    if not grading and args.r is None:
        parser.error("生成模式必须给出 -r 参数")

    try:
        if grading:
            grade_files(args.e, args.a)
        else:
            generate_files(args.n, args.r)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"错误: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
