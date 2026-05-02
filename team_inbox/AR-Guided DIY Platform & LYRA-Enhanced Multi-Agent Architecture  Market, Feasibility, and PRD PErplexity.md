# AR-Guided DIY Platform & LYRA-Enhanced Multi-Agent Architecture: Market, Feasibility, and PRD

## Executive Summary

Augmented reality (AR) work-instruction and training markets are moving from early adoption to scaled deployment, with AR training and guided installation software estimated at around 83.65 billion USD in 2024 and growing at roughly 37.9 percent CAGR through 2034 for enterprise training use cases. Within that, specialized AR work-instruction and AR overlay platform markets focused on assembly workflows are estimated at roughly 1.2 billion USD in 2024 and projected to reach 7.8 to 8.7 billion USD by 2033, a 23.6 to 24.5 percent CAGR. The global mobile AR market more broadly is estimated at 37.73 billion USD in 2024 and forecast to reach around 529.93 billion USD by 2034, a 30.24 percent CAGR. Consumer AR usage is already mainstream: over 2 billion people are expected to be using mobile AR by 2025, with the United States alone projected to have roughly 100.1 million AR users in 2025 and about 103.9 million in 2026.[^1][^2][^3][^4][^5][^6]

Despite this growth, the consumer DIY AR segment remains under-served. Existing leaders such as IKEA Place, Wayfair AR, and BILT 3D Interactive Instructions either focus on pre-purchase visualization or on brand-specific 3D instructions, not on independent AR-guided DIY across categories. This leaves a white space for a consumer-first, creator-enabled AR-guided DIY platform that can serve as a “Google Maps for hands-on projects.”[^7][^8][^9]

Parallel to this, AI agent ecosystems are formalizing around identity and protocol layers. The Lyra Protocol (in the Opus Genesis framework) focuses on verifiable agent identity and credentials as a prerequisite for agents to own, trade, and interact with digital assets. Multi-agent operating systems such as LYRAIOS build on Model Context Protocol (MCP)-style designs to orchestrate tool integration and multi-agent collaboration. Separately, “Lyra” prompt-optimization frameworks (e.g., Lyra Prompt, Lyra prompt optimizer) codify a 4-D methodology (Deconstruct, Diagnose, Develop, Deliver) for transforming fuzzy inputs into production-grade prompts and specs.[^10][^11][^12][^13]

This report synthesizes current AR and AR-guided work-instruction market data, competitive landscape, and technology trends, then proposes a system architecture and PRD for an AR-guided DIY platform that leverages a Lyra-style prompt and multi-agent protocol layer to orchestrate AR guidance, AI assistants, content generation, and commerce. It concludes with a structured PRD covering product goals, personas, functional and non-functional requirements, system architecture, component trade-offs, roadmap, and a strategic-tactical “attack plan.”

[^14]

***

## 1. Market Context and Commercial Opportunity

### 1.1 Macro AR and Mobile AR Growth

Multiple independent analysts agree that AR is in a strong growth phase across hardware, software, and services. Global mobile AR revenues are estimated at 37.73 billion USD in 2024 and forecast to reach approximately 529.93 billion USD by 2034, a compound annual growth rate of 30.24 percent. Separate AR statistics aggregations estimate that globally more than 2 billion people will be using mobile AR by the end of 2025, up from roughly 1.7 billion in 2024. In the United States, AR users are projected to reach about 100.1 million in 2025, 103.9 million in 2026, and 106.9 million in 2027.[^2][^4][^5]

AR hardware growth reinforces this trend, with AR hardware market revenue expected to grow to about 9.7 billion USD in 2026 and roughly 38 billion USD by 2030 according to ABI Research, driven by advances in optics, processors, and connectivity. AR and VR headsets collectively are estimated to be worth about 6.36 billion USD in 2026 and to grow to 9.62 billion USD by 2031, with AR devices being the faster-growing subsegment at roughly 12.1 percent CAGR.[^15][^16]

These macro trends confirm that AR is no longer a niche; it is a cross-category medium with both consumer and enterprise momentum.

[^17]

### 1.2 AR Work Instructions and Assembly Markets

Within AR, work-instruction and guided assembly are distinct, high-value verticals. A recent AR work-instructions-for-assembly report estimates the global AR work-instruction-for-assembly market at roughly 1.2 billion USD in 2024, projecting growth to about 7.8 billion USD by 2033 at a 23.6 percent CAGR. A parallel analysis of AR work-instruction platform vendors projects a similar starting point of about 1.2 billion USD in 2024, with growth to approximately 8.7 billion USD by 2033, a 24.5 percent CAGR.[^3][^6]

Adjacent digital work-instruction markets, such as digital work instructions for automotive assembly, are estimated around 1.34 to 1.42 billion USD in 2024 and forecast to reach roughly 3.96 to 3.97 billion USD by 2033 at a 11.7 to 12.7 percent CAGR. Enterprise AR training and guided installation software more broadly is estimated at about 83.65 billion USD in 2024 with a 37.9 percent CAGR through 2034.[^18][^19][^1]

These numbers validate that AR-guided workflows—especially in complex assembly, maintenance, and training—are commercially proven and scaling in B2B environments, even as consumer DIY-specific AR guidance remains under-developed.



### 1.3 Consumer AR Usage and Behavior

Consumer AR adoption is already mainstream. One synthesis of AR statistics reports that approximately one-seventh of the global population currently uses AR in some form, primarily via mobile. Mobile AR users—through apps, web AR, and visual search—are projected around 1.03 billion in 2024 and about 1.19 billion by 2028.[^2]

Consumer engagement metrics are also strong. AR campaigns can generate engagement times four times longer than mobile video and achieve 70 percent higher memory recall, which translates into higher conversion rates and lower returns for retail. AR product experiences in retail settings are reported to deliver engagement roughly 200 percent higher than non-AR experiences and can reduce return rates by more than 20 percent. These effects are directly relevant to a DIY AR platform that integrates content, instruction, and commerce.[^20]



### 1.4 DIY, Home Improvement, and Training Synergy

The DIY home-improvement market itself is on the order of hundreds of billions of USD annually, with global DIY spend approaching or exceeding 1 trillion USD when including both retail product purchases and related services in large markets. Market-intelligence reports cited in prior research on BuildAR suggest that global DIY retail was around 790 to 800 billion USD in the mid-2020s, with projected growth to roughly 1.4 to 1.5 trillion USD by 2030, implying mid-single to low-double-digit CAGR.[^14]

In parallel, AR work-instruction deployments in manufacturing have demonstrated measurable productivity and quality gains that are relevant analogues for DIY. Case studies cited in AR training and guided installation guides report average productivity increases of around 60 percent for manufacturing firms using AR-guided procedures, with specific examples such as Boeing reducing training time by up to 75 percent for aircraft wiring harness assembly, Airbus completing some maintenance tasks 25 percent faster, and Pfizer cutting training time by 40 percent while improving knowledge retention.[^1]

The combination of: (1) widespread mobile AR adoption, (2) proven AR productivity gains in adjacent assembly and training contexts, and (3) a large, growing DIY market suggests strong feasibility and upside for a consumer-centric AR-guided DIY platform that translates industrial AR work-instruction paradigms into home, prosumer, and small-business use.



