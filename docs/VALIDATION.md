# 검증 기록

검증일: 2026-09-26 · Windows · Python 3.12.14 · Node.js 24.13.1.

## 자동 검사

| 검사 | 실제 결과 |
| --- | --- |
| python -m ruff check app tests | 통과 |
| python -m ruff format --check app tests | 23개 파일 통과 |
| python -m pytest -q | **35 passed**, 3.69초 |
| node --check web/app.js | 통과 |

테스트는 모델 서버를 호출하지 않습니다. 모델 연결 계약 검사는 httpx MockTransport로 재현했습니다. Starlette TestClient의 httpx 사용 중단 예정 경고 1건이 있으며 실패는 없습니다. 실제 GPU·모델 성능 검증과 구분합니다.

주요 검사 범위:

- 요구사항 검토와 CS 검수의 전체 실행, 세 번째 팩 추가 시 공통 앱 코드 유지.
- 세 역할의 JSON 계약과 모델 별칭, 응답 오류·시간 초과·제한된 재시도.
- 근거 원문·문서 버전·문서 역할·모델에 제시한 문맥의 일치.
- 확인 범위가 불완전하면 누락 판정을 사람 확인으로 낮추기.
- 중복 실행 방지, 동시 수정 충돌, 변경 이력·보고서·재시작 후 중단 처리.
- 데모 입력 변경 거절, 모델 미설정 거절, 동일 출처 쓰기 제한.
- 데이터 중복·분할 누출 탐지, 승인된 학습 분할만 내보내기.
- 정답 문서 해시 검증, 누락된 예측 반영, 데모 지표를 모델 품질로 표시하지 않기.

## 실제 브라우저 확인

로컬 앱에서 다음을 수행했습니다.

1. 요구사항·테스트 예제를 실행해 6개 판정을 확인했습니다.
2. 근거 버튼을 열어 대상 문서의 버전·청크·원문을 확인했습니다.
3. REQ-02의 제안을 수정하고 사유를 저장했습니다.
4. CS 예제로 교체해 3개 판정을 확인했습니다.
5. 새로고침 후 실행 기록에서 이전 결과와 수정 이력을 다시 열었습니다.
6. 콘솔 오류가 없었으며 확인 당시 뷰포트 너비 1,277px에서 가로 넘침이 없었습니다.

저장된 검증 산출물:

- [요구사항 실행 JSON](../artifacts/verification/requirements-review.run.json)
- [요구사항 보고서](../artifacts/verification/requirements-review.report.md)
- [요구사항 예제 회귀 평가](../artifacts/verification/requirements-review.evaluation.json)
- [CS 실행 JSON](../artifacts/verification/cs-quality.run.json)
- [CS 보고서](../artifacts/verification/cs-quality.report.md)
- [CS 예제 회귀 평가](../artifacts/verification/cs-quality.evaluation.json)

두 예제의 정답 일치율 1.0은 **고정 데모와 합성 정답의 회귀 확인**입니다. 실제 AI 정확도·파인튜닝 개선·현업 성과를 의미하지 않습니다.

## 데이터 도구 실행

training/records.example.jsonl에 dataset-check를 실행했습니다. 규격 검사는 통과했지만 승인 레코드는 0개입니다. 이 샘플은 학습 데이터 형식을 설명하는 초안이며 학습 준비 완료 상태가 아닙니다.

## 남은 검증

- 실제 모델·LoRA 연결, 구조화 출력 지원, GPU 메모리·지연·비용.
- 독립 검수된 실데이터 평가셋과 베이스 모델 대비 학습 후 평가.
- Docker 빌드, GitHub 원격 CI, 배포 환경.
- 다중 사용자 인증·권한·팀 운영, 큰 문서 검색 품질.
- 모바일·다른 브라우저별 화면 검증.

