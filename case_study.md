# Case Study: Customer Support Ticket Triage Agent
---

## User & Problem

**Target user:** a small D2C e-commerce support team (2-3 agents) handling
50-80 tickets/day across billing, refunds, shipping, and technical issues.
(Stated assumption: Representative proxy workflow, real client data wasn't available)

**The problem:** every ticket requires the same repetitive sequence
read it, decide its category, check the relevant policy doc, write a first
response, costing an estimated 3-5 minutes of agent time per ticket, with
inconsistent quality depending on agent fatigue and FAQ familiarity.

---

## Existing Workflow & Bottleneck

Ticket arrives → agent reads and judges category/urgency/tone → agent checks
internal FAQ/policy doc → agent drafts a reply → sensitive cases (refunds,
complaints) get a second review from a senior agent → reply sent, ticket logged.

The bottleneck is the manual **classify + retrieve + draft** loop repeated
dozens of times a day, a mechanical task that still requires a human doing
all of it from scratch every single time.

---

## Scope Decisions & Non-Goals

**In scope (initial version, v1):** text-based tickets, 6 categories (Billing, Refund, Shipping,
Technical, General, Unroutable), FAISS-based policy retrieval, confidence-gated
auto-approval, a Flask form as the interface, full logging for evaluation.

**Explicit non-goals:** no live helpdesk/CRM API integration, no multi-language
support, no voice/chat channels, no fully autonomous sending (a human always
has final say before a reply actually goes out, even on "auto-approved" tickets),
no custom-trained model, off-the-shelf LLM + prompt engineering only.

These boundaries were chosen specifically to keep the project scope honest and
achievable rather than promising a production helpdesk replacement.

---

## Architecture & Major Trade-offs
Ticket → Classify (LLM) → Retrieve (FAISS) → Draft (LLM) → Decide (rules) → Log
Orchestrated with **LangGraph** so each node can be extended/retried
independently later. Retrieval uses a **real FAISS index** (TF-IDF vectors for
initial version (v1), swappable for Gemini/OpenAI embeddings without touching the FAISS code).
The LLM layer (**Groq**) includes retry logic and a `MOCK_MODE`
fallback, so the system is fully testable/demoable without a live API key.

**Key trade-off:** confidence threshold (0.85) plus a hard rule that Refunds
*always* require human review, chosen deliberately to prioritize safety over
automation rate, this system is a triage assistant, not an autonomous agent
that sends replies unsupervised.

---

## Work Delegated to AI vs. Judgment Retained by Humans

**Delegated to AI:** reading and classifying ticket text, retrieving the
matching policy snippet, drafting the first-response language.

**Retained by humans:** final send decision on every ticket (even
"auto-approved" ones, in this v1 scope), all Refund decisions, anything below
the confidence threshold, and all judgment calls about *which* categories,
thresholds, and non-goals the system should have in the first place.

---

## Failures, Changes, Results, and Limitations

Full detail in `evaluation_results.md`. Summary: after a first proxy-user test
run surfaced 2 real bugs (empty tickets misclassified, no Technical category
branch), fixing both raised mock-mode test-set accuracy from **60% to 80%**
(6/10 → 8/10), with the manual-touch rate at 40% (Refunds and low-confidence
tickets always route to a human, by design).

**Update, verified against the real Groq API:** once a live API key was
connected, real-LLM accuracy came in at **90% (9/10)**, higher than the mock
classifier, and it correctly handled both cases the mock classifier couldn't
(a Roman Urdu ticket, and a spam ticket), confirming those were mock-classifier
limitations rather than fundamental system limits (see `evaluation_results.md`,
Section 7). Cost-per-ticket is the one metric still not measured.

**Further hardening:** a safety-net rule was added so any ticket mentioning "refund" is routed to human review regardless of its assigned category, raising the manual-touch rate from 30% to 40% by correctly catching a ticket (T-6) that could otherwise have been auto-approved under a misleading category. Full detail in `evaluation_results.md`, Section 8.

---

## Adoption & Quality Metrics, Tracking Plan for First Two Weeks Post-Deployment

*(This system has not yet been deployed to a live team as of this write-up,
the metrics below are the tracking plan to run once it is, not reported results.)*

| Metric | How it will be tracked |
|---|---|
| Tickets processed/day | Count of rows in `results.csv` |
| Auto-approval rate | % of tickets with `action = auto_approved` |
| Agent override rate | % of "auto-approved" drafts the agent edits before sending |
| Classification accuracy | Spot-check a random 10% sample against agent judgment weekly |
| Time saved per ticket | Compare agent's self-reported time-to-send vs. the manual baseline |

---

## Next Two-Week Iteration Plan

1. ~~Week 1: connect a real Groq API key and re-run the full eval suite live~~ — **done**, see `evaluation_results.md` Section 7 (90% real-LLM accuracy).
2. **Week 1:** measure real cost-per-ticket and latency under production-like ticket volume.
3. **Week 1:** add the agent-override feedback checkbox to the UI to start measuring real-world draft-acceptance rate.
4. **Week 2:** expand the FAQ/policy knowledge base beyond the 3 seed categories and re-measure retrieval quality with a larger document set.