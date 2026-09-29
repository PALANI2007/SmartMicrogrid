# Validation Framework

## SmartMicrogrid — Academic Prototype Validation Reference

> [!IMPORTANT]
> **This is an academic prototype validation framework.** No real external stakeholder responses have been collected for this academic project. The sample responses documented below are clearly labelled as demonstration data only.

---

## 1. Purpose

The validation framework for SmartMicrogrid serves two purposes:

1. **Academic validation design** — To demonstrate that the system has been designed with real-world usability evaluation in mind, following established UX research practices (Think-Aloud Testing + Likert-scale questionnaires).
2. **Technical implementation** — A working `POST /api/validation` endpoint that can receive, store, and aggregate questionnaire responses in the database, ready for real stakeholder use if the system were deployed.

---

## 2. Validation Methodology

The methodology follows **Think-Aloud Usability Testing** paired with a post-task structured questionnaire. Participants would include local grid operators, facility managers, healthcare administrators, and community leaders who manage rural microgrids in Tamil Nadu.

### Session Structure (40 minutes per participant)

| Phase | Duration | Activity |
|-------|----------|----------|
| Introduction | 5 min | Explain the tool's purpose and session format |
| Scenario 1 — Monitoring | 10 min | Ask the user to identify current battery SOC and afternoon solar forecast |
| Scenario 2 — Interaction | 10 min | Ask the user to add a "Water Pump" flexible load (09:00–15:00) and run the scheduler |
| Scenario 3 — Evaluation | 5 min | Ask the user to review a CONFLICT result and read the AI explanation |
| Debrief + Questionnaire | 10 min | Administer the 6-question questionnaire and record open-ended feedback |

---

## 3. The 6-Question Validation Questionnaire

All questions use a **5-point Likert scale**:

| Score | Label |
|-------|-------|
| 1 | Strongly Disagree / Very Difficult / Very Poor |
| 2 | Disagree / Difficult / Poor |
| 3 | Neutral / Moderate |
| 4 | Agree / Easy / Good |
| 5 | Strongly Agree / Very Easy / Excellent |

### Question Definitions

| Question Key | Question Text | What It Measures |
|-------------|---------------|-----------------|
| `q1_understandable` | How easy was it to understand the current state of the battery and solar generation? | UI readability and information clarity |
| `q2_explanation_clear` | Did the AI explanations help you understand why certain loads were delayed? | Explainability (XAI) quality |
| `q3_disruption` | How confident do you feel in relying on this system to manage critical loads like medical equipment? | Trust in essential load protection |
| `q4_easy_to_read` | Was the language switching (English/Tamil) seamless and accurately translated? | Localisation quality |
| `q5_language_useful` | Did you encounter any confusion when adding a new flexible load with specific time constraints? | Form UX and input validation clarity |
| `q6_confidence_clear` | Overall, how would you rate the usefulness of this dashboard for daily operations? | Overall utility / adoption likelihood |

---

## 4. How to Submit a Validation Response

### Via the Frontend

Navigate to the **Help & Guide** page → scroll to the Validation section → fill in the questionnaire form and click **Submit**.

### Via the API (curl / Postman)

```bash
curl -X POST http://localhost:8000/api/validation \
  -H "Content-Type: application/json" \
  -d '{
    "respondent_name": "Grid Operator A",
    "q1_understandable": 5,
    "q2_explanation_clear": 4,
    "q3_disruption": 4,
    "q4_easy_to_read": 5,
    "q5_language_useful": 5,
    "q6_confidence_clear": 4,
    "overall_satisfaction": 4.5,
    "notes": "The Tamil translation is accurate and natural."
  }'
```

**Response:**
```json
{"status": "success", "id": 1}
```

---

## 5. How to View Responses

### Via the API

```bash
curl http://localhost:8000/api/validation
```

