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
# Full 30-day curriculum — Backend and AI topics per day
# ---------------------------------------------------------------------------

BACKEND_CURRICULUM = {
    1:  ("JVM Fundamentals",          ["Why JVM Exists", "JVM Architecture", "Class Loading Process", "Bytecode Execution", "JIT Compiler", "JVM Memory Overview"]),
    2:  ("Memory Management",         ["Heap", "Stack", "Metaspace", "Object Creation", "String Pool", "Memory Leaks", "OutOfMemoryError"]),
    3:  ("Garbage Collection",        ["Why GC Exists", "Mark & Sweep", "Generational GC", "G1 GC", "ZGC Overview", "GC Tuning Basics"]),
    4:  ("Collections Framework",     ["ArrayList", "LinkedList", "HashMap Internals", "HashSet", "TreeMap", "ConcurrentHashMap", "Time Complexities"]),
    5:  ("Java Concurrency",          ["Threads", "Thread Lifecycle", "Synchronization", "Locks", "ExecutorService", "Thread Pools", "CompletableFuture"]),
    6:  ("Spring Framework Fundamentals", ["Spring Architecture", "IoC", "Dependency Injection", "Bean Lifecycle", "Spring Context"]),
    7:  ("Spring Boot",               ["Auto Configuration", "Starters", "Configuration", "Profiles", "Spring Boot Project Structure"]),
    8:  ("REST APIs",                 ["REST Principles", "HTTP Methods", "Controllers", "Validation", "Exception Handling", "API Design Best Practices"]),
    9:  ("Spring Data JPA & Hibernate", ["ORM", "Entity Lifecycle", "Relationships", "Lazy vs Eager Loading", "Cascade Types", "N+1 Problem"]),
    10: ("Transactions & Testing",    ["ACID", "@Transactional", "Propagation", "Isolation Levels", "Unit Testing", "Integration Testing"]),
    11: ("SQL Fundamentals",          ["Query Execution", "Joins", "Aggregations", "Normalization", "EXPLAIN"]),
    12: ("Database Optimization",     ["Indexes", "Composite Indexes", "Covering Indexes", "Query Optimization", "Connection Pooling"]),
    13: ("Redis",                     ["Why Redis", "Data Structures", "Caching", "TTL", "Cache Aside", "Write Through"]),
    14: ("Kafka",                     ["Architecture", "Producers", "Consumers", "Partitions", "Consumer Groups", "Offsets"]),
    15: ("RabbitMQ & Messaging",      ["Queues", "Exchanges", "Routing", "Dead Letter Queues", "Retry Strategies"]),
    16: ("Docker",                    ["Containers", "Images", "Dockerfile", "Layers", "Docker Compose"]),
    17: ("Kubernetes",                ["Pods", "Deployments", "Services", "ConfigMaps", "Secrets", "Scaling"]),
    18: ("AWS & Cloud",               ["EC2", "S3", "IAM", "RDS", "ECS", "Cloud Architecture Basics"]),
    19: ("CI/CD & DevOps",            ["GitHub Actions", "Jenkins", "Pipelines", "Rolling Deployment", "Blue Green", "Canary Deployment"]),
    20: ("Monitoring & Observability", ["Logging", "Metrics", "Tracing", "Prometheus", "Grafana", "OpenTelemetry"]),
    21: ("Distributed Systems Basics", ["CAP Theorem", "Consistency Models", "Replication", "Partitioning"]),
    22: ("Scalability",               ["Sharding", "Load Balancing", "API Gateway", "Reverse Proxy", "CDN"]),
    23: ("Reliability",               ["Circuit Breakers", "Retry", "Timeouts", "Idempotency", "Bulkhead Pattern"]),
    24: ("System Design",             ["URL Shortener", "Rate Limiter", "Notification Service", "File Storage", "Chat System"]),
    25: ("Advanced Backend",          ["Event Driven Architecture", "Saga Pattern", "CQRS", "Event Sourcing", "Microservices Communication"]),
    26: ("Backend Security",          ["Authentication", "Authorization", "JWT", "OAuth2", "RBAC", "Session Management"]),
    27: ("Secure Coding",             ["SQL Injection", "XSS", "CSRF", "Input Validation", "Secure Password Storage"]),
    28: ("JVM Performance",           ["Profiling", "Heap Dump", "Thread Dump", "JFR", "VisualVM", "Performance Tuning"]),
    29: ("Production Engineering",    ["Debugging Production Issues", "Root Cause Analysis", "Performance Bottlenecks", "Incident Response", "Postmortems"]),
    30: ("SDE-2 Interview Masterclass", ["End-to-End Backend Design", "System Design Walkthrough", "Java Interview Revision", "Spring Boot Revision", "SQL Revision", "Redis Revision", "Kafka Revision", "Production Scenarios", "Mock Interview Questions"]),
}

