# RunPod 모델 연결 준비

현재 자원을 생성하거나 GPU 학습·추론을 실행하지 않았습니다. 아래는 운영 인계용 절차입니다.

## 담당자와 보존

학습 담당 1명과 대체 담당 1명을 정합니다. 실험 ID, GPU 종류, 시작·종료, 데이터·어댑터 저장 경로, 확인한 비용을 남깁니다. 장시간 학습 전에 짧은 실행으로 체크포인트 저장·재로딩을 확인합니다.

Pod 중지·종료·볼륨 보존은 서로 다릅니다. 컨테이너 디스크에만 중요한 결과를 저장하지 말고, 종료 전 지속 저장소에서 다시 읽히는지 확인하세요. [RunPod 공식 Pod 관리 문서](https://docs.runpod.io/pods/manage-pods)

## 모델 연결 순서

1. 이용 조건·한국어·출력 규격·서빙 호환성을 확인한 베이스 모델을 정한다.
2. 검수된 데이터와 학습 설정으로 어댑터를 만든다.
3. 모델/어댑터를 서빙하고 served model name을 확인한다.
4. API 키와 모델 주소를 서버 환경변수로 넣는다.
5. 한 사례로 기준 추출·검토·검증의 JSON Schema 응답을 확인한다.
6. 원문 인용·오류·타임아웃·토큰 집계를 점검한다.
7. 같은 평가셋에서 베이스와 학습 모델을 비교한다.
8. 발표 전에 cold/warm 지연과 복구 시간을 측정한다.

현재 연결부는 vLLM 호환 Chat Completions 형태입니다. RunPod의 임의 Serverless handler 입력 형식과 직접 호환된다고 가정하지 않습니다. /chat/completions를 제공하는 엔드포인트가 필요하며, 다른 handler이면 providers.py의 경계를 유지하면서 변환기를 추가합니다. [vLLM 공식 서버 문서](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/)

Serverless flex worker의 축소·cold start와 active worker의 상시 비용을 실제 데모 조건으로 비교합니다. [RunPod worker 문서](https://docs.runpod.io/serverless/workers/overview)

## 운영 범위

- 실제 모델 호출은 사용자가 화면에서 모델 모드로 실행할 때만 시작합니다.
- 엔드포인트는 서버 설정으로 고정하고 리다이렉트는 따라가지 않습니다.
- 429/503만 한 번 재시도합니다. 응답 timeout은 이미 비용이 발생했을 수 있어 자동 재호출하지 않습니다.
- 예제 응답을 실제 모델 실패의 대체 답변으로 반환하지 않습니다.
- 비용은 토큰·GPU 시간·스토리지·네트워크와 당시 요금을 직접 결합해 산정합니다.

팀 공유 배포 이전에 인증·권한·TLS·데이터 보관·DB/worker 분리를 추가해야 합니다. 현재의 localhost 기반을 그대로 공개 인터넷에 노출하는 구성은 제공하지 않습니다.

