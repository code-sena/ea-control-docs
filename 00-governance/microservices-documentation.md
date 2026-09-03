# Per-Microservice Documentation Standard — EduAirControl

> Adaptación del `microservices-governance-framework` al estado real de EduAirControl, tomando como evidencia el frontend React/Vite y el backend Spring Boot entregados.

## 1. Propósito

Este documento define cómo debe documentarse cada servicio de EduAirControl, qué información debe contener, cómo se relaciona con los contratos API, datos, dependencias y operación, y cómo debe registrarse una futura extracción hacia microservicios.

El estándar de referencia organiza la documentación de microservicios en `09-microservices` y relaciona los cambios de arquitectura, datos y API con los servicios afectados.

## 2. Estado arquitectónico actual

**EduAirControl no está implementado actualmente como varios microservicios backend independientes.**

El backend entregado corresponde a un **monolito modular Spring Boot**, con los módulos de autenticación y seguridad dentro de un único proceso.

```text
Frontend React/Vite
        |
        | HTTP
        v
Backend Spring Boot
        |
        +-- auth
        |
        +-- security
        |
        v
   PostgreSQL
```

### Tecnologías comprobadas

- Java / Spring Boot
- Spring Security
- Spring Data JPA
- PostgreSQL
- JWT
- OAuth2 con Google
- OpenAPI / Swagger
- Liquibase presente en los recursos del proyecto

Por tanto, nombres como `auth-service`, `environment-service`, `sensor-service`, `ranking-service` y `notification-service` representan **candidatos de futura extracción**, no microservicios ya desplegados.

## 3. Frontend y punto de integración

El frontend está desarrollado con React/Vite y contiene módulos funcionales de:

- autenticación;
- dashboard;
- ambientes;
- favoritos;
- ranking;
- notificaciones;
- perfil;
- configuración.

La configuración del frontend utiliza:

```text
VITE_API_URL=http://localhost:8080
```

Por ello, `http://localhost:8080` es actualmente el punto de integración configurado entre frontend y backend.

El frontend contiene servicios como `environmentService` y `rankingService`, pero su presencia no significa que existan microservicios backend independientes para esos dominios.

## 4. Estructura documental futura

Cada microservicio deberá documentarse bajo:

```text
09-microservices/
└── services/
    └── NN-service-name/
        ├── README.md
        ├── data-model.md
        ├── events.md
        ├── decisions.md
        └── runbook.md
```

Si expone REST, deberá existir además un contrato OpenAPI:

```text
07-api/
└── contracts/
    └── openapi/
        └── service-name.yaml
```

| Documento | Requisito |
|---|---|
| `README.md` | Obligatorio |
| `data-model.md` | Si posee persistencia |
| `events.md` | Si publica o consume eventos |
| `decisions.md` | Para decisiones técnicas relevantes |
| `runbook.md` | Antes de staging |
| OpenAPI | Si expone REST |

## 5. Backend actual

### Responsabilidad

El backend actual proporciona la API de EduAirControl y concentra principalmente autenticación y seguridad.

### Estructura comprobada

```text
com.eduaircontrol.backend/
├── config/
│   ├── OpenApiConfig
│   ├── SecurityBean
│   └── SecurityConfig
└── modules/
    ├── auth/
    │   ├── controller/
    │   ├── dto/
    │   ├── entity/
    │   ├── repository/
    │   └── service/
    └── security/
        ├── JwtAuthFilter
        ├── JwtService
        └── OAuth2AuthenticationSuccessHandler
```

## 6. Módulo de autenticación

El módulo `auth` administra usuarios y autenticación.

### Endpoints comprobados

```text
POST /auth/register
POST /auth/login
```

### Registro

`RegisterRequest` recibe:

```text
name
email
password
```

El servicio verifica el correo, cifra la contraseña mediante BCrypt, asigna el rol `USER`, persiste el usuario y genera un JWT.

### Login

`LoginRequest` recibe:

```text
email
password
```

El servicio valida las credenciales y genera un JWT.

### Recuperación de contraseña

El frontend contiene componentes para recuperación, cambio y verificación de código. Sin embargo, en el backend entregado existen DTO como `ForgotPasswordRequest` y `VerifyCodeRequest`, pero el `AuthController` comprobado actualmente solo expone `register` y `login`.

Por tanto, la recuperación de contraseña debe considerarse **interfaz/estructura preparada, pero no endpoint backend comprobado**, hasta que exista el controlador correspondiente.

### OAuth2

El backend contiene:

```text
OAuth2AuthenticationSuccessHandler
```

y lógica de usuario Google. La configuración utiliza:

```text
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
FRONTEND_OAUTH2_SUCCESS_URL
```

## 7. Módulo de seguridad

Los componentes comprobados son:

```text
JwtService
JwtAuthFilter
OAuth2AuthenticationSuccessHandler
```

El JWT se transmite mediante:

```text
Authorization: Bearer <token>
```

La configuración contempla los roles:

```text
USER
ADMIN
```

Las propiedades del JWT incluyen:

```text
JWT_SECRET
JWT_EXPIRATION
```

El `SecurityConfig` permite públicamente, entre otros:

```text
/
/auth/login
/auth/register
/oauth2/**
/login/**
/v3/api-docs/**
/swagger-ui/**
/swagger-ui.html
```

