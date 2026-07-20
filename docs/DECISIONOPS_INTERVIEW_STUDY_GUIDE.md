# DecisionOps Lab 면접·학습 가이드

이 문서는 DecisionOps Lab 전체를 빠르게 복습하고, 데이터 분석·제품 분석·분석 엔지니어링·실험 분석 면접에서 프로젝트를 일관되게 설명하기 위한 요약본입니다.

> 핵심 질문: **원시 이벤트 데이터를 어떻게 신뢰 가능한 지표와 실험 근거, 최종 의사결정으로 연결할 것인가?**

---

## 1. 30초 프로젝트 소개

DecisionOps Lab은 synthetic product event 데이터를 SQL 모델, metric layer, data quality check, A/B test, guardrail review, decision memo로 연결한 제품 분석·분석 엔지니어링 프로젝트입니다.

단순히 Variant B의 activation lift만 보는 것이 아니라, 먼저 데이터 품질을 확인하고 D7 revisit, refund rate, average sessions 같은 guardrail까지 검토한 뒤 Ship, Retest, Hold, Investigate 중 하나를 결정합니다.

DuckDB와 plain SQL로 staging, intermediate, mart 계층을 만들고, Python으로 품질 검사·통계 검정·시나리오 분석·리포트 생성을 자동화했습니다.

## 2. 1분 면접 답변

많은 포트폴리오 분석은 notebook에서 결과를 계산한 뒤 끝나지만, 실제 데이터 팀에서는 원시 이벤트가 신뢰 가능한지, 지표 정의가 재사용 가능한지, 실험 결과가 downstream behavior를 해치지 않는지, 최종 권고가 어떤 근거에서 나왔는지를 함께 관리해야 합니다.

DecisionOps Lab에서는 루틴·학습 습관 앱의 onboarding experiment를 가정했습니다. 핵심 지표는 가입 후 24시간 이내 첫 routine 생성 비율인 activation rate입니다. Raw events를 DuckDB에 적재하고 staging과 intermediate 모델을 거쳐 experiment, segment, retention cohort, decision summary mart를 만들었습니다.

분석 전에는 row count, null, accepted values, referential integrity, duplicate, experiment balance 등을 검사합니다. 데이터 품질이 통과하면 activation lift와 p-value·confidence interval을 보고, D7 revisit, refund rate, average sessions guardrail을 확인합니다. Strong positive에서는 Ship이지만 activation이 올라도 guardrail이 악화되면 Retest, 품질이 깨지면 Investigate로 분리합니다.

이 프로젝트의 핵심은 특정 실험 결과가 아니라 **raw data → trustworthy metric → evidence → recommendation**을 재현 가능한 workflow로 만든 것입니다.

---

## 3. 문제 정의

### 데이터 팀의 문제

실험 결과를 의사결정에 사용하려면 다음 질문에 답해야 합니다.

- 원시 이벤트가 분석 가능한 상태인가?
- 사용자·세션·실험 배정 관계가 깨지지 않았는가?
- activation의 분모와 분자는 무엇인가?
- 통계적으로 양의 lift가 있는가?
- 단기 activation 개선이 retention·monetization·engagement를 해치지 않는가?
- 같은 규칙이 다른 결과 상황에서도 일관되게 작동하는가?
- 최종 결론이 원시 계산이 아니라 추적 가능한 mart와 artifact에 기반하는가?

### 프로젝트 질문

> 데이터 분석가가 데이터 품질 확인, metric definition, experiment analysis, guardrail review, decision memo까지 하나의 재현 가능한 workflow로 만들 수 있는가?

---

## 4. 전체 흐름

```text
synthetic raw product events
→ DuckDB raw tables
→ SQL staging models
→ intermediate analysis models
→ mart layer
→ data quality report
→ experiment analysis
→ multi-guardrail review
→ decision memo
→ reviewer report
→ scenario matrix
→ automated verification
```

### 핵심 산출물

| 산출물 | 역할 |
| --- | --- |
| Synthetic dataset | 고정 seed와 scenario mode로 재현 가능한 이벤트 생성 |
| SQL models | raw, staging, intermediate, mart 계층 |
| Metric layer | activation, retention, monetization, engagement 정의 |
| Quality report | PASS / WARN / FAIL 품질 검사 |
| Experiment result | A/B 비교, lift, 검정, CI, segment, guardrail |
| Scenario matrix | 7개 상황의 Ship / Retest / Hold / Investigate |
| Decision memo | 최종 권고와 근거 |
| Reviewer report | 빠르게 검토 가능한 HTML summary |

