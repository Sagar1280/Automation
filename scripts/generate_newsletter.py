"""
generate_newsletter.py
45-day Backend & Agentic AI Bootcamp newsletter.
Uses 3 split DeepSeek API calls to avoid truncation:
  Call 1 — Backend Engineering (3 topics, full depth)
  Call 2 — Agentic AI (2 topics, full depth)
  Call 3 — System Design + Backend Coding Challenge
All 3 results are merged into one HTML file.
"""

import os
import time
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
API_KEY          = os.environ["DEEPSEEK_API_KEY"]
CURRENT_DAY      = int(os.environ.get("CURRENT_DAY", "1"))
OUTPUT_FILE      = "newsletter_output.html"
TOTAL_DAYS       = 45

# ---------------------------------------------------------------------------
# 45-Day Curriculum
# ---------------------------------------------------------------------------

BACKEND = {
    1:  ("JVM Architecture",               ["JVM Architecture & Components", "Class Loading Mechanism", "Bytecode & JIT Compilation"]),
    2:  ("JVM Memory Model",               ["Heap Memory & Object Allocation", "Stack Memory & Stack Frames", "Metaspace, String Pool & OutOfMemoryError"]),
    3:  ("Garbage Collection",             ["Mark & Sweep & Generational GC", "G1 GC Internals & Region Layout", "GC Tuning, ZGC & Choosing a Collector"]),
    4:  ("Java Collections",               ["HashMap: Hashing, Buckets & Resize", "ConcurrentHashMap & Thread Safety", "ArrayList vs LinkedList & Time Complexities"]),
    5:  ("Java Concurrency I",             ["Thread Lifecycle & Synchronization", "ReentrantLock, ReadWriteLock & Conditions", "ExecutorService, ThreadPoolExecutor & Sizing"]),
    6:  ("Java Concurrency II",            ["CompletableFuture & Async Chains", "volatile, happens-before & Memory Visibility", "Deadlocks, Livelocks & Race Conditions"]),
    7:  ("Spring IoC & DI",                ["IoC Container & ApplicationContext", "Dependency Injection: Constructor vs Setter vs Field", "Bean Lifecycle, Scopes & Circular Dependencies"]),
    8:  ("Spring Boot",                    ["Auto Configuration & @Conditional", "Spring Boot Startup Sequence", "Profiles, Properties & Externalized Configuration"]),
    9:  ("REST APIs with Spring",          ["REST Controllers & Request Mapping", "Request Validation with @Valid & Custom Validators", "Global Exception Handling with @ControllerAdvice"]),
    10: ("Spring Data JPA I",              ["ORM Concepts & JPA Entity Lifecycle", "Relationships: OneToMany, ManyToMany, ManyToOne", "Lazy vs Eager Loading & Proxy Behaviour"]),
    11: ("Spring Data JPA II",             ["N+1 Problem: Root Cause & Fixes", "JPQL, Named Queries & Native SQL", "Cascade Types, Orphan Removal & Pessimistic Locking"]),
    12: ("Transactions & Testing",         ["ACID Properties & Isolation Levels", "@Transactional: Propagation, Rollback & Common Pitfalls", "Unit Testing with Mockito & Integration Testing with Spring"]),
    13: ("SQL Fundamentals",               ["Query Execution Internals & Parsing", "JOINs: INNER, LEFT, RIGHT, FULL & Performance Impact", "Aggregations, GROUP BY, HAVING & Subqueries"]),
    14: ("Database Indexing",              ["B-Tree Index Internals & How Lookups Work", "Composite Indexes, Covering Indexes & Index Selectivity", "EXPLAIN Plan & Query Optimization Workflow"]),
    15: ("Advanced SQL",                   ["Window Functions: ROW_NUMBER, RANK, LAG, LEAD", "CTEs & Recursive CTEs", "Normalization vs Denormalization Trade-offs"]),
    16: ("Redis",                          ["Redis Data Structures & Use Cases", "Cache-Aside, Write-Through & Write-Behind", "TTL, Eviction Policies & Redis Persistence"]),
    17: ("Database Scaling",               ["Connection Pooling with HikariCP", "Read Replicas & Read-Write Splitting", "Horizontal Sharding: Range, Hash & Directory-Based"]),
    18: ("Kafka I",                        ["Kafka Architecture: Brokers, Topics, Partitions", "Producers, Consumers & Consumer Groups", "Offsets, Replication Factor & Partition Leadership"]),
    19: ("Kafka II",                       ["Offset Commit Strategies & At-Least-Once Delivery", "Kafka Topic Design, Retention & Compaction", "Kafka vs RabbitMQ: When to Use Which"]),
    20: ("RabbitMQ & Messaging",           ["Exchanges, Queues & Routing Keys", "Dead Letter Queues & Retry Strategies", "Message Acknowledgement, Durability & Persistence"]),
    21: ("Docker",                         ["Containers vs VMs: How Docker Works", "Dockerfile, Image Layers & Build Cache Optimization", "Docker Compose for Multi-Container Apps"]),
    22: ("Kubernetes",                     ["Kubernetes Architecture & Control Plane", "Deployments, ReplicaSets, Services & Ingress", "ConfigMaps, Secrets, Health Probes & HPA"]),
    23: ("AWS Core Services",              ["IAM: Users, Roles, Policies & Least Privilege", "EC2, ECS & Container Deployment on AWS", "RDS, S3 & Core Cloud Architecture Patterns"]),
    24: ("CI/CD",                          ["CI/CD Pipeline Design with GitHub Actions", "Rolling, Blue-Green & Canary Deployment Strategies", "Docker Build, Push & Deploy in Pipelines"]),
    25: ("Observability",                  ["Structured Logging: Format, Levels & Correlation IDs", "Metrics with Prometheus & Grafana Dashboards", "Distributed Tracing with OpenTelemetry"]),
    26: ("Distributed Systems I",          ["CAP Theorem in Real Production Systems", "Consistency Models: Strong, Eventual, Causal", "Database Replication: Sync vs Async Trade-offs"]),
    27: ("Distributed Systems II",         ["Load Balancing Algorithms & API Gateway", "CDN, Reverse Proxy & Edge Caching", "Service Discovery & Consistent Hashing"]),
    28: ("Reliability Patterns",           ["Circuit Breaker with Resilience4j", "Retry, Timeout, Fallback & Bulkhead", "Idempotency: Design & Implementation"]),
    29: ("Event-Driven Architecture",      ["Event-Driven vs Request-Driven Architecture", "CQRS: Separating Read & Write Models", "Saga Pattern: Choreography vs Orchestration"]),
    30: ("Microservices",                  ["Microservices vs Monolith: Real Trade-offs", "Inter-Service Communication: REST, gRPC, Events", "API Gateway & Backend for Frontend Pattern"]),
    31: ("Backend Security I",             ["Session vs Token-Based Authentication", "JWT: Structure, Signing, Validation & Expiry", "OAuth2 Flows & Spring Security Integration"]),
    32: ("Backend Security II",            ["Role-Based Access Control (RBAC)", "Securing REST APIs: Rate Limiting, CORS, Headers", "SQL Injection, XSS & CSRF Prevention"]),
    33: ("Secure Coding",                  ["Input Validation & Output Encoding", "Secure Password Storage: BCrypt & Argon2", "Secrets Management: Vault & AWS Secrets Manager"]),
    34: ("JVM Performance",                ["JVM Profiling with JFR & async-profiler", "Heap Dump Analysis & Memory Leak Detection", "Thread Dump Analysis & Deadlock Detection"]),
    35: ("API & Query Performance",        ["HTTP Caching: ETags, Cache-Control & CDN", "Database Query Optimization: Indexes & Batch Queries", "Pagination: Offset vs Cursor-Based"]),
    36: ("Production Debugging",           ["Root Cause Analysis Framework", "Debugging High Latency in Production", "Reading Logs & Metrics at Scale"]),
    37: ("Incident Response",              ["Incident Detection, Severity Classification & Escalation", "On-Call Runbooks & Troubleshooting Playbooks", "Postmortem Writing & Blameless Culture"]),
    38: ("Advanced Backend Patterns",      ["Rate Limiting: Token Bucket & Leaky Bucket", "Distributed Locking with Redis", "Outbox Pattern for Reliable Event Publishing"]),
    39: ("System Design I",                ["Design a URL Shortener end-to-end", "Design a Notification Service end-to-end", "Design a File Storage Service end-to-end"]),
    40: ("System Design II",               ["Design a Rate Limiter end-to-end", "Design a Chat System end-to-end", "Design a News Feed & Timeline System end-to-end"]),
    41: ("Java & Spring Interview Prep",   ["Top 20 Java Internals Interview Q&A", "Top 20 Spring Boot & JPA Interview Q&A", "Top 10 Concurrency & Transaction Interview Q&A"]),
    42: ("Data & Messaging Interview Prep",["Top 20 SQL, Index & Database Interview Q&A", "Top 15 Redis & Caching Interview Q&A", "Top 15 Kafka & Messaging Interview Q&A"]),
    43: ("Distributed Systems Interview",  ["Top 20 Distributed Systems Interview Q&A", "Top 15 Microservices & API Design Interview Q&A", "Top 10 Security Interview Q&A"]),
    44: ("System Design Interview Mastery",["How to Structure Any System Design Answer", "10 Most Common System Design Mistakes", "15 Must-Know System Design Patterns with Examples"]),
    45: ("Final SDE-2 Mock",               ["Full Mock: Design a Real-Time Analytics System", "Full Mock: Debug a Production Incident Scenario", "Rapid-Fire Revision: All 45 Days Key Concepts"]),
}

