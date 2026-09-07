# Team Ownership and Delivery Plan

## Responsibility matrix

| Member | Primary ownership | First deliverables | Review partners |
|---|---|---|---|
| 1. Lead/integration | Architecture, contracts, GitHub, releases, demo flow | Repository rules, issue board, API/domain contract, integration checklist | All members |
| 2. ML/fare | Dataset features, training, evaluation, model artifact | Baseline notebook, comparison report, inference schema | 3 and 4 |
| 3. Data/GIS | Hyderabad locations, zones, route data, provenance | Location seed, data dictionary, routing adapter fixtures | 2 and 6 |
| 4. Backend/database | FastAPI, Pydantic, migrations, persistence, auth | SQL migration, trip/fare endpoints, error handling | 1 and 2 |
| 5. Frontend/UI | Planner, comparison, map, summary, dashboard | Responsive screens using API contracts and demo state | 1 and 4 |
| 6. Optimization/testing | Graph model, configurable scoring, anomaly rules, tests | Optimizer, explainability fields, route/API regression tests | 2 and 4 |

## File ownership boundaries

- Member 1 owns `docs/`, root configuration, CI, and release notes.
- Member 2 owns `ml/`, `notebooks/`, and fare inference code under `backend/app/ml`.
- Member 3 owns `data/`, `database/seeds/`, and `backend/app/integrations/routing`.
- Member 4 owns `backend/app/api`, `backend/app/db`, `backend/app/core`, and migrations.
- Member 5 owns `frontend/`.
- Member 6 owns `backend/app/optimization`, anomaly services, and `tests/`.

Changes across boundaries require a small contract update and reviewer from the owning member.

## Integration sequence

1. Lead merges the Phase 1 contracts and creates issues from them.
2. Data/GIS supplies stable location and mode IDs before backend persistence work depends on them.
3. Backend creates migrations and read APIs against those IDs.
4. ML publishes a versioned prediction contract and a reproducible demo artifact.
5. Optimization consumes route and fare contracts, then publishes ranked route output with score components.
6. Frontend integrates against mocked JSON first, then the live API.
7. Lead runs the end-to-end demo script and release checklist.

## Branch and pull request rules

- Branch from `develop` using `feature/<member>-<short-name>`.
- One focused PR per deliverable; no cross-member drive-by formatting.
- PR description includes contract impact, test command, data provenance impact, and screenshots for UI changes.
- At least one reviewer outside the author owns the affected contract.
- Merge order follows the integration sequence.

## Week-by-week plan

### Week 1: contracts and data inventory

Deliver: accepted architecture, SQL schema, API schemas, data dictionary, issue board, Hyderabad location inventory, routing provider decision.

Exit: all six members can run the repository checks; no unresolved ownership or provenance question blocks implementation.

### Week 2: database and data foundation

Deliver: Docker PostgreSQL/PostGIS, migrations, seed locations/modes, sample CSV, validation script, and source attribution records.

Exit: a clean database can be recreated from zero and location/mode lookups return stable IDs.

### Week 3: fare baseline

Deliver: preprocessing pipeline, baseline Linear Regression, Random Forest and XGBoost experiment harness, metrics report, and first Joblib artifact if data supports it.

Exit: the team can reproduce metrics and explain limitations; no metric is written without an experiment output.

### Week 4: FastAPI trip and fare flow

Deliver: health check, locations, modes, trip creation, fare prediction, persistence, validation, and API tests.

Exit: a scripted request can create a trip and return a labelled fare range.

### Week 5: routing and optimization

Deliver: routing adapter, demo fallback fixture, route graph, preference profiles, constraints, ranked multimodal plans, and route tests.

Exit: the Hyderabad demo scenario returns at least the required auto, cab, bus, and metro-plus-auto candidates or a truthful no-route response.

### Week 6: anomaly, explainability, and frontend integration

Deliver: fare check, neutral anomaly language, comparison screen, planner, recommendation explanation, and trip summary.

Exit: the two-minute demo flow works from planner input through quoted fare alert.

### Week 7: map, dashboard, and dynamic context

Deliver: interactive map, admin aggregate views, simulated traffic context labelled in the UI, and re-optimization request.

Exit: traffic changes can alter ranking without pretending to be live data.

### Week 8: hardening and SIH rehearsal

Deliver: Docker Compose, security review, test suite, accessibility pass, README runbook, presentation, demo script, and failure-mode rehearsal.

Exit: a fresh machine can run the stack using documented commands and the team can explain problem, gap, AI/ML, optimization, innovation, feasibility, and measurable impact without fabricated claims.

## Definition of done for the MVP

- A new user can plan the Hyderabad demo trip.
- Fare output is a range with provenance and model/rule explanation.
- At least four candidate route patterns are compared when data permits.
- Preference changes affect weights or constraints and can change the recommendation.
- Quoted fare checking uses neutral decision-support language.
- The system exposes route score components and alternative comparisons.
- Invalid input and no-route cases have tested, readable responses.
- Demo/synthetic context is labelled everywhere it appears.