El resto de solicitudes requiere autenticación.

## 8. Persistencia actual

La entidad comprobada es `Users`, mapeada a:

```text
users
```

Campos principales:

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `name` | Nombre |
| `email` | Correo único |
| `password` | Contraseña cifrada |
| `google_id` | Identificador Google |
| `role` | Rol del usuario |

La conexión configurada es:

```text
jdbc:postgresql://postgres:5432/eduaircontrol
```

El backend utiliza actualmente:

```text
spring.jpa.hibernate.ddl-auto=update
```

También existe estructura de Liquibase en:

```text
src/main/resources/liquibase/
```

Antes de producción debe definirse una política clara sobre la evolución del esquema para evitar ambigüedad entre Hibernate y Liquibase.

## 9. OpenAPI / Swagger

OpenAPI está configurado mediante `OpenApiConfig`.

La documentación debe mantenerse sincronizada con los controladores reales.

Endpoints comprobados:

```text
POST /auth/register
POST /auth/login
```

La seguridad de la API utiliza Bearer JWT para endpoints protegidos.

Los recursos de Swagger/OpenAPI están permitidos para documentación:

```text
/v3/api-docs/**
/swagger-ui/**
/swagger-ui.html
```

## 10. Candidatos de futura extracción

| Servicio futuro | Responsabilidad | Estado |
|---|---|---|
| `auth-service` | usuarios, JWT y OAuth2 | Candidato |
| `environment-service` | ambientes educativos | Candidato |
| `sensor-service` | dispositivos y lecturas | Candidato |
| `ranking-service` | reglas y consultas de ranking | Candidato |
| `notification-service` | alertas y notificaciones | Candidato |
| `api-gateway` | entrada y enrutamiento | Candidato |

Estos nombres representan la posible evolución del sistema, no la arquitectura backend actualmente desplegada.

## 11. Criterio para extraer un microservicio

La extracción debe hacerse solamente cuando exista:

- responsabilidad de negocio claramente delimitada;
- ownership de datos;
- contrato API definido;
- dependencias identificadas;
- pruebas;
- estrategia de migración;
- necesidad real de despliegue independiente;
- observabilidad y rollback;
- documentación propia.

Crear una carpeta o clase con el nombre de un servicio no constituye por sí mismo un microservicio.

## 12. Ownership de datos futuro

Regla:

> Cada servicio será propietario de los datos de su dominio. Otros servicios no deben escribir directamente en sus tablas.

Propuesta:

| Datos | Propietario futuro |
|---|---|
| Usuarios y credenciales | `auth-service` |
| Ambientes | `environment-service` |
| Lecturas | `sensor-service` |
| Ranking | `ranking-service` |
| Alertas | `notification-service` |

En el monolito actual estos límites todavía no están separados físicamente.

## 13. Comunicación futura

La primera alternativa será REST/HTTP mediante contratos OpenAPI:

```text
React/Vite
    |
    v
API Gateway
    |
    +-- auth-service
    +-- environment-service
    +-- sensor-service
    +-- ranking-service
    +-- notification-service
```

Los eventos solamente deberán documentarse cuando exista una implementación real de mensajería.

No se debe afirmar que Kafka, RabbitMQ u otro broker está implementado si el código no lo demuestra.

## 14. Eventos futuros

Actualmente no existen eventos de dominio implementados en el backend entregado.

Cuando se implementen, `events.md` deberá registrar:

- nombre;
- productor;
- consumidores;
- transporte;
- payload;
- versión;
- compatibilidad.

Ejemplos de nombres candidatos:

```text
UserRegistered
EnvironmentMeasurementReceived
EnvironmentStatusChanged
AlertCreated
```

Estos nombres son propuestas.

## 15. Runbook

Antes de staging, cada servicio deberá documentar:

1. health check;
2. ejecución local;
3. variables de entorno;
4. errores frecuentes;
5. diagnóstico;
6. recuperación;
7. rollback;
8. migraciones;
9. métricas;
10. alertas.

Nunca deben documentarse valores reales de secretos.

Variables actuales relevantes del backend:

```text
JWT_SECRET
JWT_EXPIRATION
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
FRONTEND_OAUTH2_SUCCESS_URL
CORS_ALLOWED_ORIGINS
```

## 16. Definition of Done documental

- [ ] Existe `README.md`.
- [ ] Responsabilidad y límites están definidos.
- [ ] Ownership de datos está definido.
- [ ] Existe `data-model.md` si aplica.
- [ ] Existe `events.md` si aplica.
- [ ] Las decisiones relevantes están documentadas.
- [ ] Existe OpenAPI si expone REST.
- [ ] Existe `runbook.md` antes de staging.
- [ ] El servicio aparece en el catálogo.
- [ ] El mapa de dependencias está actualizado.
- [ ] La documentación fue revisada mediante Pull Request.

## 17. Cuándo actualizar esta documentación

Debe revisarse cuando cambie:

- arquitectura;
- módulos;
- endpoints;
- contratos OpenAPI;
- modelo de datos;
- migraciones;
- dependencias;
- eventos;
- fronteras entre servicios;
- despliegue.

Los cambios de arquitectura deben reflejarse en los servicios afectados; los cambios de datos, en el servicio propietario; y los cambios de contratos API, en sus consumidores y proveedor.


