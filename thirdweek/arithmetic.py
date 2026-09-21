"""Core arithmetic-expression generation, parsing, and grading logic."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import random
import re
from typing import Iterator, Sequence


DISPLAY_OPERATOR = {"+": "+", "-": "−", "*": "×", "/": "÷"}
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


def format_fraction(value: Fraction) -> str:
    """Format a non-negative fraction as an integer, fraction, or mixed number."""
    if value < 0:
        raise ValueError("only non-negative values can be formatted")
    whole, remainder = divmod(value.numerator, value.denominator)
    if remainder == 0:
        return str(whole)
    if whole == 0:
        return f"{remainder}/{value.denominator}"
    return f"{whole}’{remainder}/{value.denominator}"


@dataclass(frozen=True)
class Expression:
    """An immutable expression tree whose value is always exact."""

    value: Fraction
    operator: str | None = None
    left: "Expression | None" = None
    right: "Expression | None" = None

    @classmethod
    def number(cls, value: Fraction | int) -> "Expression":
        return cls(Fraction(value))

    @classmethod
    def binary(
        cls, operator: str, left: "Expression", right: "Expression"
    ) -> "Expression":
        if operator == "+":
            value = left.value + right.value
        elif operator == "-":
            if left.value < right.value:
                raise ValueError("subtraction would produce a negative value")
            value = left.value - right.value
        elif operator == "*":
            value = left.value * right.value
        elif operator == "/":
            if right.value == 0:
                raise ZeroDivisionError("division by zero")
            value = left.value / right.value
            if not 0 < value < 1:
                raise ValueError("division result must be a proper fraction")
        else:
            raise ValueError(f"unsupported operator: {operator}")
        return cls(value, operator, left, right)

    @property
    def operator_count(self) -> int:
        if self.operator is None:
            return 0
        assert self.left is not None and self.right is not None
        return 1 + self.left.operator_count + self.right.operator_count

    def canonical_key(self) -> tuple:
        """Return a key invariant only under child swaps at + and * nodes."""
        if self.operator is None:
            return ("number", self.value.numerator, self.value.denominator)
        assert self.left is not None and self.right is not None
        left_key = self.left.canonical_key()
        right_key = self.right.canonical_key()
        if self.operator in {"+", "*"} and right_key < left_key:
            left_key, right_key = right_key, left_key
        return (self.operator, left_key, right_key)

    def render(self) -> str:
        return self._render(parent_precedence=0, is_right_child=False)

    def _render(self, parent_precedence: int, is_right_child: bool) -> str:
        if self.operator is None:
            return format_fraction(self.value)
        assert self.left is not None and self.right is not None
        precedence = PRECEDENCE[self.operator]
        left_text = self.left._render(precedence, False)
        right_text = self.right._render(precedence, True)
        text = f"{left_text} {DISPLAY_OPERATOR[self.operator]} {right_text}"
        # Equal-precedence right children need parentheses to retain the tree's
        # left-associative structure. This is also significant for deduplication.
        if precedence < parent_precedence or (
            precedence == parent_precedence and is_right_child
        ):
            return f"({text})"
        return text


class ExerciseGenerator:
    """Generate valid, pairwise non-equivalent arithmetic expressions."""

    def __init__(self, number_range: int, rng: random.Random | None = None):
        if number_range < 1:
            raise ValueError("range must be a positive integer")
        self.number_range = number_range
        self.rng = rng or random.Random()

    def _number(self) -> Expression:
        # Natural numbers are always available. For r > 2, also produce proper
        # and mixed fractions whose value and denominator are both below r.
        if self.number_range <= 2 or self.rng.random() < 0.45:
            return Expression.number(self.rng.randrange(self.number_range))
        denominator = self.rng.randrange(2, self.number_range)
        numerator = self.rng.randrange(1, self.number_range * denominator)
        return Expression.number(Fraction(numerator, denominator))

    def _expression(self, operator_count: int) -> Expression:
        if operator_count == 0:
            return self._number()

        left_count = self.rng.randrange(operator_count)
        right_count = operator_count - 1 - left_count
        left = self._expression(left_count)
        right = self._expression(right_count)
        operator = self.rng.choice(("+", "-", "*", "/"))

        if operator == "-" and left.value < right.value:
            left, right = right, left
        elif operator == "/":
            if left.value == 0 or right.value == 0 or left.value == right.value:
                raise ValueError("cannot form a proper-fraction division")
            if left.value > right.value:
                left, right = right, left
        return Expression.binary(operator, left, right)

    def generate(self, count: int) -> list[Expression]:
        if count < 1:
            raise ValueError("exercise count must be a positive integer")
        exercises: list[Expression] = []
        seen: set[tuple] = set()
        attempts = 0
        max_attempts = max(20_000, count * 400)

        while len(exercises) < count and attempts < max_attempts:
            attempts += 1
            try:
                expression = self._expression(self.rng.randint(1, 3))
            except (ValueError, ZeroDivisionError):
                continue
            key = expression.canonical_key()
            if key not in seen:
                seen.add(key)
                exercises.append(expression)

        if len(exercises) != count:
            raise RuntimeError(
                f"在范围 {self.number_range} 内只能生成 {len(exercises)} 道不重复题目；"
                "请增大 -r 或减小 -n"
            )
        return exercises


TOKEN_RE = re.compile(
    r"\s*(?:(?P<number>\d+(?:[\'’]\d+/\d+|/\d+)?)|"
    r"(?P<operator>[+\-−*×/÷()]))"
)


def _tokens(text: str) -> Iterator[str]:
    position = 0
    while position < len(text):
        match = TOKEN_RE.match(text, position)
        if not match:
            if text[position:].strip() == "":
                break
            raise ValueError(f"无法识别表达式位置 {position + 1} 附近的内容")
        yield match.group("number") or match.group("operator")
        position = match.end()


def parse_number(text: str) -> Fraction:
    normalized = text.replace("'", "’")
    if "’" in normalized:
        whole_text, fraction_text = normalized.split("’", 1)
        numerator_text, denominator_text = fraction_text.split("/", 1)
        denominator = int(denominator_text)
        if denominator == 0:
            raise ValueError("分母不能为 0")
        return Fraction(int(whole_text) * denominator + int(numerator_text), denominator)
    if "/" in normalized:
        numerator_text, denominator_text = normalized.split("/", 1)
        denominator = int(denominator_text)
        if denominator == 0:
            raise ValueError("分母不能为 0")
        return Fraction(int(numerator_text), denominator)
    return Fraction(int(normalized))


class ExpressionParser:
    def __init__(self, text: str):
        aliases = {"−": "-", "×": "*", "÷": "/"}
        self.tokens = [aliases.get(token, token) for token in _tokens(text)]
        self.index = 0

    def parse(self) -> Fraction:
        value = self._sum()
        if self.index != len(self.tokens):
            raise ValueError(f"多余的符号: {self.tokens[self.index]}")
        return value

    def _sum(self) -> Fraction:
        value = self._product()
        while self._peek() in {"+", "-"}:
            operator = self._take()
            right = self._product()
            value = value + right if operator == "+" else value - right
        return value

    def _product(self) -> Fraction:
        value = self._atom()
        while self._peek() in {"*", "/"}:
            operator = self._take()
            right = self._atom()
            if operator == "*":
                value *= right
            else:
                if right == 0:
                    raise ValueError("除数不能为 0")
                value /= right
        return value

    def _atom(self) -> Fraction:
        token = self._take()
        if token == "(":
            value = self._sum()
            if self._take() != ")":
                raise ValueError("缺少右括号")
            return value
        if token in {"+", "-", "*", "/", ")"}:
            raise ValueError(f"此处应为数字，实际为 {token}")
        return parse_number(token)

    def _peek(self) -> str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def _take(self) -> str:
        token = self._peek()
        if token is None:
            raise ValueError("表达式意外结束")
        self.index += 1
        return token


def evaluate_expression(text: str) -> Fraction:
    return ExpressionParser(text.strip()).parse()


NUMBERED_LINE_RE = re.compile(r"^\s*(\d+)\.\s*(.*?)\s*$")


def parse_numbered_lines(lines: Sequence[str]) -> dict[int, str]:
    result: dict[int, str] = {}
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        match = NUMBERED_LINE_RE.match(line)
        if not match:
            raise ValueError(f"第 {line_number} 行格式错误，应为“编号. 内容”")
        index = int(match.group(1))
        if index in result:
            raise ValueError(f"编号 {index} 重复")
        result[index] = match.group(2)
    return result


def grade(exercise_lines: Sequence[str], answer_lines: Sequence[str]) -> tuple[list[int], list[int]]:
    exercises = parse_numbered_lines(exercise_lines)
    answers = parse_numbered_lines(answer_lines)
    correct: list[int] = []
    wrong: list[int] = []

    for index, exercise in exercises.items():
        expression_text = exercise.rsplit("=", 1)[0].strip()
        try:
            expected = evaluate_expression(expression_text)
            actual = parse_number(answers[index].strip())
        except (KeyError, ValueError, ZeroDivisionError):
            wrong.append(index)
        else:
            (correct if actual == expected else wrong).append(index)
    return correct, wrong


def format_grade_line(label: str, indexes: Sequence[int]) -> str:
    joined = ", ".join(str(index) for index in indexes)
    return f"{label}: {len(indexes)} ({joined})"
