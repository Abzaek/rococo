"""Shared sort-column validation used by repositories and DB adapters."""
import re


_SORT_COLUMN_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$')


def _validate_sort_columns(sort):
    """Validate sort column names and directions to block SQL injection."""
    if not sort:
        return
    for entry in sort:
        try:
            column, direction = entry
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid sort entry: {entry!r}. "
                'Expected a (column, direction) tuple, e.g. ("name", "ASC").'
            )
        if not isinstance(column, str) or not _SORT_COLUMN_RE.match(column):
            raise ValueError(
                f"Invalid sort column: {column!r}. "
                'Expected a simple identifier like "column_name" or "table.column_name" '
                "(letters, digits, underscores only)."
            )
        if not isinstance(direction, str) or direction.upper() not in ("ASC", "DESC"):
            raise ValueError(
                f"Invalid sort direction: {direction!r}. "
                'Must be "ASC" or "DESC" (case-insensitive).'
            )
