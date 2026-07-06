"""
generate_newsletter.py
Calls the DeepSeek API with the master prompt for Day X and saves
the resulting HTML newsletter to newsletter_output.html
"""

import os
import sys
import json
import time
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.environ["DEEPSEEK_API_KEY"]
CURRENT_DAY = int(os.environ.get("CURRENT_DAY", "1"))
OUTPUT_FILE = "newsletter_output.html"

# ---------------------------------------------------------------------------
# Master prompt (injected with the current day)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are a Senior Software Engineer, Backend Engineer, and AI Engineer with experience mentoring engineers into SDE-2 roles at companies such as Salesforce, Microsoft, Amazon, Atlassian, Oracle, Adobe, Walmart Global Tech, JPMorgan, and Google.

You are mentoring one engineer through a structured 30-Day Backend & Agentic AI Bootcamp.

The student's primary goal is to crack SDE-2 Backend Engineer interviews while developing production-ready engineering skills.

Your job is NOT to impress with unnecessary complexity.

Your job is to explain difficult engineering concepts clearly, intuitively, and progressively.

Assume the student has basic Java knowledge but wants to deeply understand how things work internally.

Every explanation should help the student:

• Understand the intuition behind the concept.
• Understand why the concept exists.
• Understand how it works internally.
• Implement it confidently in Java/Spring Boot.
• Debug common production issues.
• Answer SDE-2 interview questions.

Avoid Principal Engineer, Staff Engineer, or Architect-level assumptions unless specifically requested.

Teach first.
Optimize for understanding.
Then gradually increase technical depth throughout the 30-day bootcamp.
"""
def build_user_prompt(day: int) -> str:
    return f"""Generate Day {day} of 30 for the 30-Day Backend & Agentic AI Bootcamp newsletter.

## CORE RULES (Non-Negotiable)
1. This is Day {day} — generate ONLY Day {day} content.
2. Treat every newsletter issue as the next chapter of one continuous engineering book — not a standalone piece.
3. Never repeat major concepts already covered on previous days.
4. Assume the reader already understands everything from previous days — do not re-explain past material.
5. Increase technical depth every day. Day 10 must be harder than Day 5; Day 20 harder than Day 10, and so on.
6. Always prioritize production engineering over academic/textbook explanations.
7. Generate the most comprehensive newsletter possible within the model's maximum response length.
8. Do not waste tokens on introductions, disclaimers, or motivational filler — get straight into content.
9. If the response must be shortened due to length limits, cut content in this exact priority order (cut from the bottom first):
   1. System Design (protect this first — cut last)
   2. Backend
   3. Agentic AI
   4. Industry Pulse
   5. Challenges
   6. Revision
   7. Tomorrow Preview

## OBJECTIVE
Produce a premium HTML engineering newsletter with the quality and voice of:
- Stripe Engineering, Netflix Tech Blog, Uber Engineering, Databricks Engineering
- ByteByteGo, Martin Kleppmann's writing, Google Engineering blog

Target estimated reading time: 15–20 minutes.

---

## SECTION 1 — 📈 Progress Dashboard
Must include:
- Day {day} / 30
- A visual progress bar (HTML/CSS)
- List of previously completed topics
- Today's specific learning objectives
- Estimated reading time for this issue

---

## SECTION 2 — ☕ Backend Engineering
Exactly FIVE topics for Day {day}, pulled from the curriculum map below.

Every single topic must cover all of the following:
- Definition
- Why this concept exists (the underlying problem it solves)
- Internal working (mechanics, not just surface description)
- How Java/Spring implements it
- Production example
- Real debugging story
- Common mistakes
- Performance implications
- Trade-offs
- Interview questions
- Best practices
- Senior Engineer Notes

### Backend Curriculum Map
Days 1–5 — Java Internals: JVM, Memory, Garbage Collection, Collections, Generics, Concurrency, Networking
Days 6–10 — Spring Core: IoC, Dependency Injection, Spring Boot, REST, Validation, Testing, JPA, Hibernate, Transactions
Days 11–15 — Data & Messaging: SQL, Execution Plans, Indexes, Redis, Caching, Kafka, RabbitMQ, Database Scaling
Days 16–20 — Infra & Ops: Docker, Kubernetes, CI/CD, AWS, Logging, Metrics, Tracing, Observability, Deployment
Days 21–25 — Distributed Systems: CAP Theorem, Replication, Sharding, Consistency, Consensus, Circuit Breakers, Load Balancing, Rate Limiting, Resilience
Days 26–30 — Security & Performance: Authentication, Authorization, OAuth2, JWT, Security, Performance Tuning, JVM Profiling, Production Debugging, Architecture Review

---

## SECTION 3 — 🤖 Agentic AI
Exactly FIVE topics for Day {day}, pulled from the curriculum map below.

Every single topic must cover all of the following:
- Definition
- Internal Working
- Architecture
- Production Example
- Failure Modes
- Scaling
- Cost Considerations
- Latency
- Prompt Examples
- Implementation Tips
- Interview Questions
- Senior Engineer Notes

### AI Curriculum Map
Days 1–5 — LLM Foundations: Transformers, Attention, Tokens, Embeddings, Prompt Engineering, LLM Internals
Days 6–10 — Retrieval Foundations: Vector Databases, Chunking, Semantic Search, Embeddings, RAG
Days 11–15 — Advanced Retrieval & Tooling: Advanced RAG, Hybrid Search, Reranking, Tool Calling, Function Calling, MCP
Days 16–20 — Agent Cognition: Memory, Planning, LangGraph, Reflection, Reasoning, Workflow Orchestration
Days 21–25 — Multi-Agent & Safety: Multi-Agent Systems, Guardrails, Evaluation, Observability, AI Security, Prompt Engineering at Scale
Days 26–30 — Production AI: LLMOps, Inference, Optimization, Monitoring, Production Deployment, Cost Engineering, AI System Design

