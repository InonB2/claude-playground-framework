# BuildARPro — Scan-to-3D & AR Manual Tools Research
**Researcher:** Tomy  
**Date:** 2026-05-01  
**Purpose:** Landscape research for BuildARPro — an app that lets maintenance workers scan paper manuals and receive 3D AR step-by-step instructions overlaid on real equipment.

---

## Executive Summary

Three tool categories are relevant to BuildARPro:

1. **Photogrammetry / 3D scanning tools** — for converting physical objects into 3D models (MVP: used by in-house content team; future: possible consumer-facing scan flow).
2. **OCR / document parsing tools** — for extracting structured text and diagram data from paper manuals or PDFs.
3. **AR work-instruction platforms** — direct competitors or potential integration/partnership targets.

**Top 3 integration candidates for MVP and beyond:**
- **KIRI Engine API** — best accessible REST API for photogrammetry cloud processing; low cost; direct fit for MVP content pipeline.
- **LlamaParse (LlamaIndex)** — best tool for extracting structured data from scanned technical PDFs; multimodal, affordable, production-ready.
- **PTC Vuforia Engine** — best-in-class SDK for AR model-target tracking on industrial equipment; standard in the enterprise space.

---

## Category 1: Photogrammetry / 3D Reconstruction Tools

### 1.1 Polycam

| Attribute | Details |
|-----------|---------|
| What it does | Mobile LiDAR + photogrammetry scanning. Outputs GLTF, OBJ, USDZ, point clouds. |
| API availability | Yes — developer mode + REST pipeline (via Immersal integration). GitHub org exists. Enterprise tier with custom integrations. |
| Cost | Free (GLTF only). Pro: $12.99–$26.99/mo or $79.99–$199.99/yr. Enterprise: custom pricing. |
| MVP fit | Medium. Good for manually creating high-quality 3D scans of equipment. Requires Apple/Android device with LiDAR. |
| Full-product fit | High. Could be offered as the in-app scan flow for iOS users with Pro iPhones. |
| Notes | Enterprise security + custom API integrations available. Integrates with Revit, AutoCAD, Rhino, SketchUp. Actively developed as of 2026. |

**BuildARPro relevance:** Could be used by content team to create 3D equipment models quickly via tablet scan. Enterprise API makes it integratable. However, it is oriented toward architecture/BIM, not industrial equipment tracking.

---

### 1.2 Luma AI (Genie — Text-to-3D; Dream Machine — Video-to-3D)

| Attribute | Details |
|-----------|---------|
| What it does | Text-to-3D model generation (Genie) and video-to-3D/scene generation. Produces quad mesh geometry with materials. |
| API availability | Yes — Dream Machine API (credit-based). Genie API status unclear; redirects to main platform as of 2026. |
| Cost | Dream Machine: from $9.99/mo. API via credits. Genie specific pricing not publicly listed. |
| MVP fit | Low. Text-to-3D output quality is too generic for precise industrial equipment models. |
| Full-product fit | Low-Medium. Could assist with generating placeholder models or environments, not specific machine parts. |
| Notes | Luma AI photogrammetry app (original NeRF capture app) is no longer actively developed. Core platform shifted to generative AI. |

**BuildARPro relevance:** Low direct fit. Text-to-3D models will not accurately represent specific industrial machines. Not recommended for MVP or near-term roadmap.

---

### 1.3 KIRI Engine