***

## 2. Competitive Landscape in AR-Guided DIY and Related Categories

### 2.1 AR Visualization Apps (Pre-Purchase Focus)

**IKEA Place** is one of the best-known AR retail apps, allowing users to place true-to-scale 3D models of IKEA furniture in their rooms using ARKit on iOS and similar capabilities on Android. It focuses on catalog browsing and pre-purchase visualization—users scan their space, then place sofas, tables, or chairs to judge fit and aesthetics, sometimes with integration into IKEA’s e-commerce flow. The app does not provide step-by-step assembly instructions; instead, customers still rely on PDF manuals or separate texts for assembly.[^21][^22]

Design and research projects like IKEA-Assemble show how AR could guide assembly of flat-pack furniture by overlaying steps on top of real objects, but this remains in prototype or concept form rather than being adopted as IKEA’s primary instruction channel. This indicates conceptual validation and demand, but also highlights that incumbent furniture retailers have not yet fully committed to AR-guided assembly as a first-class consumer product.[^23][^24]

[^25]

### 2.2 3D Interactive Instruction Apps (Brand-Centric)

**BILT** is a leading 3D interactive instruction app offering animated instructions for assembly, installation, maintenance, and repair across hundreds of brands. BILT’s mobile and Vision Pro applications present animated 3D models with zoom, rotation, step-forward/step-back navigation, optional voice narration, and a dedicated “Toolbox” set of basic DIY and tool-usage guides. The platform is free to end users; brands fund the content to reduce returns and improve satisfaction.[^8][^9][^26]

BILT’s value proposition closely parallels the “Google Maps for instructions” analogy and has achieved millions of downloads. However, it remains brand-centric and largely non-AR: instructions are typically presented as 3D scenes that the user orbits on screen rather than as spatial overlays anchored in the user’s environment. Vision Pro support introduces spatial computing but still emphasizes 3D instructions in immersive space rather than full real-world occlusion-aware AR with computer-vision feedback on what the user has actually assembled.[^9][^27][^8]

[^10]

### 2.3 Content and Creator Platforms (Non-AR DIY Guides)

Platforms such as YouTube, Instructables, and Wikihow dominate DIY instruction via long-form video, step-by-step text, and static images. These channels scale content extremely well but have structural limitations for execution: they lack spatial awareness, personalized pacing, live error detection, and structured progression that reacts to what the user has already done.[^7]

DIY-focused creators already have large audiences: top “how-to” channels serving DIY and home-improvement segments reach millions of subscribers. However, their content is constrained by current media formats, leading to known pain points such as constant pausing and scrubbing in videos, ambiguous camera angles, and difficulty mapping 2D instructions to a 3D workspace.[^7][^14]

[^28]

### 2.4 AR Creator and Campaign Tools

No-code AR creator tools such as Kivicube, ZapWorks, and Snap’s Lens Studio make it easier to author WebAR and social AR experiences, lowering barriers for marketers and creators to deploy AR. However, these platforms primarily target marketing, art, education, or lightweight interactive experiences rather than deeply structured multi-step work instructions or complex DIY build flows.[^29][^30]

WebAR vs app-based AR trade-offs are also shifting. Some analyses argue that WebAR increasingly matches native visual fidelity thanks to WebGPU and 5G, and that removing app-download friction improves conversion in retail contexts. For a work-instruction-heavy DIY product, though, persistent multi-step sessions, offline support, richer device APIs, and high-performance spatial tracking still weigh in favor of native AR for the core experience, with WebAR as an acquisition and demo surface.[^31]

[^32]

### 2.5 Summary: White Space and Competitive Gap

Taken together, current solutions cover the following:

- AR visualization for shopping (IKEA Place, Wayfair AR, Houzz) but no AR execution guidance.
- 3D interactive instructions (BILT) but primarily non-AR and brand-locked, with limited community or creator-economy dynamics.[^26][^9]
- Massive DIY content platforms (YouTube, Instructables) with no spatial intelligence or structured AR guidance.[^7]
- AR creation frameworks and campaign tools focused on marketing and lightweight interactions rather than hard, multi-step assembly and error-checking.[^30][^29]

No single platform currently offers a cross-brand, multi-category, AR-guided DIY execution environment that combines:

- Spatial overlays anchored in the user’s real workspace.
- Multi-step checklists with stateful progress.
- AI assistance and computer-vision error detection.
- Creator tools for authoring and monetizing AR project guides.
- Commerce integration for parts, tools, and materials.

This is the opportunity for a BuildAR/BuildARPro-style product augmented by a Lyra-inspired multi-agent and prompt-orchestration layer.

[^33]

***

## 3. Lyra Protocol, Lyra Prompting, and Multi-Agent Patterns

### 3.1 Lyra Protocol and Agent Identity

Lyra Protocol, as described in the Opus Genesis framework, positions itself as an “AI identity layer” that allows AI agents to establish verifiable identity and credentials before they interact with assets or other parts of a broader ecosystem. The protocol emphasizes an identity-first architecture in which agents register identifiers, attach verifiable credentials, and operate under decentralized identity (DID) and zero-knowledge proof schemes in cooperation with partners such as Privado ID.[^10]

In this model, agents must prove who they are—via signed credentials—before owning, trading, or interacting with digital assets or participating in multi-agent workflows. That pattern is highly relevant for a future AR DIY platform with:[^10]

- Multiple internal agents (e.g., AR guidance, CV checker, BOM generator, support agent).
- External third-party agents (e.g., retailer pricing agents, creator agents).
- The need for traceability and accountability when agents recommend safety-critical steps or transact on behalf of users.

[^11]

### 3.2 LYRAIOS and Multi-Agent OS Concepts

A separate open-source project, LYRAIOS, describes itself as an MCP-style operating system for multi-AI agents that emphasizes modular tool integration, multi-modal interfaces, and a multi-agent collaboration engine for enterprise workflows. The design highlights:[^11]

- Open protocol architecture for pluggable tools and services.
- A distributed task orchestration engine for dynamic agent collaboration.
- Support for complex workflows such as enterprise-grade automation and conflict resolution.

While LYRAIOS is not specific to AR or DIY, its architectural concepts—tool manifests, registration, and orchestrated multi-agent collaboration—map directly to a multi-agent backend for an AR DIY platform where different agents handle perception, planning, instruction, and commerce.

[^12]

### 3.3 Lyra Prompt Optimization Framework (4-D Methodology)

The Lyra Prompt optimizer, as documented in Lyra Prompt and shared reference prompts, defines “Lyra” as a master-level prompt optimization specialist whose mission is to transform raw user inputs into precise, effective prompts using a structured 4-D methodology. The four stages are:[^13][^12]

1. **Deconstruct** – Extract core intent, entities, context; identify missing information.
2. **Diagnose** – Audit for ambiguity, specificity, and structural needs.
3. **Develop** – Design an optimized prompt or spec, selecting techniques such as chain-of-thought, few-shot examples, constraints, and role assignment.
4. **Deliver** – Output the improved prompt/spec with implementation guidance.

The framework is used to generate AI-ready prompts and “specs” that drive downstream coding, design, or QA agents, and is increasingly applied in systems like withLyra.com, which turns messy project context into structured, AI-executable specs for multi-agent teams.[^34][^13]