---

## SECTION 4 — 🌍 Industry Pulse
Exactly FIVE items. These must teach a lesson, not just report news.
Each item must explain:
1. What happened
2. Why it matters
3. The engineering lesson to take away

---

## SECTION 5 — 🏗 Daily System Design (MOST IMPORTANT SECTION)
Allocate approximately 40% of the entire newsletter to this section.
The day's system design problem must align with the 30-day curriculum progression.
Answer exactly as a Staff Engineer would in a live System Design interview.

Must include all 20 of the following components, in order:
1. Problem Statement
2. Assumptions
3. Functional Requirements
4. Non-Functional Requirements
5. Capacity Estimation — with shown calculations for: Users, Requests/sec, Peak traffic, Read/write ratio, Storage per day, Storage per year, Bandwidth, Monthly cloud cost
6. API Design
7. Database Design — tables, indexes, relationships, partitioning
8. High-Level Architecture
9. Component Responsibilities — Gateway, Services, Redis, Kafka, Database, Workers
10. Request Flow — step-by-step walkthrough explaining why each component exists
11. Data Flow
12. Scaling Strategy — explicitly walk through 10K → 1M → 100M → 1B users, explain when/why architecture changes at each stage
13. Failure Handling — Redis failure, Database failure, Kafka failure, Region failure, and recovery strategy for each
14. Monitoring — metrics, tracing, logging, alerts
15. Security
16. Disaster Recovery
17. Trade-offs
18. Infrastructure Cost Estimation
19. Common Interview Follow-up Questions
20. What Interviewers Expect (what separates a strong answer from a weak one)

---

## SECTION 6 — 💻 Backend Coding Challenge
One hands-on implementation problem tied to today's backend topics.

---

## SECTION 7 — 🤖 AI Challenge
One practical, hands-on AI engineering implementation challenge tied to today's AI topics.

---

## SECTION 8 — 🔁 Revision Corner
Exactly FIVE questions drawn from previous days' material (not today's).
(If this is Day 1, skip this section.)

---

## SECTION 9 — 📅 Tomorrow Preview
Exactly THREE bullet points previewing Day {day + 1 if day < 30 else 1}'s content.

---

## FORMATTING REQUIREMENTS
Output must be beautiful HTML suitable for rendering in Gmail. Use:
- Modern typography (system fonts: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif)
- Card-based layout with box shadows and rounded corners
- Tables where appropriate
- Syntax-highlighted code blocks (use <pre><code> with background #1e1e1e, color #d4d4d4)
- Architecture diagrams built with HTML/CSS (divs, flexbox, borders — no external images)
- Professional spacing and visual hierarchy
- Colored callout boxes:
  * Interview Tips: blue (#e3f2fd background, #1565c0 border-left)
  * Production Notes: orange (#fff3e0 background, #e65100 border-left)
  * Senior Engineer Notes: purple (#f3e5f5 background, #6a1b9a border-left)
- Responsive layout (max-width: 800px, centered)
- Progress bar using HTML/CSS (div with gradient background)
- Section headers with emoji and colored accent borders
- The entire output must be a single complete HTML document starting with <!DOCTYPE html>

The final result should read like a premium engineering magazine issue — never like raw AI-generated notes."""


# ---------------------------------------------------------------------------
# API call with retry logic
# ---------------------------------------------------------------------------
def call_deepseek(day: int, max_retries: int = 3) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(day)},
        ],
        "max_tokens": 8192,
        "temperature": 0.7,
        "stream": False,
    }

    for attempt in range(1, max_retries + 1):
        print(f"[generate] Attempt {attempt}/{max_retries} — calling DeepSeek for Day {day}...")
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=300,  # 5-minute timeout for long responses
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {})
            print(f"[generate] Success — tokens used: {tokens_used}")
            return content

        except requests.exceptions.Timeout:
            print(f"[generate] Timeout on attempt {attempt}.")
        except requests.exceptions.HTTPError as e:
            print(f"[generate] HTTP error on attempt {attempt}: {e.response.status_code} {e.response.text}")
            if e.response.status_code in (400, 401, 403):
                # Non-retriable errors
                raise
        except Exception as e:
            print(f"[generate] Unexpected error on attempt {attempt}: {e}")

        if attempt < max_retries:
            wait = 15 * attempt
            print(f"[generate] Waiting {wait}s before retry...")
            time.sleep(wait)

    raise RuntimeError(f"Failed to generate newsletter after {max_retries} attempts.")


# ---------------------------------------------------------------------------
# Post-processing: ensure output is valid HTML
# ---------------------------------------------------------------------------
def ensure_html(content: str) -> str:
    """
    DeepSeek sometimes wraps its output in a markdown code fence.
    Strip it if present and ensure we have a complete HTML document.
    """
    content = content.strip()

    # Strip markdown code fences
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Ensure we have a proper HTML document
    if not content.lower().startswith("<!doctype"):
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>30-Day Bootcamp — Day {CURRENT_DAY}</title>
</head>
<body>
{content}
</body>
</html>"""
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"[generate] Generating newsletter for Day {CURRENT_DAY}...")

    html_content = call_deepseek(CURRENT_DAY)
    html_content = ensure_html(html_content)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    size_kb = len(html_content.encode("utf-8")) / 1024
    print(f"[generate] Saved to {OUTPUT_FILE} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
