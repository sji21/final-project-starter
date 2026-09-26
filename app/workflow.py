import logging
import time
from concurrent.futures import ThreadPoolExecutor

from app.errors import AppError
from app.models import Critique, Extraction, Findings
from app.packs import digest
from app.providers import DemoProvider, ModelProvider
from app.retrieval import chunk_documents, retrieve
from app.validation import apply_critique, validate_extraction, validate_findings

logger = logging.getLogger(__name__)


class Workflow:
    def __init__(self, settings, registry, store, provider_factory=None):
        self.settings = settings
        self.registry = registry
        self.store = store
        self.provider_factory = provider_factory
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="review")

    def close(self):
        self.executor.shutdown(wait=True)

    def submit(self, request, key):
        pack = self.registry.get(request.pack_id)
        if self.provider_factory:
            provider = self.provider_factory(request, pack)
        elif request.mode == "demo":
            provider = DemoProvider(pack, request.documents)
        else:
            provider = ModelProvider(self.settings, pack)
        request_hash = digest({"request": request.model_dump(), "pack": pack.fingerprint})
        run, created = self.store.create(request, pack, key, request_hash)
        if created:
            self.executor.submit(self.execute, run["id"], request, pack, provider)
        return run

    def update(self, run_id, **fields):
        return self.store.mutate(run_id, lambda run: run.update(fields))

    def stage(self, run_id, name, function):
        self.update(run_id, stage=name)
        started = time.perf_counter()
        value, metadata = function()
        event = {
            "stage": name,
            "duration_ms": round((time.perf_counter() - started) * 1000),
            **metadata,
        }
        self.store.mutate(run_id, lambda run: run["trace"].append(event))
        return value

    def execute(self, run_id, request, pack, provider):
        try:
            self.update(run_id, status="running")
            chunks = self.stage(
                run_id,
                "normalize",
                lambda: (
                    chunk_documents(request.documents),
                    {"kind": "deterministic", "billable_model_call": False},
                ),
            )
            self.update(run_id, chunks=chunks)
            basis = [chunk for chunk in chunks if chunk["role"] == "basis"]
            extraction = self.stage(
                run_id,
                "extract",
                lambda: provider.call(
                    "extract", {"task": pack.manifest.task, "basis_chunks": basis}, Extraction
                ),
            )
            validate_extraction(extraction, chunks)
            criteria = extraction.criteria
            self.update(run_id, criteria=[criterion.model_dump() for criterion in criteria])
            retrieval = self.stage(
                run_id,
                "retrieve",
                lambda: (
                    retrieve(criteria, chunks),
                    {"kind": "lexical_retrieval", "billable_model_call": False},
                ),
            )
            self.update(run_id, retrieval=retrieval)
            by_id = {chunk["id"]: chunk for chunk in chunks}
            review_input = {
                "task": pack.manifest.task,
                "criteria": [criterion.model_dump() for criterion in criteria],
                "evidence_by_criterion": {
                    key: [by_id[item] for item in scope["chunk_ids"]]
                    for key, scope in retrieval.items()
                },
                "scope": retrieval,
                "all_target_documents_complete": all(
                    doc.complete for doc in request.documents if doc.role == "target"
                ),
            }
            findings = self.stage(
                run_id, "review", lambda: provider.call("review", review_input, Findings)
            )
            items = validate_findings(findings, criteria, chunks, retrieval, request.documents)
            critique = self.stage(
                run_id,
                "critic",
                lambda: provider.call(
                    "critic", {**review_input, "draft_findings": items}, Critique
                ),
            )
            items = apply_critique(items, critique)
            self.update(run_id, status="awaiting_review", stage="human_review", items=items)
        except AppError as exc:
            self.update(run_id, status="failed", error={"code": exc.code, "message": exc.message})
        except Exception as exc:  # noqa: BLE001 — background jobs must persist terminal failure
            # Never include document content or provider responses in public error details.
            logger.error("Workflow %s failed: %s", run_id, type(exc).__name__)
            self.update(
                run_id,
                status="failed",
                error={
                    "code": "WORKFLOW_FAILED",
                    "message": "실행 중 오류가 발생했습니다. 서버 로그를 확인하세요.",
                },
            )