For an AR DIY platform, this methodology can be reinterpreted as a “Prompt & Plan OS” layer that:

- Takes user goals (e.g., “build a floating shelf from these materials”) and context (room scan, inventory) as input.
- Deconstructs and diagnoses requirements (skill level, constraints, materials).
- Develops an internal execution spec (steps, AR anchors, tool list, BOM, safety checks) for AR and AI agents.
- Delivers both user-facing AR instructions and agent-facing prompts for CV and optimization agents.

[^35]

### 3.4 Implications for AR DIY Platform

Integrating Lyra-style identity and prompt-orchestration patterns enables:

- **Trust and Safety:** Each internal agent (e.g., SafetyChecker, BOMPlanner) can have verifiable identity and audited decision logs, crucial when advising on electrical work, load-bearing structures, or tool usage.
- **Extensibility:** Third-party agents (e.g., retailer connectors, pro-contractor assistants) can plug into a defined protocol layer, facilitating ecosystem growth.
- **Prompt Governance:** A central Lyra-like orchestrator can enforce prompt hygiene, red-team sensitive tasks, and normalize tasks before handing them to specialized AI or CV models.

This aligns well with a future where AR DIY is not a single agent but a constellation of agents coordinated via an identity-aware protocol.

[^36]

***

## 4. Product Vision and Strategy

### 4.1 Product Vision

The product vision is to build a cross-platform AR-guided DIY platform that:

- Delivers real-time, spatially anchored, step-by-step guidance for home-improvement, furniture assembly, maker, and light trade tasks on consumer devices.
- Integrates AI agents for contextual assistance, BOM optimization, safety checking, and personalization.
- Enables creators and pros to author, publish, and monetize AR project templates.
- Connects to retail and marketplace partners to close the loop from inspiration to parts purchase to completed project.

In essence, it aims to be the “AI-guided AR copilot” for any physical project a user wants to perform, with multi-agent intelligence and a Lyra-style spec and prompt OS under the hood.

[^34]

### 4.2 Target Segments and Personas

Building on prior BuildAR research, key target personas include:

- **Tech-Savvy DIY Enthusiasts:** Early adopters with mid-to-high DIY skills who already use YouTube and AR apps; want speed, precision, and cooler tools.[^14]
- **New Homeowners and DIY Newbies:** Time-pressed, budget-sensitive users lacking confidence; want safe, foolproof guidance and BOM clarity.[^14]
- **DIY Content Creators:** Makers with audiences on YouTube, Instagram, TikTok who want better ways for followers to “actually build” their projects and new monetization channels.[^14]
- **Store Associates and Retail Partners:** Hardware-store staff who recommend tools and materials; can champion the app in-aisle as a value-added service.[^14]

Each persona maps naturally to AR and AI capabilities—for example, newbies benefit from safety agents and checklists, creators benefit from content-authoring tooling and analytics, and store associates benefit from BOM and inventory integration.

[^37]

### 4.3 Commercial Model Options

The platform can support multiple business models over time:

- **Consumer Freemium + Subscription:** Free tier with limited projects and AR fidelity; Pro tier with unlimited projects, advanced AR features, offline downloads, and full AI agent access.[^7]
- **Creator Marketplace:** Revenue sharing with creators based on project usage and completions, similar to app stores and creator platforms.[^7]
- **B2B White-Label:** SaaS licensing of the AR guidance and LYRA-based agent infrastructure to furniture brands, hardware retailers, and equipment OEMs for branded experiences (e.g., BILT-like but AR-native).[^14]

Given consumer price sensitivity and the presence of free alternatives (YouTube, PDFs), the most resilient model is a hybrid: consumer freemium and subscription for advanced capabilities, plus B2B licensing and affiliate/commerce revenue tied to parts and tools.

[^38]

***

## 5. System Architecture and Component Design

### 5.1 High-Level Architecture Overview

The proposed architecture is a layered system with four main strata:

1. **Experience Layer (Client Apps):** Native mobile apps (iOS/Android) using ARKit/ARCore and optionally Unity AR Foundation for 3D; future AR headset apps (Vision Pro, Quest, others); WebAR microsites for acquisition and lightweight previews.[^5][^29]
2. **Interaction & Guidance Layer:** AR Scene Manager, Step Sequencer, CV-based Error Checker, Safety Overlay, and Voice + Text UI components.
3. **Intelligence & Orchestration Layer:** Lyra-style Prompt & Plan OS, Multi-Agent Orchestrator (MCP-style), and specialized agents (BOMPlanner, SafetyChecker, VisionInspector, Tutor, RetailConnector).
4. **Data & Services Layer:** Project CMS, Creator Studio backend, User & Analytics store, Commerce & Partner APIs, Authentication, and Identity/LYRA Protocol integration.

Agents communicate via an identity-aware protocol; prompts and plans are standardized; AR instructions are delivered as structured, versioned step graphs, not ad hoc content.

[^39]

### 5.2 Key Backend Components

**5.2.1 Project CMS and Content Graph**

- Stores projects as structured graphs of steps, with metadata on difficulty, required tools, materials, safety notes, AR anchors, and dependencies.[^7]
- Supports multiple content types per step (text, images, simple 3D assets, parametric templates) and references to AR overlays.
- Enables versioning and A/B variants (e.g., different screw types by region, alternative tools).

**5.2.2 Creator Studio and Authoring Pipeline**

- Web-based tool that lets creators define projects, record steps, tag AR anchor types (plane, edge, corner, reference object), and upload assets.
- Integrates Lyra-style prompt assistance to help creators specify clear instructions and safety notes; the prompt optimizer can refactor instructions into structured schemas.[^12]
- Generates internal JSON schemas that the AR Guidance Engine can interpret on-device, with validation checks (e.g., missing safety disclaimers, ambiguous tool references).

**5.2.3 Multi-Agent Orchestrator and Lyra OS**

- Implements an MCP/A2A-style protocol interface for agents.[^39][^11]
- Runs a central Lyra orchestrator agent that:
  - Deconstructs user intent (project selection, goal, constraints, environment).
  - Diagnoses missing data (measurements, materials, tools).
  - Develops a task plan and internal prompts for specialized agents.
  - Delivers refined plans back to client and logs decisions.
- Supports internal agents such as:
  - **BOMPlanner:** infers BOM from project definitions and user measurements; calls retailer APIs.
  - **SafetyChecker:** checks steps against risk rules (e.g., electrical codes, load limits), flags steps for warnings.
  - **VisionInspector:** uses CV to detect misaligned parts or missing steps in AR.
  - **Tutor:** provides context-aware Q&A explanations, analogies, and just-in-time micro-lessons.

[^40]

**5.2.4 Identity, Credentials, and Auditability**

- Integrates an identity layer inspired by Lyra Protocol’s identity-first architecture to assign DIDs and verifiable credentials to agents, creators, and potentially high-trust projects.[^10]
- Stores signed attestations for:
  - Safety review of templates (e.g., certified electrician reviewed wiring project X).
  - Creator verifications (e.g., verified pro contractor vs hobbyist).
  - Agent policy versions used when generating instructions.
- Enables compliance logs, crucial for B2B and safety-sensitive use.

