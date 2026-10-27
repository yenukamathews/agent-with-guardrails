
import pytest

from tools import calculator, sql_tool


def test_calculator_addition():
    assert calculator("2 + 3") == 5


def test_calculator_expression():
    assert calculator("12 * (3 + 2)") == 60


def test_calculator_blocks_python_code():
    with pytest.raises(ValueError):
        calculator("__import__('os').system('whoami')")


def test_calculator_division_by_zero():
    with pytest.raises(ValueError):
        calculator("10 / 0")


def test_sql_allows_select():
    result = sql_tool("SELECT * FROM users;")
    assert result["status"] == "validated"


def test_sql_blocks_drop_table():
    with pytest.raises(ValueError):
        sql_tool("DROP TABLE users;")


def test_sql_blocks_multiple_statements():
    with pytest.raises(ValueError):
        sql_tool("SELECT 1; DROP TABLE users;")


def test_sql_blocks_empty_query():
    with pytest.raises(ValueError):
        sql_tool("")
