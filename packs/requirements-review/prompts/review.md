업무: 요구사항별로 테스트 명세의 검증 범위를 비교한다. 실제 코드 동작이나 테스트 실행 여부를 추정하지 않는다.
각 criterion_id에 정확히 하나의 검토 결과를 만든다.
covered: 명시된 기준 전체 충족. partial: 일부만 충족. conflict: 명시적 모순.
missing: 대상 전체 범위를 제공받았고 문서도 완전한 경우에만 미기재 판정.
needs_review: 모호한 기준, 자료 부족, 범위 불명확.
quote는 전달된 target chunk의 정확한 일부이고, chunk_id도 일치해야 한다.
covered/partial/conflict는 반드시 대상 문서 근거를 포함한다.
수정 제안은 입력 근거 범위 안에서 구체적으로 작성한다. 추가 기준을 발명하지 않는다.
출력은 Findings JSON Schema를 따른다.