AI_CURRICULUM = {
    1:  ("Introduction to LLMs",           ["Evolution of AI", "Generative AI vs Traditional ML", "How LLMs Work", "Tokens", "Context Window", "LLM Capabilities & Limitations"]),
    2:  ("Transformer Architecture",       ["Why Transformers Replaced RNNs", "Encoder vs Decoder", "Self-Attention", "Multi-Head Attention", "Positional Encoding", "Feed Forward Networks"]),
    3:  ("Tokens & Embeddings",            ["Tokenization", "BPE", "WordPiece", "SentencePiece", "Embeddings", "Vector Similarity", "Cosine Similarity"]),
    4:  ("Prompt Engineering",             ["Prompt Structure", "Zero-shot", "One-shot", "Few-shot", "Chain of Thought", "Prompt Templates", "Common Prompting Mistakes"]),
    5:  ("LLM Inference",                  ["Inference Pipeline", "Temperature", "Top-K", "Top-P", "Max Tokens", "Streaming", "Latency Fundamentals"]),
    6:  ("Vector Databases",               ["Why Vector Databases Exist", "ANN Search", "HNSW", "FAISS", "Pinecone", "Weaviate", "ChromaDB"]),
    7:  ("Embedding Models",               ["OpenAI Embeddings", "BGE", "E5", "VoyageAI", "Choosing the Right Embedding Model", "Embedding Evaluation"]),
    8:  ("Document Chunking",              ["Fixed Chunking", "Recursive Chunking", "Semantic Chunking", "Sliding Window", "Parent-Child Chunking", "Metadata Strategies"]),
    9:  ("Retrieval Augmented Generation (RAG)", ["Why RAG Exists", "Complete RAG Pipeline", "Retrieval Flow", "Context Injection", "Hallucination Reduction", "Production Architecture"]),
    10: ("Semantic Search",                ["Similarity Search", "Hybrid Search", "Metadata Filtering", "Query Expansion", "Search Optimization"]),
    11: ("Advanced RAG",                   ["Multi-step RAG", "Recursive Retrieval", "Context Compression", "Query Routing", "Agentic RAG"]),
    12: ("Hybrid Search & Reranking",      ["BM25", "Dense Retrieval", "Hybrid Retrieval", "Cross Encoder Rerankers", "Reciprocal Rank Fusion"]),
    13: ("Tool Calling",                   ["Why Tool Calling Exists", "Function Calling", "Structured Outputs", "API Integration", "External Tools", "Best Practices"]),
    14: ("MCP (Model Context Protocol)",   ["MCP Fundamentals", "MCP Architecture", "Resources", "Tools", "Prompts", "Building MCP Servers"]),
    15: ("AI Application Architecture",    ["Chatbots", "AI Assistants", "Enterprise AI Systems", "Workflow Integration", "Common Backend Patterns"]),
    16: ("AI Agents",                      ["What is an Agent", "Agent Loop", "Perception", "Reasoning", "Planning", "Action"]),
    17: ("Agent Memory",                   ["Short-Term Memory", "Long-Term Memory", "Vector Memory", "Episodic Memory", "Semantic Memory"]),
    18: ("Planning & Reasoning",           ["ReAct", "Tree of Thoughts", "Planning Strategies", "Reflection", "Iterative Reasoning"]),
    19: ("LangGraph",                      ["Nodes", "Edges", "State", "Conditional Routing", "Human-in-the-Loop", "Error Recovery"]),
    20: ("Workflow Orchestration",         ["Multi-Step Workflows", "Durable Execution", "Retry Logic", "Parallel Execution", "Agent Coordination"]),
    21: ("Multi-Agent Systems",            ["Why Multi-Agent Systems", "Supervisor Pattern", "Planner-Executor Pattern", "Swarm Architecture", "Collaboration Strategies"]),
    22: ("AI Guardrails & Safety",         ["Prompt Injection", "Jailbreaks", "Input Validation", "Output Validation", "Content Moderation", "Secure Agent Design"]),
    23: ("AI Evaluation",                  ["Benchmarking", "Human Evaluation", "LLM-as-a-Judge", "RAG Evaluation", "Response Quality Metrics"]),
    24: ("AI Observability",               ["Prompt Logging", "Tracing", "Token Usage", "Cost Monitoring", "Latency Monitoring", "Error Analysis"]),
    25: ("Production AI Security",         ["Secret Management", "API Security", "Data Privacy", "PII Protection", "Secure Deployment"]),
    26: ("LLMOps",                         ["CI/CD for AI", "Model Versioning", "Prompt Versioning", "Deployment Pipelines", "Experiment Tracking"]),
    27: ("Production Optimization",        ["Latency Optimization", "Throughput Optimization", "Streaming Responses", "Caching", "Batching", "Rate Limits"]),
    28: ("Cost Engineering",               ["Token Optimization", "Model Selection", "Context Optimization", "Embedding Costs", "Infrastructure Costs"]),
    29: ("Deploying AI Systems",           ["AI Backend Architecture", "Scaling AI APIs", "High Availability", "Monitoring", "Failure Recovery", "Production Best Practices"]),
    30: ("AI System Design Masterclass",   ["Design a Production AI Assistant", "RAG + Agents + Tools", "End-to-End Architecture", "Scaling Strategy", "Common Interview Questions", "SDE-2 AI Backend Revision"]),
}


