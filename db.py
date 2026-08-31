"""Databricks SQL access with an explicit, safe local-demo fallback."""

from __future__ import annotations

import os
from contextlib import closing

import pandas as pd


def _setting(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


def is_configured() -> bool:
    return all(_setting(key) for key in ("DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN"))


def query(statement: str) -> pd.DataFrame:
    """Run read-only SQL. Credentials are never accepted from the app UI."""
    if not is_configured():
        raise RuntimeError("Databricks SQL is not configured")
    from databricks import sql

    with closing(sql.connect(
        server_hostname=_setting("DATABRICKS_SERVER_HOSTNAME"),
        http_path=_setting("DATABRICKS_HTTP_PATH"),
        access_token=_setting("DATABRICKS_TOKEN"),
    )) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(statement)
            columns = [column[0] for column in cursor.description]
    return pd.DataFrame(cursor.fetchall(), columns=columns)


def query_many(statements: dict[str, str]) -> dict[str, pd.DataFrame]:
    """Run several read-only queries in one warehouse session for faster page loads."""
    if not is_configured():
        raise RuntimeError("Databricks SQL is not configured")
    from databricks import sql

    results: dict[str, pd.DataFrame] = {}
    with closing(sql.connect(
        server_hostname=_setting("DATABRICKS_SERVER_HOSTNAME"),
        http_path=_setting("DATABRICKS_HTTP_PATH"),
        access_token=_setting("DATABRICKS_TOKEN"),
    )) as connection:
        with closing(connection.cursor()) as cursor:
            for name, statement in statements.items():
                cursor.execute(statement)
                columns = [column[0] for column in cursor.description]
                results[name] = pd.DataFrame(cursor.fetchall(), columns=columns)
    return results


def connection_status() -> tuple[bool, str]:
    if not is_configured():
        return False, "Local deterministic dataset"
    try:
        query("SELECT 1 AS connected")
        return True, "Databricks SQL + Unity Catalog"
    except ModuleNotFoundError:
        return False, "Databricks connector missing — launch with .venv Python"
    except Exception as exc:
        return False, f"Databricks configured but unavailable: {type(exc).__name__}"