---

## 5. Product scenario와 event model

Synthetic product는 루틴·학습 습관 앱입니다.

```text
signup
→ onboarding_start
→ onboarding_complete
→ create_routine
→ complete_routine
→ return_visit
→ trial_start
→ paid_conversion
→ refund
```

### 실험 질문

> Variant B가 신규 사용자의 가입 후 24시간 이내 첫 routine 생성 비율을 높이는가?

### Primary metric

```text
activation_rate
= 24시간 이내 첫 routine을 생성한 사용자 수
  / 실험 대상 신규 사용자 수
```

Activation은 onboarding change의 직접 목표와 가까워 primary metric으로 사용합니다.

---

## 6. SQL 모델링 계층

### Raw

생성된 CSV를 DuckDB raw table로 적재합니다. 이 계층은 원천 구조를 최대한 보존합니다.

### Staging

- 컬럼명과 타입을 정리합니다.
- timestamp와 category 값을 표준화합니다.
- downstream model이 원천 CSV 형식에 직접 의존하지 않도록 합니다.

### Intermediate

- 사용자별 signup과 experiment assignment를 연결합니다.
- activation window, revisit, session, trial, payment, refund를 계산하기 위한 분석 단위를 만듭니다.
- raw event에서 반복되는 복잡한 조건을 한 번만 모델링합니다.

### Mart

리포트와 분석 script가 raw 또는 intermediate table을 직접 조회하지 않도록 최종 재사용 계층을 제공합니다.

```text
model once
reuse many times
```

---

## 7. Mart tables와 grain

| Mart | Grain | 목적 |
| --- | --- | --- |
| `mart_experiment_result` | scenario·experiment·variant당 1행 | activation, retention, monetization, engagement 요약 |
| `mart_segment_performance` | scenario·segment dimension·value·variant당 1행 | acquisition channel, device, age group 진단 |
| `mart_retention_cohort` | signup week당 1행 | D1·D3·D7 revisit cohort |
| `mart_decision_summary` | scenario·experiment당 1행 | 최종 권고에 필요한 핵심 지표 압축 |

### 왜 grain이 중요한가

- 같은 지표를 중복 계산하는 것을 줄입니다.
- join으로 row가 증폭되는 오류를 방지합니다.
- 면접에서 “이 테이블 한 행이 무엇을 의미하는가?”를 명확히 답할 수 있습니다.
- reviewer artifact가 어떤 분석 단위에 기반하는지 추적할 수 있습니다.

---

## 8. Data quality gate

실험 해석 전에 데이터 품질을 먼저 확인합니다.

### 주요 검사 범주

- row count와 empty table
- required column null
- accepted values
- 사용자·세션·이벤트 referential integrity
- duplicate event 또는 duplicate assignment
- experiment variant balance
- timestamp 순서와 이벤트 시간 범위
- mart 생성 결과와 예상 grain

### 왜 품질 실패를 `Investigate`로 분리했는가

데이터가 깨진 상태에서 lift와 p-value를 계산해도 비즈니스 근거가 될 수 없습니다. 품질 실패는 treatment가 나쁘다는 뜻이 아니라 **분석 증거를 사용할 수 없다는 뜻**이므로 Hold와 구분해 Investigate로 처리합니다.

---

## 9. 실험 분석

### 핵심 비교

- Variant A activation rate
- Variant B activation rate
- absolute lift
- relative lift
- p-value
- confidence interval
- segment diagnostics

### 기본 공개 시나리오 결과

| 항목 | 결과 |
| --- | ---: |
| Variant A activation | 30.15% |
| Variant B activation | 34.12% |
| Absolute lift | +3.97 percentage points |
| p-value | 0.000011 |
| Guardrails | D7 revisit·refund·session 모두 PASS |
| Decision | Ship |

이 숫자는 synthetic scenario의 결과이며 실제 제품 성과를 뜻하지 않습니다.

### 왜 absolute lift와 relative lift를 둘 다 보는가

- Absolute lift는 실제 percentage point 차이를 보여줍니다.
- Relative lift는 baseline 대비 변화 크기를 보여줍니다.
- 상대 변화만 제시하면 효과가 과장될 수 있어 두 수치를 함께 봅니다.

---

## 10. Guardrail 설계

Primary metric이 좋아져도 downstream behavior가 나빠질 수 있습니다.

| Guardrail | 확인 질문 | WARN 기준 |
| --- | --- | --- |
| D7 revisit rate | 빠른 activation이 이후 재방문을 해치는가? | Variant B delta < -1%p |
| Refund rate | conversion quality가 나빠지는가? | Variant B delta > +1%p |
| Average sessions | 전체 engagement가 줄어드는가? | Variant B가 5% 초과 감소 |