| Attribute | Details |
|-----------|---------|
| What it does | Mobile photogrammetry + LiDAR scanning app (iOS/Android). Cloud-based mesh reconstruction. Also supports 3D Gaussian Splatting and AI-powered PBR material generation. |
| API availability | YES — documented RESTful API. GitHub SDK repo: `Kiri-Innovation/KIRI-ENGINE-SDK-API`. Full docs at docs.kiriengine.app. |
| Cost | Free basic (up to 70 photos/scan). Pro: $6.99/mo or $49.99/yr (200 photos, unlimited exports, DSLR/drone support). Enterprise: contact sales. |
| MVP fit | HIGH. REST API allows programmatic submission of photo sets and retrieval of 3D mesh output. Cloud processing — no GPU needed on our end. |
| Full-product fit | HIGH. Could become the backend scan engine for the "scan the machine" flow in BuildARPro. |
| Notes | KIRI Engine 4.0 (late 2025) introduced major photogrammetry + AI-PBR updates. Version 3.14 (April 2025) added AI-enhanced LiDAR scanning. Actively maintained. |

**BuildARPro relevance: STRONG.** This is the most accessible photogrammetry API in the consumer/prosumer space. At MVP, the content team can use KIRI Engine Pro to scan common machines and build the curated library. In a future automated flow, the KIRI Engine REST API could power a "scan your machine" feature directly in the app.

---

### 1.4 RealityScan (formerly RealityCapture by Epic Games)

| Attribute | Details |
|-----------|---------|
| What it does | Professional desktop photogrammetry software (Windows). Processes large datasets with high accuracy. Rebranded as RealityScan 2.0 in June 2025. |
| API availability | No public REST API. Integrates with Unreal Engine and Twinmotion. |
| Cost | Free for companies under $1M/yr revenue. $1,250/seat/yr for larger companies. |
| MVP fit | Medium. Best-quality output for the content team's library-building workflow. |
| Full-product fit | Low as a backend API — no programmatic API. |
| Notes | RealityScan 2.1 adds SLAM data import and AI-assisted masking. Industry standard for high-fidelity photogrammetry. |

**BuildARPro relevance:** Useful tool for the in-house content team to produce the highest-quality 3D equipment models for the curated library. Not integratable as a backend service.

---

### 1.5 Meshroom (Alice Vision — Open Source)

| Attribute | Details |
|-----------|---------|
| What it does | Open-source photogrammetry pipeline. Node-based. Runs locally. |
| API availability | No REST API. CLI-controllable. Can be wrapped in a custom server. |
| Cost | Free and open source. Requires GPU. |
| MVP fit | Low — requires infra setup and GPU. |
| Full-product fit | Low for SaaS. Medium for self-hosted internal pipeline. |
| Notes | Good for research and cost-conscious teams willing to manage infrastructure. |

**BuildARPro relevance:** Not recommended for MVP. Could be revisited if cost becomes a constraint and engineering capacity is available to build a self-hosted pipeline.

---

### 1.6 Apple Object Capture (RealityKit)

| Attribute | Details |
|-----------|---------|
| What it does | Apple's native photogrammetry API. Processes images taken on iPhone/iPad and generates USDZ/OBJ models. Runs on Apple silicon. |
| API availability | Yes — free as part of RealityKit framework (iOS/macOS SDK). Not available on Android or Windows. |
| Cost | Free (part of Apple developer program). |
| MVP fit | HIGH for iOS-first strategy. |
| Full-product fit | Medium — iOS/macOS only. |
| Notes | Research (PLOS One, 2025) validates research-quality output. Under 100 images, under 10 minutes. Vuforia has documented integration with Object Capture output. |

**BuildARPro relevance:** Strong candidate if BuildARPro is iOS-first. Enables native on-device or on-Mac model generation without third-party costs. Works natively with ARKit for AR display. Significant platform lock-in risk.

---

## Category 2: OCR and Technical Document Parsing Tools

### 2.1 AWS Textract

| Attribute | Details |
|-----------|---------|
| What it does | OCR + structured extraction (tables, forms, key-value pairs) from PDFs and images. |
| API availability | Yes — full REST API via AWS SDK (Python, Node.js, Java, .NET, etc.). |
| Cost | Detect Document Text: $0.0015/page (first 1M pages). Analyze Document (Tables): $0.015/page. Forms + Custom Queries: $0.065/page. |
| MVP fit | HIGH. Tables and forms are critical for extracting step-by-step instructions from manuals. |
| Full-product fit | HIGH. Industry-proven, AWS ecosystem integration, strong SLA. |
| Notes | 2026 Textract achieves 89% accuracy on degraded/low-resolution documents (up from 76% in 2024). Industry-leading table extraction with cell-level relationship mapping (82% accuracy on complex 6-column tables). |