[^13]

### 5.3 AR and CV Components on Device

**5.3.1 AR Scene Manager**

- Uses ARKit and ARCore for plane detection, anchors, and occlusion; optionally Unity AR Foundation or similar for cross-platform 3D rendering.[^41][^29]
- Manages alignment processes: calibrating the AR scene with project geometry (e.g., aligning first bracket, referencing wall studs).

**5.3.2 Step Sequencer and UI**

- Renders step overlays (arrows, bounding boxes, ghosted models) synchronized with a state machine representing the user’s progress.[^7]
- Supports voice commands (next step, repeat, zoom in, show tools) to keep hands free.

**5.3.3 VisionInspector and Feedback Loop**

- On-device CV pipelines (using on-device ML frameworks) verify key states, such as whether a bolt is in place or a bracket is level enough.
- Feeds results back to SafetyChecker and Step Sequencer to block progression or display warnings if critical conditions are unmet.

[^42]

### 5.4 Trade-Offs: Native vs WebAR, Unity vs React Native, Centralized vs Agentic

**Native vs WebAR**

- Native AR on iOS/Android using ARKit/ARCore provides higher fidelity tracking, offline use, deep device integration, and richer CV capabilities.[^43][^29]
- WebAR lowers friction and may be ideal for quick try-before-download and marketing experiences, especially as WebGPU improves, but is still less suitable for long, stateful sessions that require precise tracking.[^31]
- Recommendation: Native mobile AR for core DIY execution; WebAR as acquisition, preview, and light interactive marketing.

**Unity AR Foundation vs Device-Native AR SDKs**

- Unity AR Foundation offers cross-platform abstraction but adds engine overhead and a different tech stack.[^29][^7]
- Directly using ARKit/ARCore through React Native or native modules aligns with existing JS/TS stacks and may simplify mobile-app iteration.[^43][^7]
- Recommendation: For a lean MVP, use React Native with native AR modules; consider Unity for advanced 3D or headset-specific experiences.

**Centralized Monolith vs Multi-Agent Services**

- A monolithic backend may ship faster but risks becoming a bottleneck as new features (e.g., new agent types, new partner integrations) are added.
- A multi-agent, protocol-driven architecture enforces modularity and allows specialized teams or partners to contribute agents under a shared identity and policy framework.[^11][^39]
- Recommendation: Implement a thin orchestrator with clear tool/agent manifests from the outset; keep the number of initial agents small but design for expansion.

[^1]

***

## 6. Feasibility, Risks, and Hurdles

### 6.1 Technical Feasibility

AR-guided work-instruction systems are technically feasible today, as demonstrated by industrial deployments and consumer 3D instruction apps. Core enabling technologies include:[^8][^9][^1]

- Mature AR frameworks (ARKit, ARCore, Unity AR Foundation, Vuforia) for plane detection and anchored 3D content.[^29][^43]
- On-device ML runtimes for basic CV checks.
- Cloud-based LLMs and agent frameworks for planning, Q&A, and personalization.

The hardest components technically are robust environment calibration, error detection via CV in consumer-grade lighting and clutter, and scalable, cost-effective 3D/AR content authoring. These are mitigated by progressive enhancement: start with simple overlays and manual confirmations, then gradually introduce CV-based gating and 3D reconstructions once baseline instructional value is proven.

[^2]

### 6.2 Product and UX Hurdles

Key product hurdles include:

- **Onboarding into AR:** Many users still struggle with AR calibration; friction here can cause churn.[^7]
- **Cognitive Load:** Overly complex overlays or instructions can be overwhelming; the system must prioritize clarity and minimalism.
- **Device Compatibility:** AR performance varies widely across devices; a baseline of supported hardware must be defined, and fallbacks provided.

UX research must explore the right balance between AR overlays, textual prompts, and video snippets for each persona. For example, novices may benefit from more textual explanation and safety cues, while experts prefer minimal overlays.

[^3]

### 6.3 Content and Creator-Economy Hurdles

Educational AR content creation is expensive compared with filming a standard video. BILT’s model shows that OEMs will fund 3D instructions when they reduce returns and support costs, but consumer DIY projects (e.g., “build a custom shelf”) lack clear single-brand sponsors.[^9][^26]

To overcome this, the platform must:

- Seed a core library of high-value, cross-brand templates in-house.
- Rapidly onboard creators with easy authoring tools and clear monetization.
- Use Lyra-style automation to reduce friction in structuring instructions and generating safe, clear verbiage.

[^44]

### 6.4 Regulatory, Safety, and Liability Considerations

AR-guided instructions for electrical, structural, or potentially hazardous tasks raise safety and liability questions. Regulatory requirements vary by jurisdiction for electrical work, load-bearing structures, gas, and plumbing.

Mitigations include:

- Clear scoping of which tasks are “DIY safe” vs must recommend a professional.
- SafetyChecker agent with jurisdiction-aware rulesets.
- Signed attestations for safety-reviewed templates and pro creators (using the identity layer).[^10]
- Prominent disclaimers and in-step safety warnings.

[^4]

### 6.5 Market and GTM Risks

Finally, GTM risks include competition from entrenched content habits (YouTube), app fatigue, and the risk that BILT or similar players expand aggressively into AR overlays and creator marketplaces. On the other hand, these risks are partially mitigated by the sheer scale of the DIY market and the nascency of AR-guided execution.

[^18]

***

## 7. Product Requirements Document (PRD)

### 7.1 Product Summary

**Product Name (placeholder):** BuildAR Pro (working title)

**One-Line Description:** Cross-brand AR-guided DIY platform with multi-agent AI assistance and a creator marketplace.

**Primary Goal (Phase 1–2):** Demonstrate that AR-guided instructions materially improve DIY project success vs video/text, measured by completion rate, error incidence, and user satisfaction.

[^15]

### 7.2 Goals and Success Metrics

**User Outcomes:**

- Increase first-attempt project completion rates by at least 25 percent vs baseline video/text-only flows for comparable tasks in usability studies.
- Reduce self-reported frustration (Likert-scale scores) by at least 30 percent.
- Achieve Net Promoter Score (NPS) above +40 among early adopters.

**Business Outcomes (Year 1–2):**

- Reach 50,000 monthly active users (MAUs) across target markets.
- Demonstrate affiliate/commerce-driven GMV (gross merchandise value) of at least 2 to 5 million USD annually via BOM-driven purchases.
- Secure at least two B2B design or pilot agreements with OEMs or retailers.

[^5]

### 7.3 Personas and Use Cases (Condensed)

- **Ethan (Tech-Savvy DIYer):** Assembles furniture, builds maker projects; wants AR guidance that feels futuristic and efficient.[^14]
- **Hannah (New Homeowner):** Needs handholding through basic installs (curtain rods, light fixtures) and values safety cues and BOM sanity checks.[^14]
- **Carlos (Creator):** Wants to publish interactive versions of his projects and monetize them; values analytics and branding.[^14]
- **Alicia (Store Associate):** Uses the app in-aisle to show customers how a project works and to ensure BOM completeness for chosen projects.[^14]

[^19]

### 7.4 Scope (MVP)

**In-Scope (Phase 1–MVP):**

