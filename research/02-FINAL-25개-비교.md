# FINAL 25개 비교

조사 기준일: 2026-09-26. 사용자 요청에 따라 비교 대상은 **25개**로 제한했다. 번호는 우선순위·성적 순위가 아니다. 18기 2팀을 첫 번째로 두고, 업무 분야와 파인튜닝·평가 방식이 다른 사례를 골랐다.

## 확인 수준

- **A:** README와 관련 코드·설정·문서 17개 파일을 확보하고 핵심 경로를 상세 확인.
- **B:** README와 학습·평가·워크플로 관련 핵심 파일 2개씩 확인.
- **C:** README 중심 비교. 디렉터리 목록을 보았더라도 구현 검증으로 승격하지 않았다.
- 모든 수준에서 실행·학습·배포 재현은 하지 않았다. “학습 보고”는 저장소 설명이고, “설정·코드 확인”도 실제 학습 완료를 보증하지 않는다.
- “미확인”은 읽은 공개 자료에서 파인튜닝 증거를 확인하지 못했다는 뜻이다. 해당 팀의 미구현 판정이 아니다.

각 저장소 링크의 README가 해당 행의 기본 출처다. B 수준의 추가 출처는 아래에 연결했다.

| 번호 | 저장소·서비스 | 확인 | 핵심 업무 | sLLM·파인튜닝 근거 | 가져올 점·범위 판단 |
| --- | --- | --- | --- | --- | --- |
| 1 | [SKN18-FINAL-2TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN18-FINAL-2TEAM)<br>HelixOps | A | 문헌 검색→연구 해석→노트 | 12B QLoRA 설명; 공개 서빙 메모는 4B도 존재 | 업무 흐름·데이터 감사를 우선 참고. 최종 모델과 배포 증거는 추가 확인 필요. |
| 2 | [SKN10-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN10-FINAL-1Team)<br>사내 업무 보조 | C | RAG·분석 SQL·코드·이탈 예측 도구 연계 | 미확인 | Swarm/MCP 분업 참고. 도구 연결만으로 필수 파인튜닝이 충족되지는 않음. |
| 3 | [SKN12-FINAL-1TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN12-FINAL-1TEAM)<br>NaruTalk | C | 제약 영업의 계약·고객·직원 정보 지원 | 미확인 | 업종과 사용자를 좁힌 점이 좋음. 계약 생성+검사 같은 한 흐름만 선택. |
| 4 | [SKN13-FINAL-1TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN13-FINAL-1TEAM)<br>CLIKCA | C | 문서 검색·편집·일정 등 사내 작업 | 미확인 | 중앙 라우팅과 진행 추적 참고. 범용 사내 비서 전체는 6주 범위로 넓음. |
| 5 | [SKN13-FINAL-6Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN13-FINAL-6Team)<br>NAVI | C | 사내 문서 검색·경비 업무 지원 | 미확인 | 검색 결과를 업무 실행에 연결하는 참고 사례. 문서 검색 또는 정산 중 하나로 축소. |
| 6 | [SKN14-FINAL-3Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN14-FINAL-3Team)<br>은행 사내 업무 AI | C | 은행 직원의 전문 업무 질의 지원 | Qwen SFT+DPO·RunPod 보고; 모델 버전 표기 혼재 | 학습·서빙·평가 구성 참고. 수치와 최종 모델 버전은 실행 기록 확인 필요. |
| 7 | [SKN17-FINAL-2Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN17-FINAL-2Team)<br>말하는대로 | C | 회의 음성→화자·요약→담당자·기한 추출 | Qwen 파인튜닝 보고 | 후속 업무가 남는 회의 서비스. STT·화자 분리까지 직접 학습하면 부담 증가. |
| 8 | [SKN17-FINAL-5Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN17-FINAL-5Team)<br>글로벌 AI 무역 비서 | C | 무역 서류 간 일관성·규정 근거 검색 | 미확인 | 문서 교차 검토 흐름 참고. 규정 해석의 정답과 평가자를 확보해야 함. |
| 9 | [SKN19-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN19-FINAL-1Team)<br>CALL:ACT | C | 카드 상담원의 실시간 지원·요약·훈련 | 미확인 | 상담원 보조 화면과 후처리 참고. 실시간 음성은 별도 난이도라 MVP 후순위. |
| 10 | [SKN19-FINAL-3Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN19-FINAL-3Team)<br>AJC | C | 변경 사항을 관련 문서에 반영 | Gemma 2 2B·9B 교사 모델 및 임베딩 학습 설명 | 변경 영향과 수정 제안 참고. 변경 이력·문서 충돌 처리부터 정의. |
| 11 | [SKN19-FINAL-5Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN19-FINAL-5Team)<br>똑소리 | C | 법·기준·사례를 나누어 검색하고 검토 | 미확인 | Supervisor와 근거 검토 역할 참고. 공개 README의 GPT 활용을 자체 sLLM 학습과 구분. |
| 12 | [SKN20-FINAL-3TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN20-FINAL-3TEAM)<br>ARAE | C | 건축 도면 자산·추출·검토·검색 | Qwen3-8B 요약·검토 모델 학습 보고 | 구조화 추출과 검토의 분업 참고. CV·도면·규정·자산관리 전체는 과대 범위. |
| 13 | [SKN20-FINAL-6TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN20-FINAL-6TEAM)<br>통합 경영 파트너 | C | 창업·세무·노무·법률 경영 지원 | 미확인 | 분야별 역할 분담 참고. 전문 분야 하나, 문서 유형 하나로 제한해야 함. |
| 14 | [SKN21-FINAL-3TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN21-FINAL-3TEAM)<br>DUDE | B | Planner와 문서 생성·요약·판단 | Kanana 1.5 8B·태스크별 LoRA 설정 확인 | 학습 설정과 단계별 실험 참고. 의도 분류 인코더 학습과 생성형 sLLM 학습을 구분. |
| 15 | [SKN24-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN24-FINAL-1Team)<br>회의피하지마 HPM | C | 회의 준비→요약·태스크→승인 후 Jira | 미확인 | 사람 확인 후 외부 도구 반영하는 UX 참고. vLLM/RunPod 사용만으로 학습 증거가 되지는 않음. |
| 16 | [SKN24-FINAL-3Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN24-FINAL-3Team)<br>ALPLED / AI-DLC | B | 요구사항→개발 문서 생성·검사·재계획 | Qwen3-VL 8B 파인튜닝 보고 | 실제 그래프의 실패 경로와 검사 후 재계획 참고. 재시도 횟수 제한 필요. |
| 17 | [SKN25-FINAL-3Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN25-FINAL-3Team)<br>꽃보다 특허 | C | 청구항·선행기술·명세서 생성·검토 | Examiner 파인튜닝 경로 설명; 실행 미확인 | 초안→검토→보정 형태 참고. 특허 전체 자동화보다 문서 일부 검토로 축소. |
| 18 | [SKN25-FINAL-6Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN25-FINAL-6Team)<br>GameOps | B | 게임 CS 분류·근거 조회·응답·승인 | 미확인 | 라우팅·검색·업무 완료를 나누는 평가가 유용. 학습 태스크는 별도로 설계해야 함. |
| 19 | [SKN26-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN26-FINAL-1Team)<br>HumouR | B | JD·이력서 분석→STAR·면접 질문 | EXAONE 3.5 2.4B LoRA 학습 노트북·서빙 핸들러 확인 | 작은 전문 태스크, 학습→서비스 연결 참고. 자동 합격 판정 대신 담당자 검토 보조. |
| 20 | [SKN26-FINAL-4TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN26-FINAL-4TEAM)<br>Workit | C | 교육기관 SI 계약·산출물 검토 | Kanana 1.5 8B QLoRA 보고 | 이번 과제와 가까운 문서 검토 범위. 데이터 확보와 검토 정답 정의가 선행 조건. |
| 21 | [SKN29-FINAL-1TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN29-FINAL-1TEAM)<br>법인카드 정산 | C | 영수증 추출→규칙 검사→위험 검토·승인 | 미확인; 이상 탐지 ML과 sLLM은 별개 | AI·결정 규칙·사람 승인 역할 분리 참고. 공개 규정과 합성 정산 건으로 축소 가능. |
| 22 | [SKN29-FINAL-2TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN29-FINAL-2TEAM)<br>halil | C | 프로젝트 문맥·도구 기반 업무 에이전트 | 미확인 | 도구 권한·근거·Jira 승인 흐름 참고. 에이전트 빌더 플랫폼 자체는 MVP에서 제외. |
| 23 | [SKN29-FINAL-3TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN29-FINAL-3TEAM)<br>Answervice | B | 호텔 데이터 질의→SQL→검증·보고서 | QLoRA 학습 코드·검토 데이터 운영 규칙 확인 | 모델 출력의 서버 검증·학습 실행 기록 참고. 다중 DB/메타데이터 플랫폼은 축소. |
| 24 | [SKN30-FINAL-1Team](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN30-FINAL-1Team)<br>SalesLuv | C | CRM 문맥→회의·보고→승인 후 업데이트 | 미확인 | 업무 이력과 후속 행동을 연결하는 참고 사례. CRM 전체 대신 회의 후속 조치만 구현. |
| 25 | [SKN32-FINAL-3TEAM](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN32-FINAL-3TEAM)<br>CopyLane | C·진행 중 | 광고 문구 생성·근거 기반 검수 | Qwen3-4B LoRA 계획; README상 학습·평가 미착수 | 구현 상태를 명확히 기록하는 방식 참고. stub·501·테스트 수집 수를 완성도 증거로 사용하지 않음. |