**BuildARPro relevance:** Best candidate for extracting structured step sequences from scanned paper manuals. Particularly strong for tables (step/action/part number columns). Cost-effective at scale.

---

### 2.2 Google Document AI

| Attribute | Details |
|-----------|---------|
| What it does | ML-powered document parsing: OCR, entity extraction, layout understanding. Gemini-powered Layout Parser (Nov 2025). |
| API availability | Yes — Google Cloud REST/gRPC API. |
| Cost | Volume pricing drops to $0.60 per 1,000 pages for OCR at 5M+ pages/mo. Competitive with Textract at scale. |
| MVP fit | HIGH. 95.8% average OCR accuracy (vs. Textract 94.2% in benchmarks). |
| Full-product fit | HIGH. Gemini-powered layout understanding strong for complex document structures. |
| Notes | Weaker than Textract on complex table extraction (40% accuracy on multi-column tables in one benchmark). Better for general text and reading order. |

**BuildARPro relevance:** Strong alternative to Textract, especially for text-heavy manuals with prose instructions. Weaker for tabular data. Consider pairing with Textract (Textract for tables, Document AI for narrative text).

---

### 2.3 Adobe PDF Extract API

| Attribute | Details |
|-----------|---------|
| What it does | Extracts text, tables, and figures from PDFs using Adobe Sensei AI. Outputs structured JSON. Tables output as JSON + optional CSV/XLSX + PNG image per table. |
| API availability | Yes — REST API. SDKs for Node.js, Python, .NET, Java. |
| Cost | 500 free transactions/month. Paid: 1 transaction per 5 pages for Extract operations. Custom enterprise pricing. |
| MVP fit | MEDIUM-HIGH. Best for PDF-native manuals (not scanned images). |
| Full-product fit | HIGH. Deep structural awareness (spans, headings, reading order, figure bounding boxes). |
| Notes | Returns bounding boxes for figures and tables — useful for mapping diagram regions to instruction steps. 5-page chunks per transaction — watch cost at scale. |

**BuildARPro relevance:** Best tool when the input is a well-formed digital PDF manual (not a phone photo of paper). The figure bounding box output could be used to identify which diagram corresponds to which step — a useful bridge toward future AR overlay logic.

---

### 2.4 LlamaParse (LlamaIndex)

| Attribute | Details |
|-----------|---------|
| What it does | AI-native document parsing focused on producing AI-ready structured output. Supports 90+ formats. Multimodal: handles text, images, charts, tables. Layout-aware parsing. |
| API availability | Yes — Python and TypeScript SDKs. REST API. Integrates natively with LlamaIndex RAG pipelines. |
| Cost | Free tier available. Paid: 3 credits/page (Cost-Effective + basic LLM) up to 90 credits/page (Agentic Plus with frontier model). LlamaParse v2 (2025) offers up to 50% cost reduction vs. v1. |
| MVP fit | HIGH. Best at understanding complex document layouts including multi-column manuals and embedded diagrams. |
| Full-product fit | HIGH. Purpose-built for feeding extracted content into AI pipelines — natural fit for an AI-driven instruction system. |
| Notes | LlamaParse v2 launched 2025. LlamaExtract supports page-level schema extraction. LlamaSheets for spreadsheets. Can output structured JSON matching a custom schema (e.g., Step, Action, Part, Warning). |

**BuildARPro relevance: STRONG.** LlamaParse is uniquely suited to BuildARPro because it bridges OCR extraction and AI-structured output. You can define a schema (Step number, Action description, Part referenced, Safety warning) and get JSON output directly from a scanned manual. This is the closest thing to automated manual parsing currently production-ready.