### 왜 이 세 지표인가

- D7 revisit: 단기 행동 이후의 유지
- Refund rate: 수익 증가처럼 보여도 부적합 전환이 늘어나는지
- Average sessions: onboarding 최적화가 전체 사용성을 낮추는지

Guardrail은 primary metric을 대체하지 않고 **Ship 결정을 제한하는 안전 조건**입니다.

---

## 11. Decision rule

```text
IF data quality fails:
    Investigate
ELSE IF activation lift > 0
        AND p-value < 0.05
        AND all guardrails pass:
    Ship
ELSE IF activation lift > 0:
    Retest
ELSE:
    Hold
```

| 조건 | 권고 |
| --- | --- |
| Data quality FAIL | Investigate |
| Strong positive + 모든 guardrail PASS | Ship |
| Positive지만 evidence 약함 | Retest |
| Positive지만 guardrail WARN | Retest |
| Primary metric 개선 없음 | Hold |

이 규칙은 universal business policy가 아니라 의사결정 workflow를 보여주기 위한 portfolio-level rule입니다.

---

## 12. Scenario matrix

같은 pipeline이 하나의 좋은 결과에만 맞춰져 있지 않은지 확인하기 위해 7개 synthetic scenario를 실행합니다.

| Scenario | Quality | Guardrail | Decision | 핵심 의미 |
| --- | --- | --- | --- | --- |
| `strong_positive` | PASS | PASS | Ship | 충분한 lift와 안정적 guardrail |
| `guardrail_risk` | PASS | WARN | Retest | activation은 개선되지만 D7 약화 |
| `refund_risk` | PASS | WARN | Retest | refund 악화 |
| `session_activity_risk` | PASS | WARN | Retest | session 감소 |
| `weak_evidence` | PASS | PASS | Retest | 양의 lift지만 근거 약함 |
| `neutral` | PASS | PASS | Hold | activation 개선 없음 |
| `quality_failure` | FAIL | PASS | Investigate | 해석 전 품질 실패 |

### Scenario matrix의 가치

- decision rule이 단일 결과에 hard-code되지 않았는지 확인합니다.
- metric과 guardrail의 역할을 비교할 수 있습니다.
- 경계 상황에서 Ship이 남발되지 않는지 보여줍니다.
- regression test처럼 recommendation behavior를 검증합니다.

---

## 13. Segment와 cohort 분석

### Segment dimensions

- acquisition_channel
- device_type
- age_group

Segment 분석은 전체 평균에서 숨겨지는 treatment heterogeneity를 확인하기 위한 진단입니다.

### 주의할 점

- segment 수가 많아질수록 표본이 작아집니다.
- 여러 segment에서 반복 검정을 하면 false positive가 늘 수 있습니다.
- segment 결과를 사후적으로 골라 primary conclusion처럼 사용하지 않습니다.

### Retention cohort

signup week 기준으로 D1, D3, D7 revisit를 요약합니다. Experiment guardrail과 별개로 시간에 따른 사용자 재방문 구조를 확인할 수 있습니다.

---

## 14. 자동화와 freshness verification

### Full workflow

```bash
python scripts/run_full_verification.py
python scripts/check_report_freshness.py
```

### Step-by-step

```bash
python scripts/generate_dataset.py
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
python scripts/generate_review_report.py
python scripts/run_scenario_matrix.py
python -m pytest
python scripts/check_report_freshness.py
```

### Report freshness check

Tracked report와 현재 pipeline 재생성 결과를 비교합니다. `generated_at`처럼 변동이 불가피한 timestamp만 정규화하고, metric·guardrail·decision·memo·HTML 내용이 바뀌면 실패합니다.

이 검사는 코드가 변경됐는데 오래된 좋은 숫자가 report에 남는 문제를 방지합니다.

---

## 15. 핵심 설계 선택과 이유

### 15.1 왜 DuckDB인가

- 로컬에서 SQL workflow를 쉽게 재현할 수 있습니다.
- 별도 warehouse 운영 없이 raw→mart 계층을 보여줄 수 있습니다.
- SQL과 Python artifact 생성의 연결이 단순합니다.

### 15.2 왜 notebook보다 scripts와 SQL을 중심으로 했는가

- 실행 순서를 자동화할 수 있습니다.
- 동일한 scenario를 반복 실행할 수 있습니다.
- CI와 freshness check에 연결할 수 있습니다.
- reviewer가 계산과 artifact lineage를 추적하기 쉽습니다.