- Native mobile apps (iOS, Android) with:
  - AR-based step-by-step guides for 10–20 curated projects (furniture assembly, simple installs, basic repairs).
  - Non-AR fallback views (3D or 2D step screens) for unsupported devices.
  - Basic AI assistant (text and/or voice) for context-aware Q&A per project.
- Project CMS for internal authors.
- Light Lyra-style prompt orchestrator that converts project definitions into agent-ready schemas and prompts.
- Minimal BOM planner (static BOM per project, basic regionalization).

**Out-of-Scope for Initial MVP but Designed For:**

- Full creator studio for third-party creators.
- Automated BOM optimization and deep commerce integration.
- Computer-vision-based error blocking (beyond simple checks).
- Headset and glasses support.

[^16]

### 7.5 Functional Requirements

#### 7.5.1 Project Discovery and Selection

- Browse projects by category, difficulty, estimated time, and required tools.
- Search by keyword (e.g., “floating shelf,” “fix leaky faucet”).
- Filter by skill level, AR availability (on device), and free vs premium.

#### 7.5.2 AR Session Setup

- Detect whether device supports ARKit/ARCore and minimal performance threshold.
- Provide guided onboarding (move phone, scan area, place calibration anchors).
- Allow user to re-calibrate or reset AR scene mid-project.

#### 7.5.3 Step Execution Flow

- Display a step card with text, image/3D preview, and AR overlay.
- Allow user to toggle between AR and non-AR view.
- Provide “Next,” “Back,” and “Repeat Step” controls, plus optional auto-advance.
- Show contextual safety warnings at relevant steps.

#### 7.5.4 AI Assistance

- Context-aware Q&A inside a project session; AI sees project context, step index, BOM, and recent user interactions.
- Provide suggestions such as “You might want to pre-drill here” or “Check that the bracket is level.”
- For out-of-scope requests (e.g., unrelated tasks), gracefully decline or redirect.

#### 7.5.5 BOM and Commerce

- Show required tools and materials upfront and per step.
- Link to partner or generic SKUs where available (affiliates or pilot retailers).
- Allow user to mark items as “already have” vs “need to buy.”

[^45]

### 7.6 Non-Functional Requirements

- **Performance:** AR tracking must maintain at least 30 fps on supported devices under typical indoor lighting.
- **Reliability:** Project state should persist across app restarts, including current step index and calibration details where possible.
- **Privacy:** Only necessary sensor data and anonymized usage metrics should be transmitted; camera frames used for CV should be processed on-device by default.
- **Security:** All communication between client and backend encrypted (TLS), with agent identities and credentials verified via the Lyra-inspired identity layer.

[^46]

### 7.7 System Architecture PRD View

The PRD requires the following high-level components:

- **Mobile Apps:** React Native shell with native AR modules; networking, offline caching; local CV components.
- **Backend Services:**
  - Project CMS (PostgreSQL-like plus object storage for assets).
  - Orchestration service implementing Lyra 4-D steps for incoming intents and project specs.
  - Agent microservices for BOM, safety rules, and Q&A.
  - Identity and credential service bridging to Lyra Protocol-style DID infrastructure.
- **Creator and Admin Interfaces:** Internal web UIs for authoring, reviewing, and publishing projects; safety and quality review flows.

[^47]

### 7.8 Component Trade-Offs and Rationale (PRD Summary)

- **React Native vs Pure Native:** Choose React Native to accelerate cross-platform UI and reuse across consumer app and Creator Studio web (via shared logic and design system) while implementing AR and CV in specialized native modules.[^43]
- **Hosting vs Serverless:** Adopt a serverless or managed-platform approach for the orchestrator and agents at early scale to focus on product rather than infrastructure, with a clear pathway to containerized microservices later.
- **Centralized vs Decentralized Identity:** Start with centralized identities for agents and creators but design identity schemas to be compatible with future DID and Lyra Protocol integrations (e.g., mappable IDs, revocation mechanisms).[^10]

[^20]

***

## 8. Strategic and Tactical “Attack Plan”

### 8.1 Strategic Phasing (12–24 Months)

**Phase 1: Proof-of-Value (0–6 Months)**

- Ship MVP with core AR-guided flows for 10–20 projects in one or two categories (e.g., furniture assembly, basic installs).
- Conduct controlled usability studies comparing AR-guided flows vs YouTube/text for matched tasks; record completion rates, time-on-task, and error incidence.
- Integrate a lightweight Lyra orchestrator to create internal execution specs from project definitions and user context.

**Phase 2: Scale Content and AI (6–12 Months)**

- Expand project library to 100+ templates across multiple categories.
- Launch limited Creator Studio for selected creators; incorporate Lyra prompt assistance in authoring.
- Introduce BOMPlanner and SafetyChecker agents; begin logging and analyzing their decisions.

**Phase 3: Marketplace and B2B Pilots (12–24 Months)**

- Open creator marketplace to a broader set of authors and enable revenue-share monetization.
- Integrate with at least one regional hardware retailer or e-commerce platform for BOM-driven purchasing.
- Pilot B2B white-label solution with one OEM or retailer, reusing the same Lyra-based orchestration backend.

[^6]

### 8.2 Tactical Plan for Teams (Lower-Resolution)

**Engineering (Mobile & Backend)**

- Month 1–3: Implement AR session foundation, step sequencer, and minimal Lyra orchestrator service.
- Month 4–6: Implement AI Q&A agent integration, project CMS, and initial BOM display logic.
- Month 7–12: Extend orchestrator to handle BOMPlanner and SafetyChecker; refactor services into modular agents.

**Design & UX**

- Month 1–2: Define design system and AR session UX for on-ramp, calibration, and core step flow.
- Month 3–6: Test variations of overlay density and safety messaging; develop patterns for AI assistance UI.
- Month 7–12: Design Creator Studio flows and cross-device experiences (e.g., starting on web and continuing on mobile).

**Content & Creator Ops**

- Month 1–3: Author and test 10–20 internal projects; develop authoring guidelines and safety checklists.
- Month 4–6: Identify and onboard 5–10 pilot creators; co-author AR versions of their flagship projects.
- Month 7–12: Launch closed beta of Creator Studio; monitor content quality and user outcomes.

**Business & Partnerships**

- Month 1–3: Validate interest with local retailers and OEMs; secure at least one memorandum of understanding for pilot.
- Month 4–6: Negotiate affiliate and BOM-integration tests with online retailers.
- Month 7–12: Formalize B2B pilot scope and success metrics; align with roadmap for identity and auditability.

[^23]

### 8.3 Risk Mitigation Workstreams

- **Safety & Legal:** Parallel track to define prohibited projects, disclaimers, and review workflows; engage legal counsel and insurance early.
- **Identity & Ethics:** Incrementally layer Lyra-style identity; begin with internal agent attestation and progress toward external DID for creators and enterprise partners.
- **Performance & Device Coverage:** Test on a matrix of devices; maintain a prioritized list of performance optimizations; implement non-AR fallback flows.

[^8]

***

## 9. Conclusion

The convergence of large, growing AR markets, proven AR work-instruction gains, and a massive DIY/home-improvement economy creates a compelling backdrop for an AR-guided DIY platform with AI and multi-agent intelligence. Market data shows that AR training and guided installation software, AR work-instruction platforms, and mobile AR more broadly will all grow at double-digit CAGRs over the next decade, while DIY spending remains enormous and under-digitized in terms of guidance and planning.[^3][^5][^1]