---

## Category 3: AR Work Instruction Platforms (Competitors and Partners)

### 3.1 Scope AR — WorkLink

| Attribute | Details |
|-----------|---------|
| What it does | Enterprise AR platform for authoring and distributing 3D AR work instructions. Combines instructions + live remote assistance. |
| API availability | Yes — GraphQL API, webhooks, deeplinks. Integrates with PLM, MES, ERP, LMS systems. |
| Cost | Enterprise pricing only. Not publicly listed. |
| Target market | Large enterprise (aerospace, manufacturing, defense). |
| AR approach | CAD-based. Authors load existing 3D CAD files into the platform. |
| Notes | As of March 2026, publishes native CAD instantly across Windows, iOS, Android. AI-enabled work instruction creation. Smart glasses support. |

**BuildARPro position:** Direct competitor at the high end. Scope AR requires pre-existing 3D CAD data — it does not convert paper manuals. BuildARPro's differentiated angle is the paper-to-AR pipeline for companies that do not have CAD files. Scope AR is too expensive and heavyweight for SMB maintenance shops. **Potential partnership target** for enterprise upsell (Scope AR handles enterprise, BuildARPro handles SMB and legacy equipment).

---

### 3.2 PTC Vuforia Suite

| Attribute | Details |
|-----------|---------|
| What it does | Enterprise AR suite: Vuforia Engine (SDK), Vuforia Studio (authoring), Vuforia Expert Capture (knowledge capture), Vuforia Chalk (remote assist). |
| API availability | Vuforia Engine: SDK-based (no REST API). Vuforia Studio: web-based authoring. Model-based tracking is Vuforia's core strength. |
| Cost | Engine: Free basic. Premium and Enterprise: custom pricing. Studio and Expert Capture: enterprise SaaS contracts. |
| Target market | Manufacturing, industrial, automotive — mid to large enterprise. |
| AR approach | CAD and model-target based. Object Capture integration documented. |
| Notes | Industry standard for model-target tracking (recognizes physical equipment and overlays AR). Requires 3D model as the tracking target. |

**BuildARPro position:** Vuforia Engine is the most likely SDK to power BuildARPro's AR overlay layer itself. It is the industry standard for model-target AR tracking (identifying real equipment and overlaying instructions). **Vuforia is a technology enabler for BuildARPro, not a direct competitor** — unless BuildARPro moves upmarket. Consider building on Vuforia Engine SDK.

---

### 3.3 Taqtile Manifest

| Attribute | Details |
|-----------|---------|
| What it does | AI-powered digital work instruction platform. Digitizes legacy manuals using "Maker AI" (claims up to 80% content creation time reduction). AR overlays on HoloLens, iOS, Android. |
| API availability | Yes — open APIs for integration with business systems. |
| Cost | Not publicly listed. Enterprise SaaS. |
| Target market | Defense, manufacturing, field service. |
| AR approach | Mobile + HoloLens. 3D AR step-by-step instructions. |
| Notes | Available on Apple Vision Pro (2025). Claims to digitize paper-based work instructions. AI-assisted authoring. |

**BuildARPro position:** Taqtile is a direct and close competitor. Their "Maker AI" that digitizes legacy manuals is essentially the same value proposition as BuildARPro's manual scan pipeline. Key differentiator: Taqtile is still enterprise-first (defense contracts, HoloLens) — BuildARPro could win on simplicity and price for SMB/mid-market maintenance teams. **Monitor closely.**

---

### 3.4 LightGuide

| Attribute | Details |
|-----------|---------|
| What it does | Projected AR work instructions. Uses overhead projectors to overlay instructions directly onto workbenches/equipment. AI computer vision + analytics. |
| Cost | Not publicly listed. Hardware + software bundle. |
| Target market | Assembly lines, manufacturing floors. Fixed workstation use. |
| Notes | Different delivery mechanism (projected AR, not mobile/wearable). Not directly competitive with BuildARPro's tablet/phone approach. |