## 우리 팀이 먼저 참고할 6개

### 1. HelixOps — 업무 흐름과 학습 데이터 품질

18기 2팀은 문헌 검색·해석·기록을 연결하고 생성한 학습 데이터를 감사하는 구조가 유용하다. 모델·임베딩·테스트 설명의 불일치도 있어, 구현과 발표 문서를 맞추는 반면교사로 함께 본다. [상세 분석](./01-HelixOps-우선분석.md)

### 2. HumouR — 파인튜닝 태스크를 작게 정하기

전체 HR 업무를 한 번에 학습시키기보다 마스킹과 STAR 변환처럼 입출력이 명확한 일을 분리한다. 공개 노트북에서 데이터 분리, 학습 데이터에 대한 오버샘플링, LoRA·SFTTrainer 구성을 확인했고, RunPod 핸들러에서는 베이스 모델과 어댑터를 함께 로딩한다. 우리 팀은 이런 연결을 핵심 태스크 하나에 적용하면 된다. [학습 노트북](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN26-FINAL-1Team/blob/main/llm/train_star_masking/masking/oversam_exaone_gen_train.ipynb), [서빙 핸들러](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN26-FINAL-1Team/blob/main/runpod/masking_handler.py)

README의 전체 개선 수치와 함께 클래스별 약점도 읽어야 한다. 예를 들어 마스킹 전체 F1 개선 설명과 별개로 JD 차별 표현 항목은 낮은 F1을 보고한다. 우리 팀도 평균 점수와 업무상 중요한 클래스의 누락률을 함께 보여준다. 해당 수치는 이번 조사에서 재현하지 않았다. [README](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN26-FINAL-1Team/blob/main/README.md)

