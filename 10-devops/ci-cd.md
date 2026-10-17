# CI/CD — Jenkins

> **Decision:** Jenkins es la CI/CD oficial (ADR-019, cerró Q-006).
> Todo lo de este documento está implementado en `infra/jenkins/` y se activa con
> webhooks de GitHub. GitHub Actions (`infra/.github/workflows/build-services.yml`)
> se retira tras el primer deploy verde con Jenkins.

## Arquitectura en una frase

Jenkins corre como contenedor en el mismo VPS (`docker-compose.jenkins.yml`), recibe
un webhook de push por repositorio, ejecuta los tests, y si el push era sobre `main`
y los tests pasan, construye la imagen, la sube a GHCR y hace `docker compose pull/up`
del stack que ya sirve en esa misma máquina, cerrando con smoke test.

## Dónde vive qué

| Pieza | Ubicación |
|-------|-----------|
| Overlay de Jenkins (contenedor, sock, volumen) | `infra/docker-compose.jenkins.yml` |
| Imagen de Jenkins (docker CLI + compose + jq) | `infra/jenkins/Dockerfile` |
| Jobs (Job DSL: `test-*`, `deploy-*`, mapeo repo↔servicio) | `infra/jenkins/jobs.groovy` |
| Pipeline de tests | `infra/jenkins/Jenkinsfile.test` |
| Pipeline de deploy | `infra/jenkins/Jenkinsfile.deploy` |
| Seed (crea/actualiza los jobs) | `infra/jenkins/seed.Jenkinsfile` |
| Panel | `https://jenkins.eduaircontrol.tech` (Caddy) o túnel SSH a `localhost:8085` |

> Los jobs clonan este repo **desde `main`**: los cambios en `jenkins/**` solo
> surten efecto tras merge a `main` y un `Build Now` del job `seed` (si afecta a
> `jobs.groovy`).

## Pipelines

### `test-<servicio>` (8 jobs)

1. **Checkout** del commit exacto del push.
2. **Verify**: `./mvnw -B -ntp verify` (los 7 repos Java; `ms-environment-monitoring`
   y `ms-user-experience` usan Testcontainers contra el docker del host vía sock) o
   `npm ci && npm run build` para `web`.
3. **Deploy gate**: solo si `REF == refs/heads/main` y los tests pasaron →
   dispara `deploy-<servicio>` con los mismos `REPO_URL`/`COMMIT_SHA`.

### `deploy-<servicio>` (8 jobs, solo vía encadenado)

1. **Build** de la imagen `ghcr.io/eduaircontrol/ea-control-<servicio>` etiquetada
   `:<sha>` y `:latest` (el frontend se construye desde `apps/web` con
   `VITE_API_URL` del `.env` del VPS).
2. **Push a GHCR** con la credencial `ghcr-bot`.
3. **Deploy** en el VPS desde `/opt/eduaircontrol/infra`:
   `docker compose -f docker-compose.yml -f docker-compose.cloud.yml -f docker-compose.observability.yml pull <svc> && up -d --no-build <svc>`.
4. **Smoke**: `wait-for-services.sh` + `smoke.sh` en contenedor con `--network host`
   (los puertos publican en `127.0.0.1` del VPS, inalcanzables desde la red de
   Jenkins). Un fallo de smoke deja el job en rojo.

## Triggers

| Evento | Job | Resultado |
|--------|-----|-----------|
| Push a `develop` en cualquiera de los 8 repos | `test-<servicio>` | Feedback de tests |
| Push a `main` en cualquiera de los 8 repos | `test-<servicio>` → `deploy-<servicio>` | Test + **deploy automático** + smoke |
| «Build Now» a mano | cualquiera | Re-ejecución / deploy de un SHA concreto |

Webhook por repositorio (evento **push**, content type `application/json`):

```
https://jenkins.eduaircontrol.tech/generic-webhook-trigger/invoke?token=test-<servicio>
```

Tokens: `test-api-gateway`, `test-ms-security`, `test-ms-classroom-management`,
`test-ms-sensor-management`, `test-ms-user-management`,
`test-ms-environment-monitoring`, `test-ms-user-experience`, `test-web`.

## Credenciales Jenkins

| ID | Uso | Contenido |
|----|-----|-----------|
| `github-infra` | Los jobs clonan `ea-control-infra` | PAT bot con `read:repo` |
| `ghcr-bot` | Push de imágenes en `deploy-*` | Usuario + PAT con `write:packages` |

En el VPS, una sola vez para poder hacer `pull`:
`echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USER --password-stdin`
(con `REGISTRY=ghcr.io/eduaircontrol` y `TAG=latest` en `/opt/eduaircontrol/infra/.env`).

## Plugins mínimos

`git`, `workflow-aggregator` (Declarative), `docker-workflow`, `credentials-binding`,
`plain-credentials`, `generic-webhook-trigger`, `job-dsl`, `timestamper`.
Nada más: el panel está expuesto públicamente (ver README de infra para endurecer).

## Primer arranque (una vez)

1. Crear registro A `jenkins.eduaircontrol.tech` → IP del VPS.
2. Levantar: `docker compose -f docker-compose.yml -f docker-compose.cloud.yml -f docker-compose.observability.yml -f docker-compose.jenkins.yml up -d --build jenkins`.
3. Password inicial: `docker exec ea-control-jenkins cat /var/jenkins_home/secrets/initialAdminPassword` (o vía túnel SSH a `localhost:8085`); crear admin y cambiarla.
4. Instalar los plugins de la lista; crear las credenciales `github-infra` y `ghcr-bot`.
5. Crear el job `seed` («Pipeline script from SCM» → `ea-control-infra`, script
   `jenkins/seed.Jenkinsfile`) y lanzarlo.
6. Crear los 8 webhooks en GitHub con los tokens de arriba.
7. Merge a `main` de un servicio de prueba y verificar: test verde → imagen en GHCR →
   `pull/up` → smoke verde.

## Rollback

```bash
# En el VPS, desde /opt/eduaircontrol/infra (o desde el job "Build Now" con un SHA):
set -a && . ./.env && set +a
TAG=<sha-sano> docker compose -f docker-compose.yml -f docker-compose.cloud.yml \
  -f docker-compose.observability.yml up -d --no-build <servicio>
```

Cada deploy deja su imagen `:<sha>` en GHCR, así que volver a un SHA anterior no
requiere rebuild. Las migraciones de Liquibase son forward-only: si el problema es de
esquema, hace falta un changelog compensatorio (ver runbook §4.5).

## Entornos

- **Local**: sin Jenkins — `./up.sh` construye desde el código hermano
  (`REGISTRY=eduaircontrol`, `TAG=local`).
- **VPS (cloud test)**: imágenes de GHCR (`TAG=latest`) + deploy automático desde `main`.

## Correlaciones

- ADR-019 → decisión y alternativas.
- `09-microservices/` → los servicios que cada pipeline builda/despliega.
- `11-quality/testing-strategy.md` → qué corre dentro de `verify`.
- `13-operations/backup-and-recovery.md` → qué mirar tras el smoke.
- `infra/RUNBOOK-DESPLIEGUE.md` §4.3/§4.5 → flujo manual que Jenkins sustituye.
