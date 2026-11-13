
"""Persistent storage for AI CFD evaluation experiments."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ExperimentRegistry:
    def __init__(self, database_path="reports/experiments.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True, exist_ok=True
        )
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    run_id TEXT PRIMARY KEY,
                    challenge_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    results_json TEXT NOT NULL
                )
            """)

    def save(self, challenge_id, provider, results):
        run_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO experiments
                (run_id, challenge_id, provider,
                 timestamp, results_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    challenge_id,
                    provider,
                    timestamp,
                    json.dumps(results, allow_nan=False),
                ),
            )

        return run_id

    def get(self, run_id):
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT run_id, challenge_id, provider,
                       timestamp, results_json
                FROM experiments
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "run_id": row[0],
            "challenge_id": row[1],
            "provider": row[2],
            "timestamp": row[3],
            "results": json.loads(row[4]),
        }

    def list_runs(self, challenge_id=None):
        query = """
            SELECT run_id, challenge_id, provider,
                   timestamp, results_json
            FROM experiments
        """
        params = ()

        if challenge_id is not None:
            query += " WHERE challenge_id = ?"
            params = (challenge_id,)

        query += " ORDER BY timestamp DESC, run_id DESC"

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            {
                "run_id": row[0],
                "challenge_id": row[1],
                "provider": row[2],
                "timestamp": row[3],
                "results": json.loads(row[4]),
            }
            for row in rows
        ]
