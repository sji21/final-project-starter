# 평가와 데이터 준비

## 실행 결과 평가

브라우저에서 실행 JSON을 내보낸 뒤 고정된 정답 JSON과 비교합니다.

```bash
python -m app.cli evaluate --run artifacts/local/run.json --gold benchmarks/requirements-review.demo-gold.json --out artifacts/local/evaluation.json
```

출력 파일은 새 경로를 사용합니다. 기존 결과를 덮어쓰지 않습니다.

판정별 precision/recall/F1, 정답이 존재하는 라벨의 macro F1, 누락·예상 밖 기준 ID, 혼동 행렬, 전달 문맥 내 정답 근거 recall을 계산합니다. 검색 문맥의 적중과 모델이 실제 선택한 인용은 다른 지표입니다.

함께 제공한 gold 파일은 예제 재생을 검사하기 위한 **미검수 합성 초안**입니다. 같은 고정 응답과 비교해 일치도가 100%여도 AI 성능이 아닙니다. 도구는 demo 모드 또는 human_reviewed=false를 모델 성능으로 표시하지 않습니다. human_reviewed는 데이터 제공자가 검수 근거와 함께 관리해야 하는 선언이며 도구가 사람 검토를 자동 인증하지 않습니다.

실제 평가에서는 원문 계열 중복을 피한 독립 정답셋, 검토자, 판정 기준, 고정한 데이터 버전, 비교 모델을 기록합니다. 업무별 지연·사람 수정량·완료 시간도 함께 측정합니다.

## SFT 레코드

training/records.example.jsonl은 규격 설명용 draft 레코드입니다. 다음을 포함합니다.

- id / group_id / split(train, validation, test)
- pack_id / source / license_note
- review_status(draft, approved)
- messages(system/user/assistant)

검사:

```bash
python -m app.cli dataset-check training/records.example.jsonl
```

사람이 검수한 train 레코드만 내보내기:

```bash
python -m app.cli dataset-export path/to/reviewed.jsonl --out artifacts/local/train-v1.jsonl
```

같은 원문 그룹이 여러 split에 걸치거나, 공백을 정규화한 같은 입력이 다른 split에 있으면 실패합니다. 학습 레코드가 draft인 경우 내보내기를 거절합니다. train만 내보내고 ID·수량·hash를 manifest에 남깁니다. 예시 파일은 의도적으로 draft이므로 export가 거절되는 것이 정상입니다.

검사는 의미상 유사 문서·잘못된 정답·개인정보·이용 허락을 자동 판단하지 않습니다. 사용자 UI에서 의견을 채택했다는 사실을 곧바로 모델 학습 정답으로 변환하지도 않습니다.

## 첫 실제 실험

1. 업무별 개발 사례와 독립 검증·최종 평가를 분리합니다.
2. 베이스 모델 + 같은 RAG 문맥으로 기준 성능을 기록합니다.
3. 작은 학습 실행으로 토크나이징·저장·어댑터 추론을 확인합니다.
4. 오류 유형에 맞춰 데이터 품질을 개선합니다.
5. 학습 모델 + 같은 RAG 문맥을 비교합니다.
6. 최종 평가셋을 보며 계속 튜닝하지 않고 고정된 마지막 버전을 평가합니다.

학습 라이브러리·모델·GPU는 아직 정하지 않았습니다. training/experiment.template.json에 모델 revision, 데이터 hash, 하이퍼파라미터, 비용, 평가 파일을 기록하는 틀을 제공합니다.

