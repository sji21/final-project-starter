import json

import httpx
import pytest

from app.config import Settings
from app.errors import AppError
from app.models import Critique
from app.packs import PackRegistry
from app.providers import ModelProvider


def configured(tmp_path):
    return Settings(
        data_dir=tmp_path,
        model_base_url="https://model.example/v1",
        model_name="base",
        model_api_key="test-secret",
        stage_models={"review": "trained-adapter"},
    )


def test_compatible_request_selects_adapter_and_records_usage(tmp_path):
    seen = []

    def handle(request):
        seen.append(json.loads(request.content))
        assert request.headers["Authorization"] == "Bearer test-secret"
        assert str(request.url) == "https://model.example/v1/chat/completions"
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"issues":[]}'}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 13, "completion_tokens": 7},
            },
        )

    settings = configured(tmp_path)
    pack = PackRegistry(settings.packs_dir).get("requirements-review")
    result, trace = ModelProvider(settings, pack, httpx.MockTransport(handle)).call(
        "review", {"sample": 1}, Critique
    )
    assert result.issues == []
    assert seen[0]["model"] == "trained-adapter"
    assert seen[0]["response_format"]["type"] == "json_schema"
    assert trace["prompt_tokens"] == 13
    assert trace["attempts"] == 1


@pytest.mark.parametrize("status", [401, 302, 500])
def test_provider_error_bodies_not_exposed(tmp_path, status):
    settings = configured(tmp_path)
    pack = PackRegistry(settings.packs_dir).get("cs-quality")
    transport = httpx.MockTransport(
        lambda _: httpx.Response(status, text="test-secret private document")
    )
    with pytest.raises(AppError) as error:
        ModelProvider(settings, pack, transport).call("critic", {}, Critique)
    assert "test-secret" not in error.value.message
    assert "private" not in error.value.message


def test_invalid_json_does_not_fall_back_to_demo(tmp_path):
    settings = configured(tmp_path)
    pack = PackRegistry(settings.packs_dir).get("cs-quality")
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})
    )
    with pytest.raises(AppError) as error:
        ModelProvider(settings, pack, transport).call("critic", {}, Critique)
    assert error.value.code == "MODEL_INVALID_OUTPUT"


def test_rate_limit_retried_once(tmp_path):
    settings = configured(tmp_path)
    pack = PackRegistry(settings.packs_dir).get("cs-quality")
    calls = []

    def handle(request):
        calls.append(1)
        return httpx.Response(429, text="busy")

    with pytest.raises(AppError):
        ModelProvider(settings, pack, httpx.MockTransport(handle)).call("critic", {}, Critique)
    assert len(calls) == 2


def test_ambiguous_timeout_not_retried(tmp_path):
    settings = configured(tmp_path)
    pack = PackRegistry(settings.packs_dir).get("cs-quality")
    calls = []

    def handle(request):
        calls.append(1)
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(AppError) as error:
        ModelProvider(settings, pack, httpx.MockTransport(handle)).call("critic", {}, Critique)
    assert error.value.code == "MODEL_TIMEOUT"
    assert len(calls) == 1
