1. Overview

The Unified Platform is a multi‑tenant, module‑driven runtime that powers three primary skins:

• University Skin
• Legacy Game Studios Skin
• Space‑LEAF / Space Car Skin


All skins share the same core engine, including identity, permissions, vault, routing, safety, and telemetry.

---

2. Core Architecture

2.1 Identity Service

• Unified user accounts
• Role‑based access control (RBAC)
• Tenant‑scoped permissions


2.2 Vault & Storage

• Asset storage (immutable, versioned)
• Build artifacts
• Course/game/mission data
• Access rules enforced by RBAC


2.3 Routing Layer

• Module router
• Context switching (classroom → game pod → mission)
• Tenant isolation


2.4 Safety & Compliance (Guardian Core)

• Content scanning
• Policy engine
• Runtime enforcement
• Audit logging


2.5 Telemetry

• Event ingestion
• Performance metrics
• Safety flags
• Tenant dashboards


---

3. Tenant Model

A tenant defines a world‑type and its vocabulary.

3.1 University Tenant

• Entities: classrooms, courses, labs
• Modules: LMS tools, simulations


3.2 Legacy Game Studios Tenant

• Entities: studios, game pods, catalogs
• Modules: game runtimes, build pipelines, moderation tools


3.3 Space‑LEAF / Space Car Tenant

• Entities: missions, vehicles, environments
• Modules: simulators, planners, cockpit UIs


---

4. Module System

4.1 Module Contract

• Inputs: identity, role, tenant, context
• Capabilities: vault access, telemetry, safety checks
• UI: embedded, fullscreen, or API‑only


4.2 Module Types

• Internal modules
• Third‑party modules
• Sandboxed modules


---

5. External Studio / Third‑Party Integration

5.1 Onboarding

• Studio registration
• API key / OAuth client issuance


5.2 Submission Pipeline

• Build upload
• Metadata ingestion
• Automated safety checks
• Human review for flagged items


5.3 Runtime Sandbox

• Isolated execution
• Guardian‑enforced policies
• Kill‑switch + quarantine


---

6. Unified Data Model

6.1 Core Entities

• User
• Tenant
• Module
• Asset
• Build
• Event


6.2 Cross‑Tenant Consistency

• Shared identity
• Shared safety rules
• Tenant‑specific vocabulary


---

7. Skin Layer

7.1 Skin Definition

A skin is a UI + vocabulary + policy pack applied on top of the core.

7.2 Skin Components

• Navigation
• Theming
• Terminology mapping
• Tenant‑specific modules


---

8. Deployment Model

8.1 Services

• Identity
• Vault
• Router
• Guardian
• Telemetry


8.2 Scaling

• Per‑tenant isolation
• Horizontal module scaling


---

9. Security Model

9.1 Access Control

• RBAC
• Tenant boundaries
• Module sandboxing


9.2 Data Protection

• Encryption at rest
• Encryption in transit


9.3 Compliance

• Kid‑safe rules
• Audit trails


---

10. Roadmap (Skeleton)

• v0.1 — Core services
• v0.2 — Module runtime
• v0.3 — University skin
• v0.4 — Legacy Game Studios skin
• v0.5 — Space‑LEAF skin
• v1.0 — Unified public release


---