**Response:**
```json
{
  "responses": [...],
  "averages": {
    "q1_avg": 4.6,
    "q2_avg": 4.2,
    "q3_avg": 4.0,
    "q4_avg": 4.8,
    "q5_avg": 4.4,
    "q6_avg": 4.3,
    "overall_avg": 4.4
  },
  "count": 5
}
```

---

## 6. Sample Demonstration Responses

> [!CAUTION]
> The responses below are **demonstration data only**. They were created to illustrate the format of validation responses and to test the API. They do **NOT** represent real user studies or actual stakeholder feedback collected for this project.

| Respondent | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Overall | Notes |
|------------|----|----|----|----|----|----|---------|-------|
| Demo Operator 1 | 5 | 4 | 5 | 5 | 4 | 5 | 4.7 | Dashboard is clear and intuitive |
| Demo Operator 2 | 4 | 4 | 4 | 5 | 3 | 4 | 4.0 | Tamil UI works well, time window form needs tooltip |
| Demo Manager 1 | 5 | 5 | 4 | 4 | 4 | 5 | 4.5 | AI explanation was very helpful for understanding conflicts |
| Demo User 1 | 4 | 3 | 4 | 5 | 5 | 4 | 4.2 | Would like an alert notification when battery is low |
| Demo User 2 | 5 | 4 | 5 | 5 | 4 | 5 | 4.7 | Excellent for managing irrigation schedules |

**Demo Averages:**

| Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Overall |
|----|----|----|----|----|----|----|
| 4.6 | 4.0 | 4.4 | 4.8 | 4.0 | 4.6 | 4.4 |

---

## 7. Interpretation of Scores

| Average Score | Interpretation | Recommended Action |
|--------------|----------------|-------------------|
| **> 4.0** | System is well-received and ready for field deployment | Proceed with pilot deployment |
| **3.0 – 4.0** | Functional, but requires UX/UI refinements in specific friction areas | Identify top 3 friction points and iterate |
| **< 3.0** | Critical usability or trust issues exist | Revisit core assumptions and redesign |

### Per-Question Thresholds

| Question | Threshold | If Below |
|----------|-----------|----------|
| Q1 (understandable) | ≥ 4.0 | Simplify dashboard layout, increase font size |
| Q2 (explanation clear) | ≥ 4.0 | Improve XAI explanation text in scheduler engine |
| Q3 (trust/confidence) | ≥ 4.0 | Add essential load protection indicators |
| Q4 (language) | ≥ 4.0 | Review Tamil translations with native speaker |
| Q5 (ease of use) | ≥ 3.5 | Add form tooltips and input examples |
| Q6 (overall utility) | ≥ 4.0 | Re-evaluate core feature set with users |

---

## 8. Important Disclaimer

> [!WARNING]
> **No real external stakeholder responses have been collected for this academic project.**
>
> This system was developed as a capstone academic prototype. The validation framework, questionnaire, and API are fully functional and ready for real user studies, but no IRB-approved user study was conducted. All sample data in Section 6 is synthetic demonstration data.
>
> Any scores or averages quoted in academic presentations represent the system's design intent, not measured user performance.

---

## 9. How This Would Be Used in a Real Deployment

If this system were deployed to an actual rural microgrid in Tamil Nadu, the validation process would follow these steps:

1. **Recruitment** — Identify 10–15 stakeholders (grid operators, facility managers, community leaders).
2. **IRB Approval** — Obtain institutional review board approval for human subject research.
3. **Training** — Conduct a 30-minute orientation session with each participant.
4. **Session** — Run the 40-minute Think-Aloud session as described in Section 2.
5. **Data Collection** — Submit questionnaire responses via `POST /api/validation`.
6. **Analysis** — Retrieve aggregated averages via `GET /api/validation`.
7. **Iteration** — Use qualitative feedback to prioritise UI improvements.
8. **Follow-up** — Conduct a second round of sessions 4 weeks later to measure improvement.

The `validation_responses` database table is designed to scale to hundreds of responses without any schema changes. Future versions could add demographic fields (role, location, experience level) and longitudinal tracking (pre/post training scores).
