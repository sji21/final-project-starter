import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.errors import AppError


def now():
    return datetime.now(UTC).isoformat()


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connection() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    request_hash TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    @contextmanager
    def connection(self):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def recover_interrupted(self):
        with self.connection() as con:
            con.execute("BEGIN IMMEDIATE")
            for row in con.execute("SELECT id, payload FROM runs").fetchall():
                item = json.loads(row["payload"])
                if item["status"] in {"queued", "running"}:
                    item.update(status="failed", revision=item["revision"] + 1, updated_at=now())
                    item["error"] = {
                        "code": "INTERRUPTED",
                        "message": "서버 재시작으로 중단되었습니다. 새 검토로 다시 실행하세요.",
                    }
                    con.execute(
                        "UPDATE runs SET payload=? WHERE id=?", (json.dumps(item), row["id"])
                    )

    def create(self, request, pack, key, request_hash):
        with self.connection() as con:
            con.execute("BEGIN IMMEDIATE")
            old = con.execute("SELECT * FROM runs WHERE idempotency_key=?", (key,)).fetchone()
            if old:
                if old["request_hash"] != request_hash:
                    raise AppError(
                        "IDEMPOTENCY_CONFLICT",
                        "같은 요청 키로 다른 입력을 실행할 수 없습니다.",
                        409,
                    )
                return json.loads(old["payload"]), False
            active = sum(
                json.loads(row["payload"])["status"] in {"queued", "running"}
                for row in con.execute("SELECT payload FROM runs").fetchall()
            )
            if active >= 8:
                raise AppError(
                    "QUEUE_FULL", "대기 작업이 많습니다. 기존 작업 완료 후 다시 시도하세요.", 429
                )
            run = {
                "id": str(uuid4()),
                "revision": 1,
                "status": "queued",
                "stage": "queued",
                "created_at": now(),
                "updated_at": now(),
                "request": request.model_dump(),
                "pack": pack.public(),
                "input_hash": request_hash,
                "criteria": [],
                "chunks": [],
                "retrieval": {},
                "items": [],
                "trace": [],
                "audit": [],
                "error": None,
                "provenance": {
                    "engine_version": "0.1.0",
                    "pack_hash": pack.fingerprint,
                    "execution": "fixture_replay" if request.mode == "demo" else "model",
                    "demo_is_not_model_quality": request.mode == "demo",
                },
            }
            con.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
                (
                    run["id"],
                    key,
                    request_hash,
                    json.dumps(run, ensure_ascii=False),
                    run["created_at"],
                ),
            )
            return run, True

    def get(self, run_id):
        with self.connection() as con:
            row = con.execute("SELECT payload FROM runs WHERE id=?", (run_id,)).fetchone()
            if not row:
                raise AppError("NOT_FOUND", "검토 작업을 찾을 수 없습니다.", 404)
            return json.loads(row["payload"])

    def list_runs(self):
        with self.connection() as con:
            rows = con.execute(
                "SELECT payload FROM runs ORDER BY created_at DESC LIMIT 100"
            ).fetchall()
            return [
                {key: run[key] for key in ("id", "revision", "status", "created_at", "updated_at")}
                | {
                    "title": run["request"]["title"],
                    "mode": run["request"]["mode"],
                    "pack_name": run["pack"]["name"],
                    "item_count": len(run["items"]),
                }
                for row in rows
                if (run := json.loads(row["payload"]))
            ]

    def mutate(self, run_id, change):
        with self.connection() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT payload FROM runs WHERE id=?", (run_id,)).fetchone()
            if not row:
                raise AppError("NOT_FOUND", "검토 작업을 찾을 수 없습니다.", 404)
            run = json.loads(row["payload"])
            change(run)
            run["revision"] += 1
            run["updated_at"] = now()
            con.execute(
                "UPDATE runs SET payload=? WHERE id=?",
                (json.dumps(run, ensure_ascii=False), run_id),
            )
            return run

    def decide(self, run_id, decision):
        def change(run):
            if run["revision"] != decision.revision:
                raise AppError(
                    "REVISION_CONFLICT",
                    "다른 변경이 저장되었습니다. 새로고침 후 다시 확인하세요.",
                    409,
                )
            if run["status"] not in {"awaiting_review", "completed"}:
                raise AppError("NOT_REVIEWABLE", "실행이 끝난 작업만 검토할 수 있습니다.", 409)
            item = next(
                (item for item in run["items"] if item["criterion_id"] == decision.criterion_id),
                None,
            )
            if not item:
                raise AppError("NOT_FOUND", "검토 항목을 찾을 수 없습니다.", 404)
            entry = decision.model_dump(exclude={"revision"}) | {"at": now()}
            item["decision"] = entry
            run["audit"].append(entry)
            run["status"] = (
                "completed" if all(i["decision"] for i in run["items"]) else "awaiting_review"
            )

        return self.mutate(run_id, change)