### 15.3 왜 primary metric 하나로 결정하지 않았는가

단기 목표를 과도하게 최적화하면 retention, refund, engagement가 악화될 수 있습니다. 따라서 primary metric은 개선 방향을, guardrail은 Ship 가능 여부를 결정합니다.

### 15.4 왜 synthetic data인가

실제 product event 데이터 없이도 metric contract, quality gate, experiment workflow와 decision logic을 공개 재현하기 위해서입니다. 대신 실제 business impact나 user behavior는 주장하지 않습니다.

---

## 16. 반드시 말해야 하는 한계

- 모든 데이터는 synthetic입니다.
- 실제 제품 성과, 실제 사용자 행동, 실제 매출 영향을 주장하지 않습니다.
- p-value threshold와 guardrail threshold는 단순한 portfolio-level rule입니다.
- 실험 배정·노출·sample ratio mismatch의 production 복잡성을 모두 구현한 것은 아닙니다.
- 장기 retention과 novelty effect를 충분히 관측하지 않습니다.
- multiple testing과 sequential testing 정책은 단순화되어 있습니다.
- DuckDB schema는 portfolio review용이며 production warehouse 설계가 아닙니다.
- Ship은 실제 배포 명령이 아니라 evidence상 권고입니다.

---

## 17. 개선한다면

### Experiment design

- 사전 power analysis와 minimum detectable effect를 추가합니다.
- exposure logging과 assignment logging을 분리합니다.
- sample ratio mismatch test를 강화합니다.
- sequential testing과 peeking policy를 명시합니다.

### Metric layer

- metric definition을 YAML·semantic layer 형태로 관리합니다.
- denominator eligibility와 observation window contract를 자동 검사합니다.
- late-arriving event와 timezone 처리 규칙을 추가합니다.

### Guardrail

- threshold를 고정값이 아니라 historical baseline·business tolerance와 연결합니다.
- 각 guardrail의 confidence interval을 함께 제공합니다.
- 장기 retention과 support cost 같은 추가 downstream metric을 검토합니다.

### Engineering

- dbt 또는 orchestration tool로 lineage와 dependency를 명시합니다.
- incremental model과 partition 전략을 추가합니다.
- artifact schema contract와 data diff를 강화합니다.

---

## 18. 예상 면접 질문과 답변 핵심

### Q1. 이 프로젝트가 일반적인 A/B test notebook과 다른 점은 무엇인가요?

Raw data 모델링, data quality gate, mart, guardrail, decision memo, scenario matrix, artifact freshness까지 하나의 workflow로 만들었다는 점입니다.

### Q2. Activation을 어떻게 정의했나요?

실험 대상 신규 사용자 중 signup 후 24시간 이내 첫 routine을 생성한 사용자의 비율입니다. 분모·분자·시간창을 고정해야 재현 가능한 metric이 됩니다.

### Q3. 데이터 품질 실패와 Hold를 왜 분리했나요?

Hold는 믿을 수 있는 데이터에서 개선이 없다는 결론이고, Investigate는 데이터가 깨져 결론 자체를 내릴 수 없다는 상태입니다.

### Q4. 왜 p-value만으로 Ship하지 않았나요?

통계적 유의성은 효과 크기나 downstream risk를 보장하지 않습니다. Absolute lift, CI, guardrail을 함께 봅니다.

### Q5. 왜 D7 revisit가 guardrail인가요?

Onboarding이 첫 행동을 빠르게 만들면서 이후 재방문을 악화할 수 있기 때문입니다.

### Q6. Refund rate는 왜 필요한가요?

전환이 늘어도 제품과 맞지 않는 사용자가 유입되면 refund가 증가할 수 있어 monetization quality를 확인합니다.

### Q7. Mart layer를 둔 이유는 무엇인가요?

분석과 리포트가 raw event와 복잡한 transform에 직접 의존하지 않도록 재사용 가능한 분석 계약을 만들기 위해서입니다.

### Q8. Mart grain을 잘못 설계하면 어떤 문제가 생기나요?

Join duplication, 분모 왜곡, metric double-counting이 생길 수 있습니다. 각 mart의 한 행 의미를 명시했습니다.

### Q9. Scenario matrix는 왜 필요한가요?

좋은 결과 하나에 decision logic이 맞춰져 있지 않은지 확인하고, 품질·근거·guardrail 조합별 권고를 regression test처럼 검증하기 위해서입니다.

### Q10. Synthetic data의 장단점은 무엇인가요?

