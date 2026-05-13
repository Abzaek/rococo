"""Tests for the shared sort-column validator used by repositories and DB adapters."""
import pytest

from rococo.data.sort_validation import _validate_sort_columns


class TestValidSortColumns:
    """Valid (column, direction) entries should pass without raising."""

    def test_empty_sort_is_allowed(self):
        _validate_sort_columns(None)
        _validate_sort_columns([])

    def test_simple_column_asc(self):
        _validate_sort_columns([("name", "ASC")])

    def test_simple_column_desc(self):
        _validate_sort_columns([("name", "DESC")])

    def test_direction_is_case_insensitive(self):
        _validate_sort_columns([("name", "asc")])
        _validate_sort_columns([("name", "desc")])
        _validate_sort_columns([("name", "Asc")])

    def test_qualified_column(self):
        _validate_sort_columns([("users.name", "ASC")])

    def test_underscore_and_digits_in_column(self):
        _validate_sort_columns([("_private_col_2", "ASC")])
        _validate_sort_columns([("schema1.col_2", "DESC")])

    def test_multiple_entries(self):
        _validate_sort_columns([
            ("name", "ASC"),
            ("created_at", "DESC"),
            ("users.id", "asc"),
        ])


class TestInvalidSortColumns:
    """Anything that could enable SQL injection should raise ValueError."""

    def test_column_with_space(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("name DESC", "ASC")])

    def test_column_with_semicolon(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("name; DROP TABLE users", "ASC")])

    def test_column_with_quotes(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("name'", "ASC")])

    def test_column_starting_with_digit(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("1name", "ASC")])

    def test_column_with_parentheses(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("count(*)", "ASC")])

    def test_column_non_string(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([(123, "ASC")])

    def test_too_many_dots_in_column(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("db.schema.col", "ASC")])

    def test_empty_column(self):
        with pytest.raises(ValueError, match="Invalid sort column"):
            _validate_sort_columns([("", "ASC")])

    def test_invalid_direction(self):
        with pytest.raises(ValueError, match="Invalid sort direction"):
            _validate_sort_columns([("name", "UPWARDS")])

    def test_injection_in_direction(self):
        with pytest.raises(ValueError, match="Invalid sort direction"):
            _validate_sort_columns([("name", "ASC; DROP TABLE users")])

    def test_direction_non_string(self):
        with pytest.raises(ValueError, match="Invalid sort direction"):
            _validate_sort_columns([("name", 1)])

    def test_entry_not_a_pair(self):
        with pytest.raises(ValueError, match="Invalid sort entry"):
            _validate_sort_columns([("name",)])

    def test_entry_not_iterable(self):
        with pytest.raises(ValueError, match="Invalid sort entry"):
            _validate_sort_columns([42])

    def test_first_bad_entry_in_a_list_still_raises(self):
        with pytest.raises(ValueError):
            _validate_sort_columns([("name", "ASC"), ("bad col", "ASC")])