def _format_topics(topics: list[str]) -> str:
    return "\n".join(f"  • {t}" for t in topics)


# ---------------------------------------------------------------------------
# Master prompt (injected with the current day)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Senior Software Engineer and Backend Mentor with 10+ years of experience building production backend systems and mentoring engineers into SDE-2 roles at companies like Salesforce, Microsoft, Amazon, Atlassian, Oracle, Adobe, JPMorgan, and Walmart Global Tech.

You are running a structured 30-Day Backend & Agentic AI Bootcamp for one engineer.

Their goal: crack SDE-2 Backend interviews and develop real production-engineering skills.

YOUR TEACHING PHILOSOPHY:
- Teach first. Explain deeply. Then show the code.
- Every difficult concept must be understood intuitively before being explained technically.
- Never assume the reader already understands something — build the mental model from scratch, then go deep.
- Prioritize clarity over cleverness. Dense is good. Confusing is not.
- Ground every concept in a real production scenario the reader can relate to.

YOUR VOICE:
- You are a mentor, not a lecturer. Write like you are sitting next to the reader and walking them through a concept.
- No buzzwords. No hype. No motivational filler.
- Write as if producing a premium engineering textbook — tight, detailed, practical.

WHAT YOU ARE NOT:
- You are not a Staff Engineer or Principal Engineer explaining architecture to other architects.
- You are not writing for a Google SRE or a Netflix distributed systems team.
- You are not simplifying concepts to the point of being useless.

WHAT YOU ARE:
- A mentor helping a strong junior/mid-level engineer deeply understand backend engineering.
- Someone who explains the internals because real understanding leads to confident interviews.
- Someone who connects every concept to real code, real bugs, and real interviews.