**BuildARPro position:** Not a direct competitor. Different deployment model (fixed projector vs. mobile). Low relevance.

---

### 3.5 Wikitude AR SDK

**Status: DISCONTINUED.** As of September 21, 2024, all Wikitude services and subscriptions have been shut down. No longer a relevant competitor or integration option.

---

### 3.6 Other AR Work Instruction Players (Tier 2)

| Tool | Notes | BuildARPro Relevance |
|------|-------|---------------------|
| Dozuki | Digital SOPs for manufacturing. Text + video, not AR. | Low |
| Tulip | No-code manufacturing apps. Workflow + data, not AR overlay. | Low |
| Augmentir | AI-connected worker platform. Some AR features. | Medium — monitor |
| Proceedix | Digital work instructions. Limited AR. | Low |
| Parsable | Connected worker platform. No AR overlay. | Low |

---

## Integration Candidates: Ranked for BuildARPro

### Tier 1 — Recommended for MVP and Near-Term

| Rank | Tool | Category | Why |
|------|------|----------|-----|
| 1 | **KIRI Engine API** | 3D Scanning | REST API, cloud processing, low cost ($6.99/mo pro), photogrammetry + LiDAR, actively developed, SDK on GitHub. Best for content team building the curated equipment library and future consumer scan flow. |
| 2 | **LlamaParse** | OCR / Document Parsing | Purpose-built for AI-ready structured extraction. Define a schema (step/action/part/warning), get JSON from a scanned manual. Multimodal — handles diagrams. v2 API affordable and production-ready. Bridge between paper manual and structured AR instruction data. |
| 3 | **PTC Vuforia Engine SDK** | AR Overlay | Industry standard for model-target AR tracking. Free basic plan. Well-documented. Recognized physical equipment and overlays AR instructions. The tracking backbone BuildARPro needs. Not a backend API — it is the AR rendering/tracking layer in the app itself. |

### Tier 2 — Strong for Full Product / Future Roadmap

| Rank | Tool | Category | Why |
|------|------|----------|-----|
| 4 | **AWS Textract** | OCR / Document Parsing | Best table extraction for structured manuals. Cost-effective at scale. Use for step-numbered manuals with tabular layouts. |
| 5 | **Apple Object Capture** | 3D Scanning | Free, native, high quality — if iOS-first. No additional API costs. Natural pipeline from iPhone photo set to USDZ model to ARKit overlay. |
| 6 | **Adobe PDF Extract API** | OCR / Document Parsing | Best for PDF-native digital manuals. Figure bounding boxes useful for diagram-to-step mapping. 500 free transactions/month for prototyping. |

### Tier 3 — Monitor / Avoid

| Tool | Decision |
|------|----------|
| Luma AI (Genie) | Too generic for industrial models. Low fit. |
| RealityScan / RealityCapture | Great quality but no API. Desktop only. Use manually, not integrated. |
| Meshroom | Open source but no hosted API. Infra overhead too high for MVP. |
| Wikitude | Discontinued. Avoid. |
| Google Document AI | Solid alternative to Textract but weaker on tables. Secondary choice. |
| Scope AR | Enterprise-only competitor. Too expensive for BuildARPro's target market. |
| Taqtile Manifest | Closest competitor. Watch positioning carefully. |

---

## What This Means for BuildARPro

### MVP Path (Curated Library Approach)

BuildARPro's MVP strategy — humans build 3D models for the most common machines — is validated by the landscape. No existing tool automates paper-manual-to-3D at production quality today. The path is:

1. **Content team uses KIRI Engine Pro or RealityScan** to physically scan common industrial machines and generate 3D models.
2. **LlamaParse processes the paper/PDF manual** into a structured JSON: `[{step: 1, action: "Remove cover panel", part: "Cover-A", warning: null}, ...]`
3. **Vuforia Engine (or ARKit)** tracks the physical machine and overlays the step sequence in AR on the worker's tablet/phone.

