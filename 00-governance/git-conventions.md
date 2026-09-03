# Git Conventions — EduAirControl

> Convenciones de Git adaptadas del `microservices-governance-framework` a la implementación real de EduAirControl.

## 1. Objetivo

Definir una estrategia uniforme para ramas, commits, Pull Requests, integración y releases de frontend, backend, documentación e infraestructura.

## 2. Estrategia de ramas

```text
main
  |
  +-- dev
       |
       +-- feat/[description]
       +-- fix/[description]
       +-- chore/[description]
       +-- hotfix/[description]
```

### `main`

Rama estable.

- No se realizan commits directos.
- Recibe releases mediante Pull Request.
- Debe permanecer estable.
- Las versiones se identifican mediante tags.

### `dev`

Rama de integración.

- No se realizan commits directos.
- Recibe Pull Requests de ramas de trabajo.
- Debe mantenerse integrable.

## 3. Ramas de trabajo

| Tipo | Uso |
|---|---|
| `feat/` | Nueva funcionalidad |
| `fix/` | Corrección de errores |
| `chore/` | Mantenimiento, dependencias o configuración |
| `hotfix/` | Corrección urgente de producción |
| `docs/` | Documentación |
| `test/` | Pruebas |
| `refactor/` | Refactorización |

Reglas:

- minúsculas;
- `kebab-case`;
- sin espacios;
- una tarea por rama.

Ejemplos para EduAirControl:

```text
feat/oauth2-login
feat/environment-management
feat/ranking-filters
fix/jwt-authentication
fix/environment-status
chore/update-spring-dependencies
chore/update-frontend-dependencies
docs/microservices-documentation
docs/git-conventions
test/auth-login
refactor/auth-module
hotfix/jwt-expiration
```

## 4. Regla fundamental

```text
Una tarea = una rama = un Pull Request
```

No se deben mezclar funcionalidades independientes en una misma rama o Pull Request.

## 5. Conventional Commits

Formato:

```text
type(scope): lowercase imperative description
```

Tipos permitidos:

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección |
| `docs` | Documentación |
| `style` | Formato sin cambio de lógica |
| `refactor` | Refactorización |
| `test` | Pruebas |
| `chore` | Mantenimiento y configuración |
| `perf` | Rendimiento |

La descripción debe:

- comenzar en minúscula;
- ser breve;
- utilizar modo imperativo;
- no terminar con punto.

## 6. Scopes recomendados

### Backend

```text
auth
security
api
config
database
```

### Frontend

```text
auth
environment
ranking
notifications
profile
settings
favorites
dashboard
landing
```

### Transversales

```text
docs
deps
ci
```

Ejemplos:

```text
feat(auth): implement google oauth2 login
feat(auth): add jwt authentication
fix(security): reject invalid bearer token
feat(environment): add environment management
feat(ranking): add ranking filters
fix(environment): correct environment status
docs(microservices): document service boundaries
docs(git): define branch and commit conventions
test(auth): add login service tests
chore(deps): update spring dependencies
```

## 7. Commits pequeños

Cada commit debe representar una unidad lógica.

Correcto:

```text
feat(auth): add google oauth2 callback
test(auth): cover google user creation
docs(auth): document oauth2 flow
```

Evitar:

```text
update project
cambios
arreglos
final
ultima version
cosas
```

## 8. Body del commit

Cuando sea necesario explicar el motivo del cambio:

```text
refactor(auth): centralize jwt generation

Move token generation to JwtService so register and login
share the same authentication behavior.
```

El body debe explicar principalmente por qué se tomó la decisión.

## 9. Pull Requests

Todo cambio destinado a `dev` o `main` debe realizarse mediante Pull Request.

### Requisitos

- [ ] La rama corresponde a una única tarea.
- [ ] Los commits siguen Conventional Commits.
- [ ] El proyecto compila.
- [ ] Las pruebas disponibles pasan.
- [ ] No existen secretos.
- [ ] La documentación afectada está actualizada.
- [ ] CI está en verde.
- [ ] Existe mínimo una aprobación.
- [ ] La descripción explica el cambio.

## 10. Tamaño del Pull Request

Se recomienda mantener los Pull Requests pequeños y revisables. El Governance Framework utiliza como referencia un máximo recomendado de aproximadamente **400 líneas de código**, excluyendo tests.

Cuando sea posible, dividir cambios grandes:

```text
PR 1 → contrato/modelo
PR 2 → backend
PR 3 → frontend
PR 4 → pruebas/documentación
```

## 11. Revisión

Cada Pull Request requiere al menos:

```text
1 aprobación
```

La revisión debe considerar:

