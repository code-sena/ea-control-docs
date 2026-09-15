# Diagram Index

> Registry of all system diagrams. Diagrams go in `08-uml/diagrams/source/`
> as PlantUML or Mermaid files.

---

## Diagram registry

### Architecture diagrams (C4)

| ID | Name | Type | Tool | Source file | Description |
|----|------|------|------|-------------|-------------|
| C4-01 | System Context | C4 L1 | PlantUML | `source/c1-system-context.puml` | EduAirControl and external actors |
| C4-02 | Container Diagram | C4 L2 | PlantUML | `source/c2-container-diagram.puml` | All services and databases |

### Sequence diagrams

| ID | Name | Tool | Source file | Description |
|----|------|------|-------------|-------------|
| SEQ-01 | User Registration | PlantUML | `source/seq-registration.puml` | Registration → Validation → Storage |
| SEQ-02 | User Login | PlantUML | `source/seq-login.puml` | Login → JWT → Token response |

### ER diagrams (data)

| ID | Name | Tool | Source file | Service |
|----|------|------|-------------|---------|
| ERD-01 | IAM DB | Mermaid | `source/erd-iam.mmd` | ms-iam |
| ERD-02 | Environmental Monitoring DB | Mermaid | `source/erd-environment-monitoring.mmd` | ms-environment-monitoring |

---

## Tools

| Tool | For what | How to use |
|------|---------|------------|
| PlantUML | C4, sequence, state, class diagrams | `plantuml -tsvg file.puml` |
| Mermaid | Simple diagrams in Markdown | Native support on GitHub |

---

## Correlations

- Architecture view → `05-architecture/overview.md`
- Domain bounded contexts → `02-domain/domain-map.md`
- ER models per service → `06-data/domain/`
