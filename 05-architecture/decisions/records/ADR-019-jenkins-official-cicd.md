# ADR-019 — Jenkins as the Official CI/CD (GHCR, auto-deploy on main)

- **ID:** ADR-019
- **Date:** 2026-10-17
- **Status:** Accepted
- **Authors:** DevOps team
- **Closes:** Q-006

---

## Context

ADR-010 and ADR-011 constrain the stack to «Integration with Jenkins CI/CD», and
`01-context/overview.md` lists «Docker + Jenkins + GitHub» as the infrastructure — but
the only pipeline that ever existed was GitHub Actions
(`infra/.github/workflows/build-services.yml`), which tested six Java services, did not
cover `ms-user-experience` or the frontend, and never deployed: **deployment was and is
manual** (rsync sources to the VPS, `docker compose build`/`up`, verify with Portainer
and `smoke.sh`; rollback by hand, §4.3/§4.5 of the runbook).

**Known constraints:**
- One Hostinger KVM 2 VPS (8 GB RAM, Docker 29) also serves the stack (Compose +
  Caddy + Portainer + observability).
- Team of three, minimal MVP cost; no dedicated build machines.
- `docker-compose.yml` is already parameterized with `REGISTRY`/`TAG`
  (`image: ${REGISTRY}/ea-control-<svc>:${TAG}`), i.e. ready for pre-built images.
- The real release branch is `main` (features flow `feat/*` → `develop` → `main`).

## Decision

**We decided:** **Jenkins LTS is the official CI/CD** (closes Q-006), running as a
container on the same VPS (`infra/docker-compose.jenkins.yml`), with pipelines as code
in this repo (`infra/jenkins/`: Job DSL `jobs.groovy` + `Jenkinsfile.test` +
`Jenkinsfile.deploy`), activated by one GitHub webhook per repository:

1. **`test-<service>`** — on every push to `develop` or `main` (8 repos: the six Java
   services + `api-gateway` + the `web` frontend): checkout at the pushed SHA and run
   `./mvnw verify` (or `npm ci && npm run build` for the web app).
2. **`deploy-<service>`** — chained automatically by `test-<service>` **only when the
   tests ran on `main` and passed**: build the image (`:<sha>` + `:latest`) → push to
   **GHCR** → on the VPS `docker compose pull/up <service>` → wait + smoke.
3. The GitHub Actions workflow is **deleted after the first green deploy** (GitHub
   Actions stops being a source of truth; Q-006 answered in favour of Jenkins).

**Justification:** Jenkins was already the declared tool (ADR-010/011); running it on
the VPS costs nothing extra and gives the deploy pipeline direct access to the stack;
GHCR artifacts make deploys immutable, fast (no Maven on the serving host) and
k8s-ready, while the smoke gate keeps the automatic deploy honest.

## Evaluated alternatives

| Alternative | Pros | Cons | Reason for discarding |
|------------|------|------|-----------------------|
| **Jenkins on the VPS + GHCR artifacts (chosen)** | Zero extra cost; declared tool honoured; deploys are `pull` + `up` (seconds); images immutable and reusable by k8s | Jenkins shares the 8 GB VPS with the stack; holds the host docker socket | — (chosen) |
| Keep GitHub Actions + manual deploy | Already green; no new components | Violates ADR-010/011 constraint (Q-006 stays open); deploy stays manual; matrix incomplete | Deploy was exactly what had to be automated |
| Jenkins building from source on the VPS | No registry needed | Maven builds on the production host; non-immutable images; slower, non-reproducible deploys | Artifacts beat in-deploy builds |
| Jenkins on a local/CI machine | Isolated build resources | Deploys only when that machine is on; SSH keys elsewhere | Team needs on-demand delivery |

## Consequences

- `main` becomes a true **release branch**: every push to `main` is tested and, if
  green, deployed automatically to the VPS; `develop` only gets test feedback.
- GHCR (`ghcr.io/eduaircontrol/ea-control-<svc>`) is the image source for Compose on
  the VPS (`REGISTRY`/`TAG` in `.env`); images are tagged `:latest` and `:<sha>`
  (rollback = set `TAG=<sha>` and `up -d --no-build <service>`).
- CI configuration lives in this repo (`infra/jenkins/**`) and is read from **`main`**,
  so pipeline changes only take effect once released to `main`.
- Jenkins has the host docker socket (root-equivalent on the VPS): panel is only
  bound to `127.0.0.1` and exposed via Caddy `jenkins.eduaircontrol.tech` with
  Jenkins' own auth + CSRF; plugins limited to the documented list.
- Build concurrency is capped at 1 job (8 GB VPS also runs the stack).
- `build-services.yml` (GitHub Actions) is removed after the first green Jenkins
  deploy; its matrix gaps (`ms-user-experience`, frontend) are covered by Jenkins.
- Rollback and the job/webhook/credential runbook live in
  `10-devops/ci-cd.md`; the deploy steps of `infra/RUNBOOK-DESPLIEGUE.md` are
  superseded by «deploy through Jenkins».

## Related

- ADR-010 (containerization), ADR-011 (deployment strategy — requires Jenkins),
  ADR-012 (observability consumed by the smoke stage), `10-devops/ci-cd.md`.