### 3. DUDE — 실험 조건을 먼저 고정하기

문서 요약 설정에는 베이스 모델, 양자화, LoRA, 학습률, 데이터 경로와 평가 목표가 기록되어 있다. ROUGE-L 0.45와 형식 준수율 0.95는 설정의 목표값이며 달성 결과로 읽지 않았다. 별도 실험 보고서는 데이터 분리와 단계별 실험을 설명한다. 단, 이 보고서의 의도 분류 실험과 생성형 sLLM 요약 학습은 다른 작업이다. [요약 설정](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN21-FINAL-3TEAM/blob/main/ai/finetuning/configs/v3_summary.yaml), [의도 분류 실험 보고서](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN21-FINAL-3TEAM/blob/main/ai/experiments_v2/FINAL_REPORT.md)

### 4. ALPLED — 생성 후 검사와 실패 경로

공개 그래프는 전처리→생성 Supervisor→내보내기→정리 흐름을 구성한다. 평가기는 결과 키와 검증 결과를 확인하고, 문제가 있으면 대상·범위를 정해 재계획한다. 우리 팀도 검토 에이전트가 단순한 “다시 해봐”가 아니라 실패한 항목과 수정 대상을 반환하도록 한다. [그래프](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN24-FINAL-3Team/blob/main/ALPLED-CORE/workflow/graph.py), [평가기](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN24-FINAL-3Team/blob/main/ALPLED-CORE/supervisor/evaluate/evaluator.py)

