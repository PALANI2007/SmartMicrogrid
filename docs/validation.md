# User Validation Methodology

## Validation Methodology
To ensure the Renewable-Aware Load Scheduler meets the practical needs of rural microgrid operators, we employ a **Think-Aloud Usability Testing** approach paired with a post-test questionnaire. Participants include local grid operators, facility managers, and community leaders.

## Questionnaire Questions (6 Questions)
1. How easy was it to understand the current state of the battery and solar generation?
2. Did the AI explanations help you understand why certain loads were delayed?
3. How confident do you feel in relying on this system to manage critical loads like medical equipment?
4. Was the language switching (English/Tamil) seamless and accurately translated?
5. Did you encounter any confusion when adding a new flexible load with specific time constraints?
6. Overall, how would you rate the usefulness of this dashboard for daily operations?

## Scoring Rubric
Questions are scored on a 5-point Likert Scale:
1 - Strongly Disagree (or Very Difficult / Very Poor)
2 - Disagree
3 - Neutral
4 - Agree
5 - Strongly Agree (or Very Easy / Excellent)

## Sample Validation Session Procedure
1. **Introduction (5 mins):** Explain the purpose of the tool and the format of the session.
2. **Scenario 1 - Monitoring (10 mins):** Ask the user to identify the current battery SOC and forecast for the afternoon.
3. **Scenario 2 - Interaction (10 mins):** Ask the user to add a new "Water Pump" load that must run between 09:00 and 15:00.
4. **Scenario 3 - Evaluation (5 mins):** Ask the user to review a scheduled conflict and read the provided AI explanation.
5. **Debrief (10 mins):** Administer the 6-question questionnaire and record open-ended feedback.

## How to Interpret Scores
- **Average Score > 4.0:** System is well-received and ready for field deployment.
- **Average Score 3.0 - 4.0:** Functional, but requires UX/UI refinements in specific friction areas.
- **Average Score < 3.0:** Critical usability or trust issues exist. Core assumptions need revisiting.

## Recommended Iteration Process
1. Aggregate questionnaire scores and transcribe qualitative feedback.
2. Identify the top 3 most common user friction points.
3. Rapidly prototype solutions (e.g., clearer wording, larger buttons).
4. Conduct follow-up validation sessions with a subset of the original group.
