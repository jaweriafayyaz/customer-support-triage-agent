# 🤖 Customer Support Ticket Triage Agent
### Agentic AI system for classifying, retrieving policy, and drafting support replies, powered by LangGraph + FAISS + Groq LLM

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-blue?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

---

## 🎯 Overview

An agentic AI system that automates the repetitive first step of customer support: reading a ticket, classifying it, retrieving the correct policy, and drafting a reply, while keeping a human in the loop on anything sensitive or uncertain.

Customers submit a ticket through a simple form. Behind the scenes, the agent classifies it, retrieves the matching policy via semantic search, drafts a response, and either auto-approves it or flags it for a human agent to review.

**Real-world tested result: 90% classification accuracy (9/10) against a live Groq API.**

---

## 🏗️ Architecture

Ticket → Classify (LLM) → Retrieve (FAISS) → Draft (LLM) → Decide (rules) → Log

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | LangGraph | Chains classify → retrieve → draft → decide as a state graph |
| **Retrieval** | FAISS | Real vector search over policy/FAQ documents |
| **LLM** | Groq (openai/gpt-oss-20b) | Classifies tickets and drafts replies |
| **Validation** | Pydantic | Enforces structured, validated I/O on every node |
| **Backend** | Flask | Two-route interface, customer form + agent dashboard |

---

## ✨ Features

- 🎫 Real customer-facing ticket submission form (`/submit`)
- 🖥️ Internal agent dashboard showing category, confidence, and draft reply (`/agent-dashboard`)
- 🔍 Real FAISS semantic search over policy documents
- 🤖 Fast LLM classification + drafting via Groq
- 🛡️ Confidence-gated auto-approval, Refunds always require human sign-off
- 🔁 Retry logic + graceful fallbacks on LLM failures
- 📊 Built-in evaluation harness, accuracy, latency, manual-touch rate
- 🧪 Mock mode, fully testable/demoable with zero API key

---

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/jaweriafayyaz/customer-support-triage-agent.git
cd customer-support-triage-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
cp .env.example .env
```
Add your Groq key and set `MOCK_MODE=false`, or leave `MOCK_MODE=true` to test with zero API keys.

### 5. Run
```bash
python app.py
```
Open → **http://localhost:5000**

---

## 🔑 API Key (Free)

| API | Get Key |
|-----|---------|
| Groq | [console.groq.com](https://console.groq.com) |

---

## 💬 Example Tickets

- *"My card was charged twice for order #4521"* → Billing, auto-approved
- *"I want a refund, item arrived damaged"* → Refund, flagged for human review
- *"App crashes every time I try to log in"* → Technical, auto-approved
- *"Do you offer student discounts?"* → General, auto-approved

---

## 📁 Project Structure

\`\`\`
customer-support-triage-agent/
├── app.py                          ← Flask app (/submit + /agent-dashboard)
├── pipeline.py                     ← LangGraph orchestration
├── faiss_retriever.py              ← Real FAISS retrieval
├── llm_client.py                   ← Groq LLM wrapper (retries, mock mode)
├── schemas.py                      ← Pydantic I/O contracts
├── config.py                       ← Loads settings from .env
├── run_test_set.py                 ← 10-ticket batch test runner
├── eval_day4.py                    ← Evaluation harness
├── templates/
│   ├── submit.html                 ← Customer-facing form
│   └── agent_dashboard.html        ← Internal agent view
├── .env.example
└── README.md
\`\`\`

## 📊 Evaluation Results

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90%** (real Groq API) |
| Manual-touch Rate | 70% (Refunds + low-confidence always reviewed) |
| Latency | ~0.5-2s/ticket (real API) |

Full failure analysis, root causes, and before/after regression in [`day4_evaluation.md`](day4_evaluation.md).

---

## 📄 Full Documentation

- [`day1_discovery_baseline.md`](day1_discovery_baseline.md), target user, workflow map, baseline
- [`day2_design.md`](day2_design.md), architecture, schemas, tool rationale
- [`day4_evaluation.md`](day4_evaluation.md), results, failure analysis, real-LLM verification
- [`CASE_STUDY.md`](CASE_STUDY.md), full write-up
---

## 📞 Contact

- 📧 jaweriafayyaz474@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/jaweria-fayyaz/)
- 🐙 [GitHub](https://github.com/jaweriafayyaz)

---

<div align="center">

⭐ Star this repo if it helped you.

**Built with ❤️ by Jaweria Fayyaz**

</div>