- comportamiento;
- seguridad;
- calidad;
- pruebas;
- compatibilidad;
- documentación;
- impacto arquitectónico.

## 12. CI

No se debe hacer merge mientras los checks obligatorios estén fallando.

Validaciones recomendadas:

```text
Frontend
 ├── install
 ├── lint
 ├── tests
 └── build

Backend
 ├── compile
 ├── tests
 └── security checks
```

Si una validación todavía no está automatizada, no debe afirmarse que ya forma parte del CI.

## 13. Política de merge

Para features y correcciones hacia `dev`:

```text
Squash and Merge
```

Para releases hacia `main`:

```text
Merge Commit
```

Esta estrategia sigue las convenciones del Governance Framework.

## 14. Versionado

Se utilizará Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Ejemplos:

```text
v1.0.0
v1.1.0
v1.1.1
```

- `MAJOR`: cambios incompatibles.
- `MINOR`: nuevas funcionalidades compatibles.
- `PATCH`: correcciones compatibles.

Crear un tag:

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

## 15. Flujo de nueva funcionalidad

```bash
git checkout dev
git pull origin dev

git checkout -b feat/environment-management
```

Después del desarrollo:

```bash
git status
git add .
git commit -m "feat(environment): implement environment management"
git push -u origin feat/environment-management
```

Después:

1. Crear Pull Request hacia `dev`.
2. Solicitar revisión.
3. Resolver observaciones.
4. Verificar CI.
5. Obtener aprobación.
6. Hacer Squash and Merge.
7. Eliminar la rama.

## 16. Flujo de corrección

```bash
git checkout dev
git pull origin dev
git checkout -b fix/jwt-authentication
```

Ejemplo:

```bash
git commit -m "fix(security): reject invalid jwt tokens"
```

Después se utiliza el flujo normal de Pull Request.

## 17. Hotfix

Para problemas críticos de producción:

```text
hotfix/[description]
```

Flujo:

```text
main
  |
  +-- hotfix/jwt-expiration
          |
          +-- PR → main
          |
          +-- PR → dev
```

El cambio debe llegar a producción y posteriormente a desarrollo para evitar regresiones.

## 18. Archivos sensibles

El frontend contiene un `.env` y su configuración ignora archivos sensibles como:

```text
.env
node_modules/
```

El backend utiliza variables como:

```text
JWT_SECRET
JWT_EXPIRATION
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
FRONTEND_OAUTH2_SUCCESS_URL
CORS_ALLOWED_ORIGINS
```

Nunca se deben subir:

- contraseñas;
- JWT secrets reales;
- OAuth secrets;
- tokens;
- claves privadas;
- credenciales de producción.

Se recomienda utilizar:

```text
.env.example
```

para documentar los nombres de las variables sin incluir secretos.

## 19. Configuración actual del proyecto

El frontend utiliza:

```text
VITE_API_URL=http://localhost:8080
```

El backend utiliza PostgreSQL y configuración externa para JWT y OAuth2.

Los valores de desarrollo no deben convertirse automáticamente en configuración de producción.

Además, el backend actualmente contiene valores por defecto de desarrollo para PostgreSQL y JWT. Estos valores no deben utilizarse como secretos de producción.

## 20. Cambios que requieren actualizar documentación

| Cambio | Documentación a revisar |
|---|---|
| Arquitectura | ADR + microservices |
| Nueva entidad | Data + API + servicio |
| Nuevo endpoint | OpenAPI + servicio |
| Cambio de endpoint | OpenAPI + consumidores |
| Nueva dependencia | documentación del servicio |
| Nuevo microservicio | catálogo + mapa + OpenAPI |
| Cambio de datos | migraciones + ownership |
| Nuevo evento | event catalog + servicio |
| Cambio de autenticación | API + seguridad |
| Cambio de despliegue | DevOps + runbook |

## 21. Checklist antes del commit

```text
¿Pertenece a esta tarea?
¿La rama tiene el tipo correcto?
¿El commit explica el cambio?
¿Está en Conventional Commits?
¿Hay secretos?
¿Las pruebas pasan?
¿La documentación necesita actualizarse?
```

## 22. Checklist antes del Pull Request

```text
¿La rama está actualizada?
¿El cambio es revisable?
¿CI está en verde?
¿La documentación está actualizada?
¿El PR tiene una única finalidad?
```

## 23. Resumen operativo

```text
main       → estable
 dev       → integración
feat/*     → funcionalidades
fix/*      → errores
chore/*    → mantenimiento
hotfix/*   → urgencias

Conventional Commits
        ↓
Pull Request
        ↓
1 aprobación mínima
        ↓
CI verde
        ↓
Squash → dev
Merge Commit → main
        ↓
SemVer tag
```