By combining robust AR guidance, Lyra-inspired prompt and multi-agent orchestration, and an identity-first agent architecture, the proposed platform can differentiate from existing visualization and instruction products and position itself as both a consumer brand and a B2B infrastructure layer. The PRD and architecture presented here provide a concrete starting point to align engineering, design, content, and business teams around a sequenced, risk-aware execution path.

---

## References

1. [AR-Guided Installation: The Complete B2B Buyer's Guide for 2026 ...](https://seller.alibaba.com/blogs/2026/southeast-asia/apparel-accessories/ar-guided-installation-training-accuracy-alibaba-b2b) - AR training market valued at USD 83.65 billion in 2024, growing at 37.9% CAGR through 2034 · Manufac...

2. [Augmented Reality Statistics By Innovations and Facts (2026)](https://market.us/statistics/information-and-communication/augmented-reality/) - Augmented Reality Statistics: Digital data and the live, in-the-moment world are smoothly combined w...

3. [AR Work Instructions for Assembly Market Research Report 2033](https://researchintelo.com/report/ar-work-instructions-for-assembly-market) - According to our latest research, the Global AR Work Instructions for Assembly market size was value...

4. [Augmented Reality Statistics By Market, Users, And Trends (2025)](https://electroiq.com/stats/augmented-reality-statistics/) - In 2025, about 54.1% of the global population is expected to use AR software, and this share may inc...

5. [Mobile Augmented Reality (AR) Market Size and Growth 2025 to 2034](https://www.precedenceresearch.com/mobile-augmented-reality-market) - The global mobile augmented reality (AR) market size was estimated at USD 37.73 billion in 2024 and ...

6. [AR Work Instructions Platform Market Research Report 2033](https://marketintelo.com/report/ar-work-instructions-platform-market) - As per our latest market intelligence, the Global AR Work Instructions Platform market size was valu...

7. [promaker_ar_research.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/104142404/745c7ab0-0c39-4af8-8687-a6390877d7c9/promaker_ar_research.md?AWSAccessKeyId=ASIA2F3EMEYE63OKSDI2&Signature=1DoH%2FND51fKIj%2FbWJr3smiJS%2BEU%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHsaCXVzLWVhc3QtMSJIMEYCIQDcpPPFHvnunLhAngnzdKhBDUBJKdxG9LI6y4IEPuYzIAIhALeh2ATcuKmB3Gb0W8Z1NxB1CXXU0dh%2FFa8ir5ipi97pKvMECEQQARoMNjk5NzUzMzA5NzA1Igx7uebghH%2BQW3Ixrfoq0AS5%2FuNo9otdOlAQnsMoMi4XqtVRq28wGK4lQbmC%2BpxHs4M9v%2FGhqzp1eLaq6a86UaX222runzETQqluQE3QutSCUR9AyjQXmtFc9sQLsda99cNznSAAP9WRacWj0Szan%2BWCX9EschbfU8ge9O%2BNgUxCuWx%2FUNBxhrWvktTU8kKwgY3zKTlA9H%2BWIpSSk5K81BxWG5%2BmiUtSEbj%2F7r5%2BHSdtuM578QDTSNORjUXaqqgv6weyN58kbCCXuwb44Z3mKw4hJxTmjAqupy65VAB7DMH3yCwvg9Z1VLKTK8JrBZkvTPU%2FLNT%2B0kMPtFBrhdsqNt0BGA8DS2Y1I7AtydvvEXimawRRxpvcN2PPDKdoVK57l1h28p2leLc5Ob3E%2B6eXeHRJRoAFf6ZALK4pImlUIUP9l093EUtHzHQ5OjEc7MtUFnhVe2vJf9vt8CqbkoA38k1C70Ixts7%2F9bk3ww%2B0n8TFV%2FOJ8AgMpJNZEv%2BVicnPFn9tXfIcdn2%2FX6CesrtXy6vrcgTIld9ExSMUVfuqqtivxskbCwBTwTPUooxYZ5fEWfC69k2EgoxH4wDC0br8xg%2BBdV3jrJLLGUjVuZ%2FtUMJE0yqqnF8Z9nuGNtTlKKgttOvEUg1XHTRMXw3Bth4KLhMYisgjF66SPNyMxHZvZw0UvmWI%2BcYRt6qKv95%2BTjbGD8VtoUt2A%2B%2FyaSjzU7gGRd7mDRr8VLncVV6qR8jm7eNH9r1irvHVmuYUiKq%2FU2zQeAM%2Bu%2FufcH%2FP%2FJlYJl8n%2FDRDQUuyJ3gPqjSPe%2FyjtrvDMOWP2c8GOpcBCw946vHWWpRwEXwvxQkd61g30a6dZfieVfCpEVYI%2FDTHVc7yrxvrSy6Ecx%2F7b0D75HUwpXQLkNeP2nZITSw2qEg2eVd6D0Jn6JaZ91EkjiH6gFZEg5HAZO5%2Bnpi6xrS7jFjMTQ04vlHfV5Jz6H1zO8PDUqeyzh6WThtTrdbjcoxZBY2W%2FCxFtunzxLM8o63jzUmH%2FGUtGg%3D%3D&Expires=1777751480) - Prepared by Tomy Research Specialist Date 2026-04-30 For Andy Orchestrator Cole Pitch Deck Inon Baas...

8. [BILT 3D Immersive Instructions - App Store](https://apps.apple.com/us/app/bilt-3d-immersive-instructions/id6469053057) - BILT creates and delivers stunning 3D Immersive Instructions to maximize comprehension and minimize ...

9. [BILT: 3D Instructions - Apps on Google Play](https://play.google.com/store/apps/details?id=com.bilt.mobile&hl=en) - Follow easy BILT instructions to repair a toilet, lay bathroom tile, paint a room, jump a car batter...

10. [Lyra AI - BETA](https://www.lyrastory.ai) - Lyra Protocol provides the foundational identity layer that enables AI agents to establish verifiabl...

11. [lyraios - GitHub](https://github.com/GalaxyLLMCI/lyraios) - LYRAI is a Model Context Protocol (MCP) operating system for multi-AI AGENTs designed to extend the ...

12. [Lyra Prompt](https://lyraprompt.com) - Transform any idea into powerful AI prompts. Our advanced generator creates optimized prompts for te...

13. [You are Lyra, a master-level AI prompt optimization specialist. Your ...](https://x.com/DataChaz/status/1945022239709016116) - I'm Lyra, your AI prompt optimizer. I transform vague requests into precise, effective prompts that ...

14. [Current-AR-Market-Trends-research-3.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/104142404/bfef0152-533e-49a3-8421-8cdc63062d25/Current-AR-Market-Trends-research-3.pdf?AWSAccessKeyId=ASIA2F3EMEYE63OKSDI2&Signature=JeGTxrmpovL%2FNuWfUatlf9Ov3%2FE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHsaCXVzLWVhc3QtMSJIMEYCIQDcpPPFHvnunLhAngnzdKhBDUBJKdxG9LI6y4IEPuYzIAIhALeh2ATcuKmB3Gb0W8Z1NxB1CXXU0dh%2FFa8ir5ipi97pKvMECEQQARoMNjk5NzUzMzA5NzA1Igx7uebghH%2BQW3Ixrfoq0AS5%2FuNo9otdOlAQnsMoMi4XqtVRq28wGK4lQbmC%2BpxHs4M9v%2FGhqzp1eLaq6a86UaX222runzETQqluQE3QutSCUR9AyjQXmtFc9sQLsda99cNznSAAP9WRacWj0Szan%2BWCX9EschbfU8ge9O%2BNgUxCuWx%2FUNBxhrWvktTU8kKwgY3zKTlA9H%2BWIpSSk5K81BxWG5%2BmiUtSEbj%2F7r5%2BHSdtuM578QDTSNORjUXaqqgv6weyN58kbCCXuwb44Z3mKw4hJxTmjAqupy65VAB7DMH3yCwvg9Z1VLKTK8JrBZkvTPU%2FLNT%2B0kMPtFBrhdsqNt0BGA8DS2Y1I7AtydvvEXimawRRxpvcN2PPDKdoVK57l1h28p2leLc5Ob3E%2B6eXeHRJRoAFf6ZALK4pImlUIUP9l093EUtHzHQ5OjEc7MtUFnhVe2vJf9vt8CqbkoA38k1C70Ixts7%2F9bk3ww%2B0n8TFV%2FOJ8AgMpJNZEv%2BVicnPFn9tXfIcdn2%2FX6CesrtXy6vrcgTIld9ExSMUVfuqqtivxskbCwBTwTPUooxYZ5fEWfC69k2EgoxH4wDC0br8xg%2BBdV3jrJLLGUjVuZ%2FtUMJE0yqqnF8Z9nuGNtTlKKgttOvEUg1XHTRMXw3Bth4KLhMYisgjF66SPNyMxHZvZw0UvmWI%2BcYRt6qKv95%2BTjbGD8VtoUt2A%2B%2FyaSjzU7gGRd7mDRr8VLncVV6qR8jm7eNH9r1irvHVmuYUiKq%2FU2zQeAM%2Bu%2FufcH%2FP%2FJlYJl8n%2FDRDQUuyJ3gPqjSPe%2FyjtrvDMOWP2c8GOpcBCw946vHWWpRwEXwvxQkd61g30a6dZfieVfCpEVYI%2FDTHVc7yrxvrSy6Ecx%2F7b0D75HUwpXQLkNeP2nZITSw2qEg2eVd6D0Jn6JaZ91EkjiH6gFZEg5HAZO5%2Bnpi6xrS7jFjMTQ04vlHfV5Jz6H1zO8PDUqeyzh6WThtTrdbjcoxZBY2W%2FCxFtunzxLM8o63jzUmH%2FGUtGg%3D%3D&Expires=1777751480) - page-2 to streams address pieces of the puzzle, but none integrate AR guidance with interactive plan...

15. [AR Device Components: A Complete B2B Procurement Guide ...](https://seller.alibaba.com/blogs/2026/southeast-asia/electronics/ar-device-components-procurement-guide-alibaba-b2b) - Mordor Intelligence reports that the broader AR and VR headsets market is valued at USD 6.36 billion...

16. [Augmented Reality (AR) Market Breakdown: Four Big Trends from ...](https://www.abiresearch.com/blog/augmented-reality-market-trends) - According to ABI Research, the Augmented Reality (AR) hardware market size will grow by 64.8% Year-o...

17. [symvn-Current-AR-Market-Trends-research-4.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/104142404/2827cc87-5312-41e9-907b-c692509c5dad/symvn-Current-AR-Market-Trends-research-4.pdf?AWSAccessKeyId=ASIA2F3EMEYE63OKSDI2&Signature=%2FgFOUg6nVOIE9imEO3cNqf%2FE1fg%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHsaCXVzLWVhc3QtMSJIMEYCIQDcpPPFHvnunLhAngnzdKhBDUBJKdxG9LI6y4IEPuYzIAIhALeh2ATcuKmB3Gb0W8Z1NxB1CXXU0dh%2FFa8ir5ipi97pKvMECEQQARoMNjk5NzUzMzA5NzA1Igx7uebghH%2BQW3Ixrfoq0AS5%2FuNo9otdOlAQnsMoMi4XqtVRq28wGK4lQbmC%2BpxHs4M9v%2FGhqzp1eLaq6a86UaX222runzETQqluQE3QutSCUR9AyjQXmtFc9sQLsda99cNznSAAP9WRacWj0Szan%2BWCX9EschbfU8ge9O%2BNgUxCuWx%2FUNBxhrWvktTU8kKwgY3zKTlA9H%2BWIpSSk5K81BxWG5%2BmiUtSEbj%2F7r5%2BHSdtuM578QDTSNORjUXaqqgv6weyN58kbCCXuwb44Z3mKw4hJxTmjAqupy65VAB7DMH3yCwvg9Z1VLKTK8JrBZkvTPU%2FLNT%2B0kMPtFBrhdsqNt0BGA8DS2Y1I7AtydvvEXimawRRxpvcN2PPDKdoVK57l1h28p2leLc5Ob3E%2B6eXeHRJRoAFf6ZALK4pImlUIUP9l093EUtHzHQ5OjEc7MtUFnhVe2vJf9vt8CqbkoA38k1C70Ixts7%2F9bk3ww%2B0n8TFV%2FOJ8AgMpJNZEv%2BVicnPFn9tXfIcdn2%2FX6CesrtXy6vrcgTIld9ExSMUVfuqqtivxskbCwBTwTPUooxYZ5fEWfC69k2EgoxH4wDC0br8xg%2BBdV3jrJLLGUjVuZ%2FtUMJE0yqqnF8Z9nuGNtTlKKgttOvEUg1XHTRMXw3Bth4KLhMYisgjF66SPNyMxHZvZw0UvmWI%2BcYRt6qKv95%2BTjbGD8VtoUt2A%2B%2FyaSjzU7gGRd7mDRr8VLncVV6qR8jm7eNH9r1irvHVmuYUiKq%2FU2zQeAM%2Bu%2FufcH%2FP%2FJlYJl8n%2FDRDQUuyJ3gPqjSPe%2FyjtrvDMOWP2c8GOpcBCw946vHWWpRwEXwvxQkd61g30a6dZfieVfCpEVYI%2FDTHVc7yrxvrSy6Ecx%2F7b0D75HUwpXQLkNeP2nZITSw2qEg2eVd6D0Jn6JaZ91EkjiH6gFZEg5HAZO5%2Bnpi6xrS7jFjMTQ04vlHfV5Jz6H1zO8PDUqeyzh6WThtTrdbjcoxZBY2W%2FCxFtunzxLM8o63jzUmH%2FGUtGg%3D%3D&Expires=1777751480) - page-1

18. [Digital Work Instructions for Automotive Assembly Market - Dataintelo](https://dataintelo.com/report/digital-work-instructions-for-automotive-assembly-market) - According to our latest research, the global Digital Work Instructions for Automotive Assembly marke...

19. [Digital Work Instructions for Automotive Assembly Market Research ...](https://growthmarketreports.com/report/digital-work-instructions-for-automotive-assembly-market) - According to our latest research, the global Digital Work Instructions for Automotive Assembly marke...

20. [The Augmented Reality and Virtual Reality Industry 2026](https://blog.shayaikehassan.com/the-augmented-reality-and-virtual-reality-industry-an-in-depth-overview-in-2026) - AR campaigns generate engagement times four times longer than mobile video and a 70% higher memory r...

21. [Assembly Instructions - IKEA](https://www.ikea.com/us/en/customer-service/assembly-instructions-puba2cdc880/) - Just look for any product in the search bar above and find its assembly instruction available on the...

22. [Say Hej to IKEA Place](https://www.youtube.com/watch?v=UudV1VdFtuQ) - IKEA Place is our new app that lets you virtually “place” IKEA products in your space. It’s a new wa...

23. [IKEA assembly made easier through augmented-reality app - Dezeen](https://www.dezeen.com/2018/03/23/ikea-assembly-made-easier-through-augmented-reality-app/) - To use the app, users firstly scan the barcode on their furniture item. This then brings up an anima...

24. [Leveraging AR To Spatially Assemble IKEA Furniture](https://www.juanacape.com/design/ikea-assemble)

25. [I want you to do a financial breakdown for stock $NBIS, which is Nebios Group NV Class A. I want you to look at their financials, which they reported today per trading day, and look at the stock on the street if they have any news. Explain the current stock graph (SMA 20 is in pink, SMA 150 is not on screen but is at 107.49 which is out on the scale on the graph - to the lower end, . Attached, take a look.](https://www.perplexity.ai/search/92f2d6c5-5e92-436a-aa7f-7a4c61329d7b) - NBIS still looks like a high-expectation AI infrastructure name: the bigger trend is intact, but the...

26. [BILT - App Store - Apple](https://apps.apple.com/lb/app/bilt/id879452214) - Follow easy BILT instructions to fix a toilet, lay bathroom tile, paint a room, jump a car battery, ...

27. [BILT 3D Interactive Instructions Preview for iOS or Android - YouTube](https://www.youtube.com/watch?v=WcPceZ0Tagk) - ... BILT is the app for you. Free from the App Store and Google Play, BILT provides official 3D inte...

28. [Lyra - AI Personal Assistant](https://www.trylyra.com) - Try Lyra. Tap into thousands of AI specialists—book flights and restaurants, manage your calendar, a...

29. [Top 10 Augmented Reality Tools in 2026: Features, Pros, Cons ...](https://www.devopsschool.com/blog/top-10-augmented-reality-tools-in-2025-features-pros-cons-comparison/) - Top 10 Augmented Reality Tools in 2026 · 1. Microsoft HoloLens 2 · 2. Vuforia · 3. ARKit (Apple) · 4...

30. [Top 5 Popular AR Creator Apps & Best Use Cases - Kivicube](https://www.kivicube.com/post/ar-creator-app/) - This guide covers what AR creator apps can do, the best use cases, the top platforms, and why Kivicu...

31. [Web-Based AR vs. App-Based AR: Which Strategy Wins in 2026?](https://blog.cylindo.com/web-based-ar-vs-app-based) - This is why Web-native AR consistently outperforms app-based AR for conversion. It does not ask cust...

32. [[Agent] Lyra · Issue #1447 · lobehub/lobe-chat-agents - GitHub](https://github.com/lobehub/lobe-chat-agents/issues/1447) - You are Lyra, a master-level AI prompt optimization specialist. Your mission: transform any user inp...

33. [Lyra](https://lyra-omni.github.io) - We introduce Lyra, an efficient MLLM that enhances multi-modal abilities, including advanced long sp...

34. [Lyra: unlock AI agents for your team](https://withlyra.com) - Lyra turns messy, multiplayer context into one-shot, AI-executable specs, fine-tuned for coding, des...

35. [Lyra: Generative 3D Scene Reconstruction via Video Diffusion ...](https://arxiv.org/html/2509.19296v1) - We introduce Lyra, a novel method for generating explicit 3D environments from the latent representa...

36. [GitHub - anuragpoolakkal/lyra-ai: Lyra is a Voice Assistant App powered by ChatGPT and DALL-E](https://github.com/anuragpoolakkal/lyra-ai) - Lyra is a Voice Assistant App powered by ChatGPT and DALL-E - anuragpoolakkal/lyra-ai

37. [Lyra debuts AI therapy chatbot for lower risk mental health conditions](https://www.emarketer.com/content/lyra-debuts-ai-therapy-chatbot-lower-risk-mental-health-conditions) - Lyra Health is debuting a generative AI (genAI) chatbot for mild to moderate mental health challenge...

38. [A full Operator's Assistant Built Locally on Parrot OS : r/ParrotSecurity](https://www.reddit.com/r/ParrotSecurity/comments/1lcjn6h/showcase_aptlyra_a_full_operators_assistant_built/) - [SHOWCASE] APT‑LYRA: A full Operator's Assistant Built Locally on Parrot OS. Sorry, this post was de...

39. [AI Agent Protocols 2026: Complete Guide - Ruh AI](https://www.ruh.ai/blogs/ai-agent-protocols-2026-complete-guide) - In this guide, we will discover the three major protocols—MCP for agent-to-tool connections, A2A for...

40. [GitHub - JIA-Lab-research/Lyra: [ICCV 2025] Official Implementation ...](https://github.com/dvlab-research/Lyra) - Lyra shows superiority compared with leading omni-models in: Stronger performance: Achieve SOTA resu...

41. [Unity AR Foundation Tutorial : Make an AR app like IKEA ... - YouTube](https://www.youtube.com/watch?v=Ilajw3BR9Bc) - Unity AR Foundation Tutorial : Make an AR app like IKEA Place ** PART 1 -Placing an AR Object. 80K v...

42. [Best Multi-Agent Frameworks in 2026 - GuruSup](https://gurusup.com/blog/best-multi-agent-frameworks-2026) - Multi-agent systems need coordination primitives: how agents discover each other, share state, handl...

43. [How to Build an AR App for Android: A Step-by-Step Guide for 2026](https://inceptivesdigital.com/blog/android-ar-app-development) - Learn how to build an augmented reality app for Android devices step by step. Explore ARCore, Unity,...

44. [A comprehensive review of augmented reality-based instruction in ...](https://www.sciencedirect.com/science/article/abs/pii/S073658452200093X)

45. [Mobile Augmented Reality (ar) Market Size 2026 - LinkedIn](https://www.linkedin.com/pulse/mobile-augmented-reality-ar-market-size-2026-technology-4c1gf) - The Mobile Augmented Reality (ar) Market demonstrates strong, region-specific growth patterns shaped...

46. [Digital Work Instructions (AR Overlay) Market Future Prospects](https://htfmarketinsights.com/report/4372027-digital-work-instructions-ar-overlay-market) - Unlock new opportunities in Digital Work Instructions (AR Overlay) Market: the latest release from H...

47. [Augmented Virtual Reality AR VR Market Outlook 2026-2034](https://www.intelmarketresearch.com/global-augmentedvirtual-reality-forecast-market-26213) - The market is projected to grow from USD 1.93 billion in 2026 to USD 3.73 billion by 2034, exhibitin...