### 5. GameOps — 어디에서 실패했는지 나누어 보기

E2E 평가 코드에서 라우팅·행동 일치·예상 밖 fallback·워크플로 성공 등을 구분한다. CS 평가 문서도 라우팅 성능, DB 경로, 검색 근거 적중을 따로 보고하며 최종 답변 품질 전체와 구분한다. 우리 팀도 “답변이 별로였다”를 검색 실패인지 생성 실패인지 데이터 조회 실패인지 나누어 기록한다. [E2E 평가 코드](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN25-FINAL-6Team/blob/main/apps/chatbot/backend/evals/eval_e2e_workflow_dataset.py), [CS 평가 문서](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN25-FINAL-6Team/blob/main/docs/eval/cs_auto_eval_summary.md)

일부 결과 링크가 작성자의 로컬 Windows 경로를 가리킨다. 우리 팀의 평가 결과는 저장소 상대 경로나 공유 가능한 결과 저장소로 연결해야 다른 팀원이 확인할 수 있다.

### 6. Answervice — 모델 출력과 검증 증거를 분리하기

학습 문서는 검토된 데이터만 사용하고, SQL의 의존 관계를 모델 설명 그대로 신뢰하지 않고 서버에서 다시 계산하도록 명시한다. 미실행 상태를 실행 증거로 취급하지 않는 점도 좋다. 학습 코드는 베이스 모델 revision, 데이터, 학습 조건, 결과 manifest를 남기는 구조다. 우리 팀은 “문서가 존재함 / 코드가 존재함 / 실행됨 / 평가됨”을 구분하는 습관을 가져온다. [학습 데이터 운영 문서](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN29-FINAL-3TEAM/blob/main/src/ai/training/README.md), [학습 코드](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN29-FINAL-3TEAM/blob/main/src/ai/training/train_lora.py)

## 주제를 정할 때 추가로 볼 4개

| 후보 주제 | 가까운 사례 | 판단 기준 |
| --- | --- | --- |
| 문서 검토·수정 제안 | Workit, ALPLED | 실제 문서와 검토 기준을 첫 주에 확보 가능한가 |
| CS 초안·정책 근거 | GameOps | 정책 문서와 합성 업무 상태로 정답을 만들 수 있는가 |
| 정산 검토 | 법인카드 정산 | 금액·날짜·승인 규칙을 코드로 검증할 수 있는가 |
| 회의 후속 업무 | 말하는대로, HPM | STT를 기존 서비스로 처리하고 업무 추출·승인에 집중 가능한가 |

이번 조사의 결론은 특정 팀의 기술 스택을 그대로 복제하자는 것이 아니다. **업무 흐름은 HelixOps, 작은 학습 태스크는 HumouR, 평가와 증거 관리는 GameOps·Answervice에서 가져와 하나의 좁은 MVP로 결합**하는 것이 5명·약 6주 조건에 맞는다.

조직의 검색 결과: [FINAL 저장소 목록](https://github.com/SKNETWORKS-FAMILY-AICAMP?q=FINAL&type=all&language=&sort=). 조회 당시 읽은 파일의 SHA와 URL은 [조사 출처 기록](./sources.json)에 보관했다.
