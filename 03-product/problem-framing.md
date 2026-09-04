# Problem Framing — Problem Definition

> **Why this document exists:** Before designing solutions, the team must be
> aligned on the problem it solves. This document captures that alignment.
> A well-defined problem is already halfway to a solution.

---

## 1. The problem in one sentence

> Complete this template:

> **Users of educational environments** who **need to monitor and understand environmental conditions over time** struggle with **having centralized and accessible information about temperature, humidity, CO₂, and noise levels**, because **environmental information is not sufficiently centralized and analyzed in a single platform**, resulting in **difficulty understanding environmental conditions and their changes over time**.


---

## 2. Affected users

| Segment | Description | Estimated size | Priority |
|---------|-------------|---------------|---------|
| Educational environment users | Users who access the platform to consult environmental conditions and historical environmental information | Not defined | High |
| Administrators | Users responsible for managing access and educational environment information | Not defined | High |

### Jobs-to-be-done (JTBD)

> What job is the user trying to do when they "hire" our product?

**When** I need to understand the environmental conditions of an educational environment,

**I want** to consult temperature, humidity, CO₂, and noise information and analyze it over different time periods,

**so that** I can better understand the environmental conditions and their changes over time.

---

## 3. Evidence of the problem

> The problem must be real. Document the evidence you have.

| Evidence type | Source | Date | Key finding |
|--------------|--------|------|------------|
| User interviews | Not defined | Not defined | Not defined |
| Support data | Not defined | Not defined | Not defined |
| Benchmarking | Not defined | Not defined | Not defined |
| Direct observation | Not defined | Not defined | Not defined |

---

## 4. Current user solution (and its problems)

> How does the user solve the problem today?

| Current solution | Limitations | Cost/Friction |
|-----------------|------------|--------------|
| Not defined | Environmental information may not be centralized in a single platform | Not defined |
| Not defined | Not defined | Not defined |

---

## 5. Solution hypothesis

> This is the first draft of the solution direction. It is not a commitment.

**We believe that** a platform that centralizes the monitoring and analysis of environmental conditions in educational environments, including temperature, humidity, CO₂, and noise level information,

**for** users who need to consult and understand environmental conditions,

**will achieve** easier access to environmental information and better understanding of changes over time.

**We will know we succeeded when** users can access the environmental dashboard and analyze environmental information by day, week, month, and year.

---

## 6. Success metrics (North Star)

| Metric | Current baseline | 6-month target | How to measure it |
|--------|----------------|---------------|-------------------|
| Environmental data analysis availability | Not defined | Not defined | Not defined |
| Dashboard adoption | Not defined | Not defined | Not defined |
| Historical analysis by period | Not defined | Not defined | Not defined |

**North Star Metric:** **Not defined**

---

## 7. Hypothesis risks

| Risk | Probability | Impact | Experiment to validate |
|------|-------------|--------|----------------------|
| Users will not adopt the environmental dashboard | Not defined | High | Pilot the dashboard with representative users and collect usage feedback |
| The available environmental data may not be sufficient for meaningful analysis | Not defined | High | Validate the availability and completeness of environmental data |
| The defined environmental variables may not fully satisfy user needs | Not defined | Medium | Validate the usefulness of temperature, humidity, CO₂, and noise information with users |
| Historical analysis may not provide sufficient value to users | Not defined | Medium | Test the day/week/month/year analysis views with representative users |

---

## 8. Out of scope (we do not solve)

> Explicitly define which related problems you are NOT solving in this version.
>
> This prevents scope creep.

- **Environmental Ranking:** The current version does not provide ranking of educational environments. The project focuses on monitoring and analyzing environmental information.

- **Advanced predictive environmental analysis:** Predictive or advanced forecasting capabilities are not part of the current MVP scope.

- **Automated control of environmental equipment:** The system does not automatically control air conditioning, ventilation, lighting, or other environmental equipment.

- **External environmental control systems:** Integration with external systems for automated environmental control is not part of the current scope.

- **External environmental sensor hardware:** The project software does not cover the physical implementation or management of environmental sensor hardware.

- **Advanced external infrastructure services:** External infrastructure services outside the currently defined technology stack are not part of the current scope.

---

## Correlations

- Product vision → `03-product/vision.md`

- HUs that implement this solution → `04-requirements/user-stories.md`

- Detailed KPIs → `13-operations/README.md`
