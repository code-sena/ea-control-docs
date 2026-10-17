# 10 — DevOps

> **What is this?** How code goes from the developer's computer to production,
> and how it is maintained in each environment. CI/CD, environments, and local configuration.

## Why this section exists

Without documented DevOps:
- Each developer has their own deploy process (and fails differently)
- "It works on my machine" is the most expensive answer in software
- Releases are high-risk events instead of routine

---

## What is here and how to fill it in

### `local-setup.md` ⭐ (Most urgent)
How to start THE ENTIRE SYSTEM on a new computer from scratch.
**Fill in:** step by step, omitting nothing, assuming the reader has never touched the project.
Include: software prerequisites, environment variables, exact commands, how to verify it works.

**Format:**
```markdown
## Prerequisites
- [ ] Docker Desktop >= 24.0
- [ ] [Language/Runtime] >= [version]
- [ ] [Tool] >= [version]

## Steps
1. Clone the main repository: `git clone [url]`
2. Copy environment variables: `cp .env.example .env`
3. Start infrastructure: `docker-compose up -d`
4. Wait for services to be ready: `./scripts/wait-for-services.sh`
5. Verify: `curl http://localhost:8080/health`

## Local ports
| Service | Port |
|---------|------|
| API Gateway | 8080 |
| [Service 1] | 8001 |
| RabbitMQ UI | 15672 |
| Adminer (DB) | 8090 |

## Common issues
- **Port in use:** `lsof -i :8080` to see what is using it
- **DB not connecting:** verify Docker is running
```

### `environments.md` ⭐
Description of all project environments.
**Fill in:** local, development, staging, production. For each: purpose, URL, who has access,
how it is deployed, what data it has.

**Format:**
```markdown
| Environment | URL | Purpose | Access | DB | Deploy |
|-------------|-----|---------|--------|-----|--------|
| local | localhost | Individual development | All | Test data | Manual |
| dev | dev.api.domain.com | Continuous integration | Team | Test data | Automatic (push to dev) |
| staging | staging.api.domain.com | QA / validation | Team + PO | Anonymized data | Manual (approval) |
| prod | api.domain.com | Production | Ops team | Real data | Manual (double approval) |
```

### `ci-cd.md` ⭐

Filled (2026-10-17): **Jenkins is the official CI/CD** (ADR-019, closes Q-006).
The document covers where each piece lives (`infra/jenkins/`), the `test-<service>`
and `deploy-<service>` pipelines, triggers (push to `develop` = tests; push to
`main` = tests + **auto-deploy** to GHCR + VPS + smoke), webhook tokens,
credentials, required plugins, first boot, rollback and environments.

---

## Correlations with other sections

| This section is fed by... | And feeds into... |
|---------------------------|-------------------|
| `05-architecture/deployment.md` → how it is deployed | Pipeline implementation |
| `11-quality/testing-strategy.md` → which tests to run | Pipeline steps |
| `09-microservices/` → each service to deploy | Which images the pipeline builds |
| `13-operations/` → post-deploy monitoring | What the pipeline verifies |

---

## Questions this section must answer

- How do I start the system locally in 30 minutes?
- What happens automatically when I push?
- How does code get to production?
- How many environments are there and what is each one for?