DEPTH RULE: Fewer topics explained deeply is always better than many topics explained shallowly. I would rather read 3 topics with 1,500 words each than 8 topics with 400 words each."""


def build_user_prompt(day: int) -> str:
    # ── pull exact curriculum for this day ──────────────────────────────────
    b_title, b_topics = BACKEND_CURRICULUM.get(day, ("Backend Review", ["Mixed topics"]))
    a_title, a_topics = AI_CURRICULUM.get(day, ("AI Review", ["Mixed topics"]))

    b_topics_str = _format_topics(b_topics)
    a_topics_str = _format_topics(a_topics)

    # For the backend section instruction, select 3 subtopics to go deep on
    b_deep = b_topics[:3] if len(b_topics) >= 3 else b_topics
    b_deep_str = _format_topics(b_deep)

    # For the AI section instruction, select 2 subtopics to go deep on
    a_deep = a_topics[:2] if len(a_topics) >= 2 else a_topics
    a_deep_str = _format_topics(a_deep)

    # Tomorrow preview day
    next_day = day + 1 if day < 30 else 1
    nb_title, nb_topics = BACKEND_CURRICULUM.get(next_day, ("Backend Review", []))
    na_title, na_topics = AI_CURRICULUM.get(next_day, ("AI Review", []))

    return f"""Generate Day {day} of 30 for the 30-Day Backend & Agentic AI Bootcamp newsletter.

## NON-NEGOTIABLE RULES
1. Generate ONLY Day {day} content. Do not explain or summarize previous days.
2. This newsletter is one chapter of a continuous 30-day engineering book. Build on what came before.
3. Never repeat concepts already covered in earlier days. Go forward.
4. Increase depth every single day. Day {day} must be noticeably more advanced than Day {day - 1 if day > 1 else 1}.
5. Do not add introductions, disclaimers, filler phrases, or motivational sentences. Start with content immediately.
6. Every concept must be explained deeply, intuitively, and practically — not academically.
7. Use the full response length. Do not truncate content early.
8. If content must be cut due to length, cut in this order (last to first):
   Tomorrow Preview → Revision → AI Challenge → Backend Challenge → Industry Pulse → AI Section → Backend Section → System Design (never cut System Design).

---

## TARGET AUDIENCE
An engineer with basic Java knowledge preparing for SDE-2 Backend interviews at:
Salesforce, Microsoft, Amazon, Atlassian, Oracle, Adobe, JPMorgan, Walmart Global Tech, Databricks.

---

## SECTION 1 — 📈 Progress Dashboard

Include:
- Day {day} / 30 with a visual HTML/CSS progress bar ({round(day / 30 * 100)}% filled)
- A short 2-line summary of where the 30-day journey stands at Day {day}
- Today's backend theme: {b_title}
- Today's AI theme: {a_title}
- Estimated reading time

---

## SECTION 2 — ☕ Backend Engineering

Today's theme: **{b_title}**

Full topic list for Day {day}:
{b_topics_str}

Go deep on exactly these 3 subtopics (the most important ones for interviews and production):
{b_deep_str}

For EACH of the 3 subtopics, write a deeply detailed explanation in this exact order:

**1. What Is It?**
Define the concept plainly. One paragraph. No jargon without explanation.

**2. Why Does It Exist?**
Explain the real problem it was built to solve. Be specific. Use a concrete scenario.

**3. Intuition**
Build the mental model. Explain it like you are drawing on a whiteboard. Use an analogy if it helps. This section must make the concept click before any code is shown.

**4. Internal Working**
Explain the mechanics. How does it actually work under the hood? Go deep. This is not surface description — explain the internals step by step.

**5. Java Implementation**
Show clean, well-commented Java code. Not toy examples. Code that looks like it belongs in a real service.

**6. Spring Boot Integration**
Show how this concept is used in a real Spring Boot application. Include annotations, configuration, and relevant patterns.

**7. Production Example**
Describe a real scenario where this concept directly impacted a production system. Be specific — what was the service, what was the behaviour, what was the outcome.