AI = {
    1:  ("Introduction to LLMs",                ["How LLMs Work: Training & Inference", "Tokens, Context Window & Limitations"]),
    2:  ("Transformer Architecture",            ["Self-Attention & Multi-Head Attention", "Encoder vs Decoder & Positional Encoding"]),
    3:  ("Tokens & Embeddings",                 ["Tokenization: BPE & WordPiece", "Embeddings, Vector Space & Cosine Similarity"]),
    4:  ("Prompt Engineering",                  ["Zero-shot, Few-shot & Chain of Thought", "Prompt Templates, System Prompts & Structured Outputs"]),
    5:  ("LLM Inference",                       ["Inference Pipeline: Temperature & Sampling", "Latency, Throughput, Streaming & Caching"]),
    6:  ("Vector Databases",                    ["HNSW Index & ANN Search Internals", "Pinecone, Weaviate & ChromaDB Comparison"]),
    7:  ("Embedding Models",                    ["Choosing the Right Embedding Model", "Evaluating & Benchmarking Embedding Quality"]),
    8:  ("Document Chunking",                   ["Recursive & Semantic Chunking Strategies", "Parent-Child Chunking & Metadata Enrichment"]),
    9:  ("RAG Architecture",                    ["Complete RAG Pipeline End-to-End", "Hallucination Reduction & Context Injection"]),
    10: ("Semantic & Hybrid Search",            ["Hybrid Search: BM25 + Dense Retrieval", "Metadata Filtering & Query Expansion"]),
    11: ("Advanced RAG",                        ["Context Compression & Query Routing", "Agentic RAG & Multi-Step Retrieval"]),
    12: ("Reranking",                           ["Cross-Encoder Rerankers & When to Use Them", "Reciprocal Rank Fusion"]),
    13: ("Tool & Function Calling",             ["Function Calling & Structured JSON Outputs", "API Integration, Error Handling & Retries"]),
    14: ("MCP Protocol",                        ["MCP Architecture & Core Concepts", "Building MCP Servers, Tools & Resources"]),
    15: ("AI Application Architecture",         ["Enterprise AI System Patterns", "AI Backend Integration with REST APIs"]),
    16: ("AI Agents",                           ["Agent Loop: Perception, Reasoning, Action", "Agent Types & Design Patterns"]),
    17: ("Agent Memory",                        ["Short-Term vs Long-Term Memory", "Vector Memory & Episodic Memory"]),
    18: ("Planning & Reasoning",                ["ReAct Framework & Chain of Thought", "Tree of Thoughts & Self-Reflection"]),
    19: ("LangGraph",                           ["State, Nodes & Conditional Routing", "Human-in-the-Loop & Error Recovery"]),
    20: ("Workflow Orchestration",              ["Multi-Step Workflows & Parallel Execution", "Durable Execution & Retry Logic"]),
    21: ("Multi-Agent Systems",                 ["Supervisor & Planner-Executor Patterns", "Swarm Architecture & Agent Communication"]),
    22: ("AI Safety & Guardrails",              ["Prompt Injection & Jailbreak Prevention", "Input/Output Validation & Content Moderation"]),
    23: ("AI Evaluation",                       ["LLM-as-a-Judge & RAG Evaluation Metrics", "Response Quality, Benchmarking & A/B Testing"]),
    24: ("AI Observability",                    ["Tracing, Prompt Logging & Token Monitoring", "Latency & Cost Monitoring"]),
    25: ("Production AI Security",              ["API Security, PII Protection & Data Privacy", "Secure Deployment & Secrets Management"]),
    26: ("LLMOps",                              ["CI/CD for AI & Prompt Versioning", "Deployment Pipelines & Experiment Tracking"]),
    27: ("Production Optimization",             ["Latency Optimization: Caching & Batching", "Streaming Responses & Throughput Tuning"]),
    28: ("Cost Engineering",                    ["Token Optimization & Model Selection", "Context Window Optimization & Cost Monitoring"]),
    29: ("Deploying AI Systems",                ["Scaling AI APIs & High Availability", "Failure Recovery & Production Best Practices"]),
    30: ("AI System Design",                    ["Design a Production RAG System end-to-end", "Design an AI Agent Backend end-to-end"]),
    31: ("Senior AI Interview: LLM Foundations",["LLM architecture, attention, tokenization: 8 senior interview Q&A with model answers", "Prompt engineering, inference tuning: 8 senior interview Q&A with model answers"]),
    32: ("Senior AI Interview: RAG Systems",    ["RAG pipeline, chunking, retrieval: 8 senior interview Q&A with model answers", "Hybrid search, reranking, hallucination: 8 senior interview Q&A with model answers"]),
    33: ("Senior AI Interview: Agents & Tools", ["Agent architecture, tool calling, MCP: 8 senior interview Q&A with model answers", "Agent memory, planning, LangGraph: 8 senior interview Q&A with model answers"]),
    34: ("Senior AI Interview: Production AI",  ["LLMOps, deployment, scaling AI APIs: 8 senior interview Q&A with model answers", "Cost engineering, latency, observability: 8 senior interview Q&A with model answers"]),
    35: ("Senior AI Interview: Safety & Eval",  ["Guardrails, prompt injection, jailbreaks: 8 senior interview Q&A with model answers", "AI evaluation, benchmarking, LLM-as-a-Judge: 8 senior interview Q&A with model answers"]),
    36: ("AI System Design: RAG",               ["Design a production RAG system: full staff-level walkthrough", "Design an AI-powered search engine: full walkthrough"]),
    37: ("AI System Design: Agents",            ["Design a multi-agent customer support system: full walkthrough", "Design an LLMOps pipeline: full walkthrough"]),
    38: ("AI System Design: Enterprise",        ["Design a document intelligence platform: full walkthrough", "Design a real-time AI assistant API: full walkthrough"]),
    39: ("AI Hard Questions I",                 ["10 hardest LLM & RAG interview questions with model answers", "10 hardest AI agent interview questions with model answers"]),
    40: ("AI Hard Questions II",                ["10 hardest production AI interview questions with model answers", "10 hardest AI system design questions with model answers"]),
    41: ("AI Rapid Fire I",                     ["30 rapid-fire AI interview Q&A: LLM & RAG focus", "30 rapid-fire AI interview Q&A: Agents & Tools focus"]),
    42: ("AI Rapid Fire II",                    ["30 rapid-fire AI system design Q&A", "Common AI interview mistakes & how to avoid them"]),
    43: ("AI Scenario Questions I",             ["Scenario: RAG system with poor retrieval quality: diagnose & fix", "Scenario: Agent stuck in a loop: diagnose & resolve"]),
    44: ("AI Scenario Questions II",            ["Scenario: AI system costs 10x budget: find & fix", "Scenario: AI API P99 latency is 8s: trace & fix"]),
    45: ("Final AI Revision",                   ["Full revision: Every AI concept Days 1-30 as interview Q&A", "AI system design: Design the most complex AI system you can"]),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(topics):
    return "\n".join("  - " + t for t in topics)

# ---------------------------------------------------------------------------
# System prompt (shared across all 3 calls)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a Senior Software Engineer and Backend Mentor with 10+ years of experience
mentoring engineers into SDE-2 roles at Salesforce, Microsoft, Amazon, Atlassian, Oracle, Adobe, JPMorgan, and Walmart.

You are generating one section of a 45-Day Backend & Agentic AI Bootcamp newsletter.

RULES:
- Every topic listed gets EQUAL depth. No topic is more important than another.
- Never skip, summarise, or merge topics. Each gets its own complete treatment.
- Dense, practical, interview-focused. No fluff. No motivational filler.
- Write like a premium engineering textbook — clear, precise, immediately useful.
- Output ONLY the HTML body content for your section (no DOCTYPE, no <html>, no <head>, no <body> tags).
- Use inline CSS only. Cards: background:white, border-radius:12px, padding:32px, margin-bottom:24px, box-shadow:0 2px 12px rgba(0,0,0,0.08).
- Code blocks: background:#1e1e1e, color:#d4d4d4, font-family:Courier New monospace, font-size:13px, padding:20px, border-radius:8px, overflow-x:auto.
- Callout boxes — Interview: background:#eff6ff, border-left:4px solid #2563eb, padding:16px, border-radius:0 8px 8px 0.
- Callout boxes — Production: background:#fff7ed, border-left:4px solid #ea580c, padding:16px, border-radius:0 8px 8px 0.
- Callout boxes — Takeaway: background:#f0fdf4, border-left:4px solid #16a34a, padding:16px, border-radius:0 8px 8px 0.
- Section headers: font-size:22px, font-weight:700, border-left:5px solid #2563eb, padding-left:14px, margin-bottom:20px, font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif."""

# ---------------------------------------------------------------------------
# Prompt builders — one per API call
# ---------------------------------------------------------------------------

def prompt_backend(day, b_title, b_topics):
    b_str = _fmt(b_topics)
    prev = day - 1 if day > 1 else 1
    return f"""Generate the BACKEND ENGINEERING section for Day {day} of 45 of a Backend & Agentic AI Bootcamp.

Backend theme: {b_title}

Topics:
{b_str}

For EVERY topic above, write a complete explanation with these exact subsections:

1. What is it?
   Plain definition. No jargon without explanation.

2. Why do we need it?
   The real problem it solves. What breaks or becomes harder without it.

3. How does it work?
   Internal mechanics step by step. Deep enough for SDE-2 interviews.
   Use analogies where helpful. Include ASCII diagrams for architecture if useful.

4. Where is it used?
   A real Java or Spring Boot code example — clean, well-commented, production-quality.
   A real production scenario where this concept directly matters.

5. Interview focus
   - 5 SDE-2 interview questions on this topic with the direction a strong answer would take
   - 3 common mistakes engineers make with this concept

Wrap the entire section in a white card div with inline styles.
Use a bold section header: "Backend Engineering — Day {day}: {b_title}".
Depth should be noticeably harder than Day {prev}."""


def prompt_ai(day, a_title, a_topics):
    a_str = _fmt(a_topics)
    prev = day - 1 if day > 1 else 1
    return f"""Generate the AGENTIC AI section for Day {day} of 45 of a Backend & Agentic AI Bootcamp.

AI theme: {a_title}

Topics:
{a_str}

For EVERY topic above, write a complete explanation with these exact subsections:

1. What is it?
   Plain definition. No jargon without explanation.

2. Why do we need it?
   The real problem it solves. What breaks without it.

3. How does it work?
   Internal mechanics step by step.
   Include an architecture diagram using HTML/CSS divs where useful.

4. Where is it used?
   A real Python code example or concrete prompt example.
   A real production AI system scenario where this concept directly matters.

5. Interview focus
   - 5 SDE-2 AI interview questions on this topic with the direction a strong answer would take
   - 3 common mistakes engineers make with this concept

Wrap the entire section in a white card div with inline styles.
Use a bold section header: "Agentic AI — Day {day}: {a_title}".
Depth should be noticeably harder than Day {prev}."""


def prompt_system_design(day, b_title):
    prev = day - 1 if day > 1 else 1
    return f"""Generate the SYSTEM DESIGN section and BACKEND CODING CHALLENGE for Day {day} of 45 of a Backend & Agentic AI Bootcamp.

Design a system that naturally relates to today's backend theme: {b_title}

SYSTEM DESIGN — cover all of the following in order, in full detail:

1. Problem Statement — what are we building and why?
2. Functional Requirements — 5 to 8 specific requirements
3. Non-Functional Requirements — latency, availability, consistency, scalability targets
4. API Design — REST endpoints with method, path, request body, response body, status codes
5. Database Design — tables, columns, data types, indexes. Explain every index and why it exists.
6. High-Level Architecture — draw using HTML/CSS divs, flexbox, borders and colours. No images.
7. Component Responsibilities — for each component explain what it does and why it exists
8. Request Flow — step by step walkthrough of a key user request. Explain every hop.
9. Caching Strategy — what is cached, where, what TTL, what invalidation strategy
10. Scaling Strategy — how does the system scale from 10K to 1M users? What changes and why?
11. Bottlenecks — where will this break under load? How do you fix each one?
12. Failure Handling — DB down, cache down, service crash. Recovery strategy for each.
13. Monitoring & Alerting — key metrics, alerts, how to debug a production incident
14. Security — auth, input validation, at least one design-specific risk
15. Trade-offs — what was sacrificed? What would you do differently with more time?
16. 5 follow-up interview questions with the direction a strong answer would take

BACKEND CODING CHALLENGE:
One Java implementation problem tied to {b_title}.
- Problem statement (clear, production-relevant)
- Constraints
- Expected input and output examples
- Java starter skeleton with meaningful comments
- What concept this tests and why it matters in SDE-2 interviews
Do NOT include the solution.

Wrap each part (System Design and Coding Challenge) in its own white card div with inline styles.
Use bold section headers: "System Design — Day {day}" and "Backend Coding Challenge — Day {day}".
Depth should be noticeably harder than Day {prev}."""

# ---------------------------------------------------------------------------
# API call helper
# ---------------------------------------------------------------------------

def call_deepseek(prompt_text, label, max_retries=3):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt_text},
        ],
        "max_tokens": 8192,
        "temperature": 0.7,
        "stream": False,
    }

    for attempt in range(1, max_retries + 1):
        print(f"[{label}] Attempt {attempt}/{max_retries}...")
        try:
            r = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=300)
            r.raise_for_status()
            data = r.json()
            usage = data.get("usage", {})
            print(f"[{label}] Done — tokens: {usage}")
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            print(f"[{label}] Timeout on attempt {attempt}.")
        except requests.exceptions.HTTPError as e:
            print(f"[{label}] HTTP {e.response.status_code}: {e.response.text}")
            if e.response.status_code in (400, 401, 403):
                raise
        except Exception as e:
            print(f"[{label}] Error: {e}")

        if attempt < max_retries:
            wait = 15 * attempt
            print(f"[{label}] Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(f"[{label}] Failed after {max_retries} attempts.")


def strip_fences(text):
    text = text.strip()
    if text.startswith("```html"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def build_html(day, b_title, a_title, backend_html, ai_html, sysdesign_html):
    pct = round(day / TOTAL_DAYS * 100)
    progress_bar = (
        f'<div style="background:#e5e7eb;border-radius:6px;height:12px;margin:12px 0 4px 0;">'
        f'<div style="width:{pct}%;background:linear-gradient(90deg,#2563eb,#7c3aed);height:12px;border-radius:6px;"></div>'
        f'</div>'
    )
    dashboard = f"""
    <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);color:white;border-radius:12px;padding:32px;margin-bottom:24px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <div style="font-size:13px;opacity:0.8;margin-bottom:4px;">45-Day Backend & Agentic AI Bootcamp</div>
      <div style="font-size:28px;font-weight:800;margin-bottom:8px;">Day {day} / {TOTAL_DAYS}</div>
      {progress_bar}
      <div style="font-size:13px;opacity:0.75;margin-top:8px;">{pct}% complete</div>
      <div style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.15);border-radius:20px;padding:4px 14px;font-size:13px;">Backend: {b_title}</span>
        <span style="background:rgba(255,255,255,0.15);border-radius:20px;padding:4px 14px;font-size:13px;">AI: {a_title}</span>
      </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>45-Day Bootcamp — Day {day}: {b_title}</title>
</head>
<body style="margin:0;padding:20px;background:#f0f2f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:800px;margin:0 auto;">

{dashboard}

{backend_html}

{ai_html}

{sysdesign_html}

</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    day = CURRENT_DAY
    b_title, b_topics = BACKEND.get(day, ("Backend Review", ["Mixed review"]))
    a_title, a_topics = AI.get(day, ("AI Review", ["Mixed review"]))

    print(f"[generate] Day {day} — Backend: {b_title} | AI: {a_title}")
    print("[generate] Making 3 API calls...")

    backend_raw   = call_deepseek(prompt_backend(day, b_title, b_topics),       "backend")
    ai_raw        = call_deepseek(prompt_ai(day, a_title, a_topics),             "ai")
    sysdesign_raw = call_deepseek(prompt_system_design(day, b_title),            "sysdesign")

    html = build_html(
        day, b_title, a_title,
        strip_fences(backend_raw),
        strip_fences(ai_raw),
        strip_fences(sysdesign_raw),
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) / 1024
    print(f"[generate] Saved {OUTPUT_FILE} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
