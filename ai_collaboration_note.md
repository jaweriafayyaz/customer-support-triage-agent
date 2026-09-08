# AI Collaboration Note

## AI Tools Used and Their Role

- **Claude (Anthropic):** used as a coding assistant under my direction, I
  defined the workflow to build (customer support triage), the architecture
  decisions (LangGraph orchestration, FAISS retrieval, confidence-gated
  approval), and the scope/non-goals for the project. Claude
  executed these instructions, generating code scaffolding, drafting
  documentation structure, and producing synthetic test tickets to my
  specification, which I then reviewed, ran, tested, and corrected myself.
- **Groq (LLM API):** the production classifier and drafter model the system
  calls at runtime, this is the model doing the actual ticket classification
  and reply-drafting once deployed, separate from Claude's role as a build
  assistant.

## Work Delegated to AI (under my direction)

- Writing first-draft code for modules I specified (schemas, retriever,
  pipeline, Flask app, evaluation harness) based on the architecture I chose
- Drafting synthetic test tickets and category labels I designed the test
  plan for
- Producing first-draft documentation structure, which I reviewed and edited

## How I Verified AI-Generated Results

- I ran every module myself, the pipeline end-to-end on a sample ticket,
  then the full 10-ticket test set, and inspected the output personally to
  confirm accuracy numbers, confusion cases, and CSV logs were real
- I manually reviewed the failure output from the first test run, identified
  two root causes myself, and directed the fixes (documented in
  `llm_client.py`)
- I connected my own Groq API key and re-ran the test set to verify results
  against the real LLM, not just the mock classifier, confirming 90%
  real-world accuracy
- I manually checked every category assignment, confidence score, and action
  decision against the expected labels I defined at the start

## Important Results I Rejected or Corrected

- I caught two classifier bugs (empty-ticket misclassification, missing
  Technical category) myself through manual testing and directed the fixes, 
  see `evaluation_results.md`, Failures 1 & 2
- I rejected the framing that the system "beats" manual accuracy, I set the
  honest comparison as ~80-90% AI accuracy vs. ~95% assumed human accuracy,
  making clear the system's value is speed and consistency, not superior
  judgment
- I identified that two documented mock-mode limitations (non-English
  tickets, spam) no longer applied once I tested against the real API, and
  updated the documentation to reflect that correction transparently

## Core Decisions I Personally Owned

- Choosing customer support triage as the project workflow
- Setting the confidence threshold (0.85) and the hard rule that Refunds
  always require human sign-off, my deliberate safety-over-automation
  trade-off
- Designing the two-route interface split (customer-facing `/submit` vs.
  internal `/agent-dashboard`) to keep internal triage details away from
  customers
- Defining all scope/non-goal boundaries (English-only baseline, no live
  helpdesk integration, no autonomous sending) that keep this a realistic initial version.
- Identifying the T-7 auto-approval gap and designing a keyword-based safety net (any "refund" mention routes to human review) as defense-in-depth beyond category-based rules alone