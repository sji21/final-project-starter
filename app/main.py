from contextlib import asynccontextmanager
from typing import Annotated
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import ROOT, Settings
from app.errors import AppError
from app.models import DecisionRequest, RunRequest
from app.packs import PackRegistry
from app.reports import diagnostic_metrics, markdown_report
from app.store import Store
from app.workflow import Workflow


def create_app(settings=None, provider_factory=None):
    settings = settings or Settings()
    registry = PackRegistry(settings.packs_dir)
    store = Store(settings.data_dir / "workspace.sqlite3")
    workflow = Workflow(settings, registry, store, provider_factory)

    @asynccontextmanager
    async def lifespan(app):
        store.recover_interrupted()
        yield
        workflow.close()

    app = FastAPI(title="Topic Platform", version="0.1.0", lifespan=lifespan)
    app.state.store = store
    app.state.workflow = workflow
    app.state.registry = registry
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))

    @app.middleware("http")
    async def local_request_boundary(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin and request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin_parts = urlsplit(origin)
            expected_host = request.headers.get("host")
            if origin_parts.scheme not in {"http", "https"} or origin_parts.netloc != expected_host:
                return JSONResponse(
                    {
                        "error": {
                            "code": "ORIGIN_DENIED",
                            "message": "허용되지 않은 요청 출처입니다.",
                        }
                    },
                    status_code=403,
                )
        size = request.headers.get("content-length")
        if size and (not size.isdigit() or int(size) > 1_000_000):
            return JSONResponse(
                {"error": {"code": "INPUT_TOO_LARGE", "message": "입력이 너무 큽니다."}},
                status_code=413,
            )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path == "/":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
            )
        return response

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        return JSONResponse(
            {"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status
        )

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.1.0", "model_ready": settings.model_ready}

    @app.get("/api/packs")
    def packs():
        return {"packs": [pack.public() for pack in registry.packs.values()]}

    @app.get("/api/packs/{pack_id}/example")
    def example(pack_id: str):
        return registry.get(pack_id).example.model_dump()

    @app.get("/api/runs")
    def runs():
        return {"runs": store.list_runs()}

    @app.post("/api/runs", status_code=202)
    def start_run(
        request: RunRequest,
        idempotency_key: Annotated[str | None, Header(pattern=r"^[A-Za-z0-9_-]{1,100}$")] = None,
    ):
        return workflow.submit(request, idempotency_key or str(uuid4()))

    @app.get("/api/runs/{run_id}")
    def run(run_id: str):
        return store.get(run_id)

    @app.post("/api/runs/{run_id}/decisions")
    def decide(run_id: str, decision: DecisionRequest):
        return store.decide(run_id, decision)

    @app.get("/api/runs/{run_id}/metrics")
    def metrics(run_id: str):
        return diagnostic_metrics(store.get(run_id))

    @app.get("/api/runs/{run_id}/report.md", response_class=PlainTextResponse)
    def report(run_id: str):
        run = store.get(run_id)
        if run["status"] not in {"awaiting_review", "completed"}:
            raise AppError("REPORT_NOT_READY", "완료된 실행에서 보고서를 만들 수 있습니다.", 409)
        return PlainTextResponse(
            markdown_report(run),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="review-{run_id}.md"'},
        )

    @app.get("/")
    def index():
        return FileResponse(ROOT / "web" / "index.html")

    app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")
    return app
