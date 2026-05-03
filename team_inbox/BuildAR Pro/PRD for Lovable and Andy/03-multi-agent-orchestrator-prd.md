# Multi‑Agent Orchestrator & Lyra OS PRD (For Lovable & Claude Agents)

## 1. Purpose and Audience

This PRD defines the **multi‑agent orchestration layer ("Lyra OS")** that coordinates LLM calls, tools, and internal agents for BuildAR.

Audience:
- AI agents (Lovable, Claude) implementing backend orchestration services and tool integrations.
- Human maintainers responsible for AI behavior, safety, and performance.

This layer converts user intents and project context into **structured plans**, routes subtasks to specialized agents (BOM, safety, vision, tutor), and returns responses to clients.

---

## 2. Goals and Non‑Goals

### 2.1 Goals

1. Provide a **single orchestration entrypoint** for client apps to request plans, assistance, and evaluations.
2. Implement a **Lyra‑style 4‑D methodology** (Deconstruct, Diagnose, Develop, Deliver) in code.
3. Standardize **tool and agent interfaces** so Lovable/Claude can safely add new agents.
4. Capture **structured logs** of decisions for debugging and optimization.

### 2.2 Non‑Goals

- Designing or training custom models (use external LLMs/CV services).
- Full agent identity/DID implementation (deferred; design for future integration).

---

## 3. Architecture Overview

### 3.1 Logical Components

1. **Orchestrator API** (HTTP endpoint): entrypoint from mobile/web.
2. **Lyra Controller**: implements 4‑D methodology.
3. **Agent Registry**: metadata about available agents (name, capabilities, tool contracts).
4. **Specialized Agents** (initial set):
   - `BOMPlannerAgent` – material & tools reasoning.
   - `SafetyCheckerAgent` – safety warnings and gating.
   - `TutorAgent` – Q&A and explanations.
   - `VisionInspectorAgent` – placeholder stubs for CV integration.
5. **LLM Client**: abstraction over Claude API.
6. **Event Logger**: writes orchestrator events into `events` table.

### 3.2 Data Flow (High‑Level)

1. Client calls `POST /api/v1/orchestrator/plan` with payload (session, project, step, user message).
2. Orchestrator validates input and loads context from DB.
3. Lyra Controller runs 4‑D pipeline:
   - **Deconstruct** – parse intent and relevant entities.
   - **Diagnose** – decide which agents/tools are needed.
   - **Develop** – call agents/LLM with structured prompts.
   - **Deliver** – synthesize and return response payload.
4. Orchestrator logs decisions and outputs to `events`.

---

## 4. API Contract

### 4.1 Endpoint

`POST /api/v1/orchestrator/plan`

**Request body (MVP):**

```ts
export interface OrchestratorRequest {
  sessionId: string;
  projectId: string;
  currentStepIndex: number;
  userMessage: string;       // optional for auto‑planning; required for Q&A
  mode: 'assist' | 'plan';   // 'assist' = Q&A; 'plan' = generate/adjust plan
}
```

**Response body (MVP):**

```ts
export interface OrchestratorResponse {
  messages: Array<{
    role: 'assistant' | 'system';
    content: string;
  }>;
  hints?: string[];          // bullet hints for UI
  warnings?: string[];       // safety warnings
  metadata?: Record<string, any>;
}
```

Behavior:
- `mode='assist'`: treat `userMessage` as a question; orchestrator calls `TutorAgent` plus optional `SafetyCheckerAgent`.
- `mode='plan'`: orchestrator may adjust or generate step‑level suggestions (used later for authoring, not MVP UI).

---

## 5. Lyra 4‑D Methodology in Code

Implement the Lyra 4‑D methodology as a pure‑function pipeline.

### 5.1 Deconstruct

Inputs:
- Raw `OrchestratorRequest`.
- Loaded context: session, project, current step, BOM snippet.

Outputs:
- `LyraContext` object with:
  - `intent` ("qna" or "plan_adjustment").
  - `entities` (project id, step index, tools/materials, etc.).
  - `gaps` (missing info from user or DB).

Implementation notes:
- Use a **small LLM call** or rule‑based logic (mode‑based) to classify intent.

### 5.2 Diagnose

Inputs:
- `LyraContext` from Deconstruct.

Outputs:
- `AgentPlan` describing which agents to call and in what order.

Example:
- If user asks "Is it safe to drill here?":
  - Agents: [`SafetyCheckerAgent`, `TutorAgent`].
- If user asks "Which screw is A4?":
  - Agents: [`BOMPlannerAgent`, `TutorAgent`].

Implementation notes:
- Start rule‑based; later, consider LLM‑based planner.

### 5.3 Develop

Inputs:
- `AgentPlan`.
- Context (project, step, BOM).