장점은 공개 재현성과 edge case 생성입니다. 단점은 실제 사용자 행동과 business constraint를 대표하지 못한다는 점입니다.

### Q11. `strong_positive` 결과를 실제 성과처럼 말할 수 있나요?

아닙니다. 해당 숫자는 workflow가 생성한 synthetic evidence입니다. 주장 범위는 분석 구조와 의사결정 설계입니다.

### Q12. 가장 중요한 engineering 요소는 무엇인가요?

SQL 계층화와 report freshness check입니다. 코드와 최종 문서가 서로 다른 결과를 말하지 않도록 합니다.

### Q13. Multiple testing 문제는 어떻게 다뤘나요?

현재는 segment를 진단용으로 제한합니다. Production이라면 사전 가설, correction, hierarchical analysis 정책이 필요합니다.

### Q14. Guardrail threshold는 어떻게 정했나요?

현재는 workflow를 설명하기 위한 단순 threshold입니다. 실제 환경에서는 historical variance, business tolerance, power를 기반으로 정해야 합니다.

### Q15. 다시 만든다면 무엇을 먼저 추가하겠나요?

Power/MDE, SRM 검사, exposure contract, late event 처리와 metric semantic layer를 먼저 추가하겠습니다.

---

## 19. 핵심 파일 읽는 순서

### 1단계 · 프로젝트와 의사결정

1. `README.md`
2. `docs/PORTFOLIO_PITCH.md`
3. `docs/DECISION_RULES.md`
4. `reports/decision_memo.md`
5. `reports/scenario_matrix.md`

### 2단계 · SQL과 mart

1. `docs/MART_LAYER.md`
2. `sql/staging/`
3. `sql/intermediate/`
4. `sql/marts/`
5. `sql/metrics/`

### 3단계 · 실행 scripts

1. `scripts/generate_dataset.py`
2. `scripts/run_pipeline.py`
3. `scripts/run_quality_checks.py`
4. `scripts/run_experiment_analysis.py`
5. `scripts/run_scenario_matrix.py`

### 4단계 · artifact와 검증

1. `reports/quality_report.json`
2. `reports/experiment_result.json`
3. `scripts/generate_decision_memo.py`
4. `scripts/generate_review_report.py`
5. `scripts/check_report_freshness.py`
6. `.github/workflows/verify.yml`

---

## 20. 3회독 학습법

### 1회독 · Workflow만 익히기

```text
raw → staging → intermediate → mart
→ quality → experiment → guardrail → decision
```

세부 SQL은 보지 않고 각 계층의 목적만 파악합니다.

### 2회독 · Metric과 grain 보기

- activation의 분모·분자·시간창
- experiment mart 한 행의 의미
- segment mart와 cohort mart의 차이
- D7, refund, session 계산 단위

### 3회독 · 의사결정과 한계 말하기

- 왜 품질이 먼저인가?
- 왜 유의한 lift만으로 부족한가?
- 왜 guardrail WARN은 Retest인가?
- 왜 synthetic result를 실제 성과로 말할 수 없는가?
- 왜 freshness check가 필요한가?

---

## 21. 면접 직전 체크리스트

- [ ] 30초 소개를 자연스럽게 말할 수 있다.
- [ ] Activation metric의 분모·분자·24시간 window를 설명할 수 있다.
- [ ] Raw / staging / intermediate / mart 차이를 말할 수 있다.
- [ ] 네 mart의 grain을 대략 설명할 수 있다.
- [ ] Quality FAIL이 Investigate인 이유를 말할 수 있다.
- [ ] 세 guardrail과 WARN 기준을 말할 수 있다.
- [ ] Ship / Retest / Hold / Investigate 규칙을 설명할 수 있다.
- [ ] Scenario matrix의 목적을 말할 수 있다.
- [ ] p-value와 effect size 차이를 설명할 수 있다.
- [ ] Synthetic data의 claim boundary를 명확히 말할 수 있다.
- [ ] Report freshness check가 막는 문제를 설명할 수 있다.

---

## 22. 최종 안전 문장

> DecisionOps Lab은 synthetic product event 데이터를 DuckDB SQL 계층과 mart로 모델링하고, 품질 검사와 activation experiment, D7 revisit·refund·session guardrail을 거쳐 Ship·Retest·Hold·Investigate 의사결정으로 연결한 재현 가능한 분석 workflow입니다. 공개 수치는 실제 제품 성과가 아니라 synthetic scenario 결과이며, 프로젝트의 주장은 metric definition, quality gate, experiment interpretation과 decision artifact 설계에 있습니다.
