# FINAL Project Starter · 작업실

주제별 설정과 프롬프트를 교체하는 **문서 기반 업무 검토 플랫폼의 실행 가능한 공통 기반**입니다. 5인팀·약 6주 프로젝트의 선작업으로 만들었습니다.

- 요구사항·테스트 검토 / CS 답변 검수 업무 팩 2개.
- 기준 추출 → 근거 검색 → 검토 초안 → 독립 검증 → 사람 검토.
- 문서 버전·근거 원문·실행 기록·수정/채택/반려 이력.
- Markdown 보고서와 JSON 내보내기.
- vLLM 호환 모델 연결부, 단계별 모델/LoRA 이름 지정.
- 오프라인 평가·데이터 분할 검사·검수된 SFT 자료 내보내기.

**현재 데모는 정해진 합성 예제의 응답을 재생합니다. 실제 AI 분석이나 파인튜닝 성능을 보여주는 것이 아닙니다.** 변경한 문서를 데모에 넣으면 거절합니다. 실제 모델 모드는 모델 서버를 설정해야 사용할 수 있습니다.

## 프로젝트 준비 자료

- [전체 준비 자료 안내](research/00-먼저읽기.md)
- [18기 2팀 HelixOps 우선 분석](research/01-HelixOps-우선분석.md)
- [FINAL 25개 비교](research/02-FINAL-25개-비교.md)
- [5명·6주 준비안](research/03-6주-프로젝트-준비안.md)
- [5인팀 협업 규칙](research/04-5인팀-협업규칙.md)
- [현재 구현 범위와 다음 작업](research/08-공통플랫폼-진행결과.md)

분석 자료는 공개 저장소를 확인한 작성 시점의 기록입니다. 타 팀의 성능 수치는 재현 결과가 아니며, 해당 저장소의 코드나 모델을 이 프로젝트에 복제하지 않았습니다. 최종 주제·팀 역할·GPU 예산은 미확정입니다.

## 실행

Python 3.12로 확인했습니다. 프로젝트 루트에서 실행하세요.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m app
```

Windows에서는 setup.ps1 -Python <python.exe 경로> 실행 후 start.ps1을 사용할 수도 있습니다. 시스템 전체 Python을 수정하지 않고 프로젝트 가상 환경을 만듭니다.

macOS/Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m app
```

브라우저: [http://127.0.0.1:8765](http://127.0.0.1:8765)  
API 계약: [OpenAPI](http://127.0.0.1:8765/openapi.json), [API 문서](http://127.0.0.1:8765/docs)

종료는 서버 터미널에서 Ctrl+C입니다. 실행 데이터는 기본 .data/workspace.sqlite3에 남습니다. APP_DATA_DIR 환경변수로 저장 위치를 바꿀 수 있습니다. 허용 Host 목록은 APP_ALLOWED_HOSTS로 바꾸며 기본값은 localhost,127.0.0.1입니다. 프런트엔드 빌드나 npm 설치는 필요하지 않습니다.

## 3분 확인 순서

1. 요구사항·테스트 예제를 실행한다.
2. 불일치 항목의 근거 버튼을 눌러 원문을 확인한다.
3. 검토 의견을 열고 제안 수정·사유를 저장한다.
4. 보고서를 내려받고 변경한 문구가 포함되는지 확인한다.
5. CS 답변 검수로 전환해 같은 흐름을 실행한다.
6. 실행 기록에서 앞선 작업을 다시 연다.

## 주제를 교체하는 위치

```text
app/                        공통 계약·실행·검증·저장·평가
web/                        업무 공통 화면
packs/<업무-id>/
  manifest.json             이름·입력 문서·판정 라벨·학습 태스크
  prompts/extract.md         검토 기준 추출
  prompts/review.md          도메인 검토·수정안
  prompts/critic.md          독립 검증
  example.json              입력 예제
  demo-responses.json       데모 전용 고정 출력
benchmarks/                 데모 회귀 확인용 정답 초안
training/                   학습 데이터 규격과 실험 양식
tests/                      오프라인 계약·실패·영속성 검사
docs/                       구조·주제 교체·평가·운영·팀 백로그
```

새 팩은 서버 재시작 시 읽습니다. 공통 결과는 covered / partial / missing / conflict / needs_review의 다섯 가지이고, 화면 표현은 manifest에서 바꿉니다. 상세 절차: [주제 교체 가이드](docs/SWAP_TOPIC.md).

## 실제 모델 연결

서버를 시작하는 터미널에 설정합니다. .env.example은 참고용이며 Python 실행 시 자동으로 읽지 않습니다. Docker Compose는 별도의 .env 로딩 규칙을 사용합니다.

```powershell
$env:MODEL_BASE_URL = "https://YOUR-ENDPOINT/v1"
$env:MODEL_NAME = "YOUR-SERVED-MODEL"
$env:MODEL_API_KEY = "YOUR-SERVER-KEY"
$env:MODEL_REVIEW = "YOUR-SERVED-LORA-ALIAS"
.\.venv\Scripts\python.exe -m app
```

실제 키는 저장소에 넣지 않습니다. MODEL_EXTRACT, MODEL_REVIEW, MODEL_CRITIC를 각각 지정할 수 있고, 비워두면 MODEL_NAME을 사용합니다. 브라우저가 모델 서버 주소나 키를 지정하지 않습니다.

호환 조건: /chat/completions, messages, response_format의 JSON Schema, choices[].message.content. 모델 서버의 구조화 출력·채팅 템플릿·LoRA 별칭 지원은 실제 연결 시 확인해야 합니다. 공개 vLLM 서버로 접속하거나 API 비용을 지출하지 않았습니다.

## 검증

```bash
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q
node --check web/app.js
```

의존성은 검증 환경의 requirements.lock으로 고정했습니다. 2026-09-27 최초 업로드 코드의 [GitHub Actions 검사](https://github.com/sji21/final-project-starter/actions/runs/36255693667)가 통과했습니다. Dockerfile·Compose도 준비했으나 컨테이너 빌드·배포는 검증하지 않았습니다.

[실제 검증 기록](docs/VALIDATION.md) · [구조](docs/ARCHITECTURE.md) · [평가](docs/EVALUATION.md) · [RunPod 연결 준비](docs/RUNPOD.md) · [5인팀 백로그](docs/TEAM_BACKLOG.md)

## 현재 범위

- UTF-8 텍스트/Markdown 붙여넣기·파일 불러오기, RunRequest JSON 가져오기.
- 작은 문서는 대상 전체를 전달하고, 큰 문서는 단순 어휘 검색으로 후보를 고릅니다. 임베딩 RAG는 아직 연결하지 않았습니다.
- 문서 기반 검토 계열은 팩 교체로 바꿀 수 있습니다. 외부 업무 실행·OCR·음성·조직 인증·다중 사용자 권한은 추가 개발 대상입니다.
- 검토자 이름은 로컬 입력이며 인증된 신원이 아닙니다. 현재 서버는 로컬 개발용이고 단일 프로세스만 지원합니다.
- 모델의 인용 ID·원문 일치는 코드로 검사합니다. 인용의 의미상 적절함과 모델 판정의 진실성을 자동 보증하지는 않습니다.
- 파인튜닝 모델, 실데이터, 최종 평가셋, GPU 학습 성능은 아직 없습니다.

이 기반을 최종 서비스로 발전시키려면 도메인 데이터·업무 기준·사용자 평가를 가장 먼저 채워야 합니다.