This three-tool stack is affordable, production-ready today, and avoids any research-grade automation.

### Future Path (Automated Scan-to-AR)

The fully automated "scan a paper manual → auto-generate AR overlay" pipeline is **research-grade today** but getting closer. The steps that are production-ready:
- OCR of manual pages: Ready (Textract, LlamaParse).
- Extraction of step sequences into structured JSON: Ready (LlamaParse v2 with custom schema).
- 3D reconstruction from images: Functional (KIRI Engine API, Object Capture) but requires deliberate photo capture of the machine, not just a casual phone scan.
- Automatic correspondence of manual steps to 3D model geometry: **Not production-ready.** This is the remaining hard research problem.

The most promising shortcut on the roadmap: **LlamaParse extracts steps + diagram bounding boxes from the manual** → steps are displayed as AR text overlays anchored to the 3D model (without needing to solve diagram-to-geometry correspondence). This is achievable within 12 months.

### Competitive Moat

BuildARPro's differentiation vs. Scope AR / Taqtile Manifest:
- **Simpler onboarding** — no CAD files required. Works with a phone photo and a paper manual.
- **SMB price point** — enterprise competitors are $50K+/yr. BuildARPro can price at $99–$499/mo.
- **Mobile-first** — no HoloLens required. Works on any smartphone.

The risk: Taqtile's Maker AI is explicitly targeting the same "digitize legacy manuals" use case. BuildARPro needs to move fast to establish the brand and distribution before Taqtile moves downmarket.

---

## Sources

- [KIRI Engine Pricing](https://www.kiriengine.app/pricing)
- [KIRI Engine API Docs](https://docs.kiriengine.app/)
- [KIRI Engine SDK GitHub](https://github.com/Kiri-Innovation/KIRI-ENGINE-SDK-API)
- [KIRI Engine 4.0 Release](http://www.kiriengine.app/blog/kiri-engine-4.0-release)
- [Polycam Pricing](https://poly.cam/pricing)
- [Polycam Developer Mode](https://learn.poly.cam/hc/en-us/articles/34295907278996-How-to-Access-Developer-Mode)
- [Luma AI Pricing](https://lumalabs.ai/pricing)
- [Apple Object Capture Documentation](https://developer.apple.com/documentation/realitykit/realitykit-object-capture/)
- [RealityScan Licensing](https://www.realityscan.com/en-US/license)
- [AWS Textract Pricing](https://aws.amazon.com/textract/pricing/)
- [AWS Textract vs Google Document AI 2026](https://www.braincuber.com/blog/aws-textract-vs-google-document-ai-ocr-comparison)
- [Adobe PDF Extract API](https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/)
- [Adobe PDF Services Pricing](https://developer.adobe.com/document-services/pricing/main/)
- [LlamaParse v2 Launch](https://www.llamaindex.ai/blog/introducing-llamaparse-v2-simpler-better-cheaper)
- [LlamaIndex Pricing](https://www.llamaindex.ai/pricing)
- [Scope AR WorkLink](https://www.scopear.com/product)
- [PTC Vuforia Engine Pricing](https://developer.vuforia.com/library/vuforia-engine/FAQ/pricing-and-licensing-options/)
- [PTC Vuforia Work Instructions](https://www.ptc.com/en/technologies/augmented-reality/work-instructions)
- [Taqtile Manifest](https://taqtile.com/manifest/)
- [Wikitude Discontinued](https://en.wikipedia.org/wiki/Wikitude)
- [Best AR Companies 2026](https://treeview.studio/blog/best-augmented-reality-ar-companies)
- [Alternatives to Paper Work Instructions 2026](https://manual.to/5-effective-alternatives-to-paper-based-work-instructions-for-manufacturing/)
