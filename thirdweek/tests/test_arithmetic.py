from fractions import Fraction
import random

import pytest

from arithmetic import (
    ExerciseGenerator,
    Expression,
    evaluate_expression,
    format_fraction,
    format_grade_line,
    grade,
    parse_number,
)


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (Fraction(0), "0"),
        (Fraction(3), "3"),
        (Fraction(3, 5), "3/5"),
        (Fraction(19, 8), "2’3/8"),
    ],
)
def test_format_fraction(value, text):
    assert format_fraction(value) == text
    assert parse_number(text) == value


def test_parser_honors_precedence_parentheses_and_ascii_aliases():
    assert evaluate_expression("1 + 2 * 3") == 7
    assert evaluate_expression("(1 + 2) × 3") == 9
    assert evaluate_expression("2’1/2 ÷ 5") == Fraction(1, 2)


def test_subtraction_rejects_negative_intermediate_result():
    with pytest.raises(ValueError):
        Expression.binary("-", Expression.number(1), Expression.number(2))


def test_division_requires_a_proper_fraction_result():
    with pytest.raises(ValueError):
        Expression.binary("/", Expression.number(2), Expression.number(1))
    assert Expression.binary("/", Expression.number(1), Expression.number(2)).value == Fraction(1, 2)


def test_commutative_swaps_have_the_same_canonical_key():
    one, two = Expression.number(1), Expression.number(2)
    assert Expression.binary("+", one, two).canonical_key() == Expression.binary("+", two, one).canonical_key()
    assert Expression.binary("*", one, two).canonical_key() == Expression.binary("*", two, one).canonical_key()


def test_required_association_deduplication_example():
    one, two, three = (Expression.number(i) for i in range(1, 4))
    first = Expression.binary("+", Expression.binary("+", one, two), three)
    equivalent = Expression.binary("+", three, Expression.binary("+", two, one))
    different = Expression.binary("+", Expression.binary("+", three, two), one)
    assert first.canonical_key() == equivalent.canonical_key()
    assert first.canonical_key() != different.canonical_key()


def test_render_preserves_right_nested_expression_tree():
    one, two, three = (Expression.number(i) for i in range(1, 4))
    expression = Expression.binary("+", one, Expression.binary("+", two, three))
    assert expression.render() == "1 + (2 + 3)"


def test_generator_constraints_and_uniqueness():
    expressions = ExerciseGenerator(10, random.Random(7)).generate(500)
    assert len({item.canonical_key() for item in expressions}) == 500
    assert all(1 <= item.operator_count <= 3 for item in expressions)
    assert all(evaluate_expression(item.render()) == item.value for item in expressions)
    for expression in expressions:
        _assert_valid_intermediate_results(expression)


def _assert_valid_intermediate_results(expression):
    if expression.operator is None:
        return
    assert expression.left is not None and expression.right is not None
    if expression.operator == "-":
        assert expression.left.value >= expression.right.value
    if expression.operator == "/":
        assert 0 < expression.value < 1
    _assert_valid_intermediate_results(expression.left)
    _assert_valid_intermediate_results(expression.right)


def test_generated_leaf_values_and_denominators_are_below_range():
    generator = ExerciseGenerator(10, random.Random(11))
    for _ in range(1000):
        number = generator._number()
        assert 0 <= number.value < 10
        assert number.value.denominator < 10


def test_grade_marks_correct_wrong_missing_and_malformed_answers():
    exercises = ["1. 1/6 + 1/8 =", "2. 3 × 4 =", "3. 5 − 2 =", "4. 1 + 1 ="]
    answers = ["1. 7/24", "2. 11", "3. abc"]
    correct, wrong = grade(exercises, answers)
    assert correct == [1]
    assert wrong == [2, 3, 4]
    assert format_grade_line("Wrong", wrong) == "Wrong: 3 (2, 3, 4)"


def test_zero_denominator_and_invalid_expression_are_rejected():
    with pytest.raises(ValueError):
        parse_number("1/0")
    with pytest.raises(ValueError):
        evaluate_expression("1 + hello")