**8. Debugging Story**
A short but real story: a bug or incident caused by misunderstanding or misusing this concept. What was the symptom? What was the root cause? How was it fixed?

**9. Common Mistakes**
List 3–5 specific mistakes engineers make with this concept, especially in interviews and production.

**10. Performance Considerations**
What are the performance implications? What should an engineer always think about when using it?

**11. Interview Questions**
Exactly 5 SDE-2 interview questions on this topic. Include the ideal answer approach for each — not the full answer, just what a strong candidate would say.

**12. Key Takeaways**
3–5 bullet points summarising the most important things to remember.

After covering the 3 deep topics, add a brief **"Rest of Day {day} Topics"** section that gives a 2–3 sentence summary of each remaining topic from the full list:
{b_topics_str}
This ensures the reader knows what the remaining topics are about even if they are not covered in full depth today.

---

## SECTION 3 — 🤖 Agentic AI

Today's theme: **{a_title}**

Full topic list for Day {day}:
{a_topics_str}

Go deep on exactly these 2 subtopics:
{a_deep_str}

For EACH of the 2 subtopics, write a deeply detailed explanation in this exact order:

**1. What Is It?**
Define it plainly. One focused paragraph.

**2. Why It Exists**
What engineering problem does this solve? Why did it need to be built?

**3. Internal Working**
Explain the mechanics in detail. How does it actually work?

**4. Architecture**
Describe how this component fits into a larger AI system. Draw the architecture using HTML/CSS if helpful.

**5. Implementation**
Show real implementation code in Python or pseudocode. Make it practical.

**6. Prompt Example**
If applicable, show a concrete prompt and explain why it is structured that way.

**7. Production Example**
A real-world scenario where this concept is used in a production AI system.

**8. Failure Modes**
What goes wrong with this in production? Be specific.

**9. Cost Considerations**
What does this cost to run? What drives the cost? How do you optimise it?

**10. Interview Questions**
Exactly 3 SDE-2 AI interview questions on this topic with ideal answer direction.

**11. Key Takeaways**
3–4 bullets summarising what matters most.

After the 2 deep topics, add a brief **"Rest of Day {day} AI Topics"** section — 2–3 sentences per remaining topic from:
{a_topics_str}

---

## SECTION 4 — 🌍 Industry Pulse

Exactly 3 items. Each item must teach a real engineering lesson — not just report news.

For each item include:
- What happened (1–2 sentences)
- Why it matters to a backend engineer (1–2 sentences)
- The engineering lesson to take away (2–3 sentences, specific and actionable)

Topics can include: real production incidents, engineering blog deep-dives, notable open source releases, backend architecture decisions made at scale companies, database lessons, API design patterns observed in the wild.

---

## SECTION 5 — 🏗 Daily System Design

This is the most important section. Allocate the most space to it.

The design problem must naturally align with today's backend theme: **{b_title}**

Answer as a strong SDE-2 candidate would in a live interview. Explain every decision — not just what you chose, but why.

Include all of the following, in order:

1. **Problem Statement** — What are we building and why?
2. **Functional Requirements** — What must the system do? (5–8 specific requirements)
3. **Non-Functional Requirements** — Latency, availability, consistency, scalability targets
4. **API Design** — REST endpoints with method, path, request body, response body, and status codes
5. **Database Design** — Tables/collections, columns, data types, indexes, and relationships. Explain every index.
6. **High-Level Architecture** — Describe the components and draw the architecture using HTML/CSS boxes and arrows
7. **Component Responsibilities** — For each component (API Gateway, Service, Cache, Queue, Database, Workers): what it does and why it exists
8. **Request Flow** — Step-by-step walkthrough of a key user request through the system. Explain why each hop exists.
9. **Caching Strategy** — What is cached, where, what TTL, and what invalidation strategy
10. **Scaling Strategy** — How does the system scale from 10K to 1M users? What changes and why?
11. **Bottlenecks** — Where will this system break under load? How do you address each one?
12. **Failure Handling** — What happens when the database goes down? When the cache fails? When a service crashes? Recovery strategy for each.
13. **Monitoring** — Key metrics, alerts, and how you would debug a production incident in this system
14. **Security** — Authentication, authorisation, input validation, and at least one security risk specific to this design
15. **Trade-offs** — What did you sacrifice? What would you do differently with more time or resources?
16. **Interview Questions** — 5 follow-up questions an interviewer would ask, with the direction a strong answer would take