Outputs:
- `AgentResults` map keyed by agent name.

Implementation:
- For each agent in plan:
  - Build a **structured prompt** using templates.
  - Call Claude via LLM client (or local logic for simple agents).
  - Parse and normalize output.

### 5.4 Deliver

Inputs:
- `AgentResults`.

Outputs:
- `OrchestratorResponse`.

Implementation:
- Merge agent outputs respecting priorities:
  - Safety warnings first.
  - Tutor explanations as main message.
  - BOM details as hints.

---

## 6. Agent Interfaces (Contracts)

All agents implement a common interface:

```ts
export interface AgentContext {
  session: Session;
  project: Project;
  step: ProjectStep | null;
  userMessage?: string;
}

export interface AgentResult {
  name: string;
  messages: string[];       // natural language outputs
  hints?: string[];
  warnings?: string[];
  data?: Record<string, any>;
}

export interface Agent {
  name: string;
  capabilities: string[];   // e.g., ['safety', 'bom']
  run(ctx: AgentContext): Promise<AgentResult>;
}
```

### 6.1 BOMPlannerAgent (MVP)

Purpose:
- Clarify which materials or tools the user should use at the current step.

Inputs:
- `project`, `step`, `userMessage`.

Behavior:
- Use Claude to interpret the question and existing BOM entries.
- Return clear text (e.g., "Screw A4 is the 30mm silver screw labeled A4 in your kit.") and optional structured `data`.

### 6.2 SafetyCheckerAgent (MVP)

Purpose:
- Identify obvious safety warnings and limitations.

Inputs:
- `step`, `userMessage`.

Behavior:
- Prompt Claude with step description and user question.
- Return `warnings` such as "Do not drill into walls that may contain electrical wiring; use a stud finder.".

### 6.3 TutorAgent (MVP)

Purpose:
- Provide conceptual explanations and step‑by‑step help.

Behavior:
- Use Claude to explain procedure in simple language using context.
- Should respond in 2–4 sentences per answer.

### 6.4 VisionInspectorAgent (Stub)

Purpose:
- Placeholder for CV checks.

Behavior:
- For MVP, just return an empty result.
- Designed to later call a CV service for verifying photo/AR frame uploads.

---

## 7. LLM Client Abstraction

### 7.1 Module Design

Create `/packages/ai-client` with:

```ts
export interface LLMMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface LLMOptions {
  model?: string;           // e.g., 'claude-3.5-sonnet'
  maxTokens?: number;
  temperature?: number;
}

export async function callLLM(
  messages: LLMMessage[],
  options?: LLMOptions
): Promise<string> {
  // Implementation calls Claude API
}
```

Agents must use this helper instead of calling external APIs directly.

---

## 8. Logging and Telemetry

### 8.1 Events

For each orchestrator call, log an event to the `events` table with:

- `type`: 'orchestrator_invoked'.
- `session_id`.
- `project_id`.
- `step_index`.
- `intent`.
- `agents_used`.
- `warnings_count`.

Also log any agent‑specific events if needed (e.g., 'safety_warning_issued').

### 8.2 Error Handling

- If an agent fails, orchestrator should:
  - Log the error.
  - Fall back to a generic TutorAgent response: "I am having trouble accessing some tools; here is general guidance...".

---

## 9. Security, Safety, and Guardrails

- All orchestrator endpoints must validate auth and ensure the caller is associated with the session.
- Claude prompts must:
  - Be prefixed with a **system message** defining safety constraints (no structural engineering, electrical work beyond basic guidance, etc.).
  - Clearly instruct models not to fabricate measurements or guarantee safety; instead, they must encourage consulting a professional when necessary.

Future:
- Agent identity (Lyra Protocol style) can be layered on by giving each agent a stable ID and storing signed attestations for safety‑reviewed projects.

---

## 10. Implementation Guidance for AI Agents

1. Implement orchestrator as a **separate module/service** in `/apps/api` or equivalent.
2. Keep agent implementations small and composable; avoid cross‑agent state mutation.
3. Use TypeScript types from `/packages/core-types` for Session/Project/ProjectStep.
4. Write unit tests for:
   - Deconstruct/Diagnose logic.
   - Individual agents (mocking `callLLM`).

---

## 11. Acceptance Criteria

The orchestrator is considered MVP‑complete when:

1. `/api/v1/orchestrator/plan` handles `assist` mode requests from mobile app.
2. Lyra 4‑D pipeline is implemented and calls TutorAgent + SafetyCheckerAgent + BOMPlannerAgent as appropriate.
3. Responses are stable, within length limits, and respect safety guardrails.
4. Orchestrator decisions are logged to `events` and can be inspected via admin tools.
