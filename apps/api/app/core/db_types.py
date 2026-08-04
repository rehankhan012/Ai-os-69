"""
Portable UUID column type.

Works on PostgreSQL (native UUID) and SQLite (CHAR(32)). Unlike the plain
`sqlalchemy.Uuid`, it also accepts plain strings on bind (path params, query
params, JWT `sub`, frontend ids) so endpoints never need manual
`uuid.UUID(...)` conversions. Invalid id strings bind to NULL, which makes
lookups return no rows (404) instead of crashing with a 500.
"""

import uuid

from sqlalchemy import Uuid as SqlUuid


class Uuid(SqlUuid):
    """UUID type that coerces string values to uuid.UUID on bind."""

    def bind_processor(self, dialect):
        base = super().bind_processor(dialect)

        def process(value):
            if isinstance(value, str):
                try:
                    value = uuid.UUID(value)
                except ValueError:
                    # Malformed id → NULL so `== id` matches nothing → 404
                    value = None
            return base(value) if base is not None else value

        return process