---

## SECTION 6 — 💻 Backend Coding Challenge

One hands-on Java implementation problem directly tied to today's backend theme: **{b_title}**

Include:
- Problem statement (clear, specific, production-relevant)
- Constraints
- Expected input/output
- Starter code skeleton in Java
- What concept this tests and why it matters in interviews

Do NOT include the solution.

---

## SECTION 7 — 🤖 AI Implementation Challenge

One practical AI engineering challenge tied to today's AI theme: **{a_title}**

Include:
- What to build
- Tech stack to use
- Key implementation steps
- What to think about (edge cases, failure modes)
- Why this challenge is relevant to production AI systems

Do NOT include the solution.

---

## SECTION 8 — 🔁 Revision Corner

{'Skip this section entirely — this is Day 1.' if day == 1 else f'''Exactly 5 questions drawn from concepts covered in Days 1 through {day - 1}.
Do not ask about today\'s topics.
Questions must require real understanding — not just definitions.
Mix conceptual, debugging, and design questions.'''}

---

## SECTION 9 — 📅 Tomorrow Preview

Day {next_day} covers:
- Backend: **{nb_title}** — {", ".join(nb_topics[:4])}{"..." if len(nb_topics) > 4 else ""}
- AI: **{na_title}** — {", ".join(na_topics[:3])}{"..." if len(na_topics) > 3 else ""}

Write exactly 3 bullet points — one sentence each — telling the reader what specifically they will learn tomorrow and why it matters.

---

## FORMATTING REQUIREMENTS

Output must be a single complete HTML document, beautiful and Gmail-compatible.

- Font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- Max width: 800px, centered, background: #f0f2f5
- Each section in a white card: background:white, border-radius:12px, padding:32px, margin-bottom:24px, box-shadow:0 2px 12px rgba(0,0,0,0.08)
- Section headers: font-size:22px, font-weight:700, border-left:5px solid #2563eb, padding-left:14px, margin-bottom:20px
- Code blocks: <pre><code> with background:#1e1e1e, color:#d4d4d4, font-family:'Courier New',monospace, font-size:13px, padding:20px, border-radius:8px, overflow-x:auto
- Callout boxes (use for Interview Tips, Production Notes, Debugging Stories, Key Takeaways):
  * Interview Tips: background:#eff6ff, border-left:4px solid #2563eb, padding:16px, border-radius:0 8px 8px 0
  * Production Notes: background:#fff7ed, border-left:4px solid #ea580c, padding:16px, border-radius:0 8px 8px 0
  * Debugging Story: background:#fdf4ff, border-left:4px solid #9333ea, padding:16px, border-radius:0 8px 8px 0
  * Key Takeaways: background:#f0fdf4, border-left:4px solid #16a34a, padding:16px, border-radius:0 8px 8px 0
- Architecture diagrams: built with HTML/CSS divs using flexbox, borders, background colours — no external images
- Progress bar: outer div background:#e5e7eb, inner div width:{round(day / 30 * 100)}%, background:linear-gradient(90deg,#2563eb,#7c3aed), height:12px, border-radius:6px
- Topic badges: display:inline-block, background:#eff6ff, color:#1d4ed8, border:1px solid #bfdbfe, border-radius:20px, padding:4px 12px, font-size:13px, margin:3px
- The entire output must start with <!DOCTYPE html>
- Do NOT use external stylesheets, external fonts, or external images
- Inline all critical styles directly on elements

The final result must read like a premium engineering textbook — dense, clear, deeply explained, and immediately useful for both learning and interview preparation."""


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
