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
SECTION_MARKERS  = {
    "backend": "<!-- SECTION:BACKEND_COMPLETE -->",
    "ai": "<!-- SECTION:AI_COMPLETE -->",
    "sysdesign": "<!-- SECTION:SYSDESIGN_COMPLETE -->",
}

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

SYSTEM_DESIGN = {
    1:  ("Scale from 0 to 1M Users", ["Single Server Setup & Vertical Scaling", "Database Replication & Read-Replicas", "Load Balancing & Horizontal Scaling"]),
    2:  ("Back-of-the-Envelope Estimation", ["Latency, Throughput & QPS Calculations", "Storage & Bandwidth Estimation", "Memory & Cache Sizing Estimation"]),
    3:  ("Client-Server Communication Protocols", ["REST vs GraphQL vs gRPC", "WebSockets vs Server-Sent Events (SSE)", "Long Polling & Short Polling"]),
    4:  ("SQL vs NoSQL Databases", ["Relational DBs (PostgreSQL/MySQL)", "Key-Value Stores (Redis) & Document DBs (MongoDB)", "Wide-Column (Cassandra) & Graph Databases (Neo4j)"]),
    5:  ("System-Wide Caching", ["Cache-Aside, Write-Through & Write-Behind Patterns", "Cache Eviction Policies (LRU, LFU, FIFO)", "Cache Stampede, Cache Penetration, Breakdown & Avalanche"]),
    6:  ("Design a Distributed Key-Value Store", ["Data Partitioning & Replication", "Consistency Models & Tunable Consistency", "Handling Failures & Gossip Protocol"]),
    7:  ("Design a Distributed Unique ID Generator", ["Auto-Increment DB IDs & UUIDs", "Twitter Snowflake ID Generator", "Ticket Server (Flicker) Strategy"]),
    8:  ("Design a URL Shortener (TinyURL)", ["Base 62 Encoding & MD5 Hashing", "API Design & Redirect Operations", "Scalability & Caching High-Traffic Aliases"]),
    9:  ("Design a Pastebin-like Text Sharing Service", ["Data Model & Object Storage Partitioning", "URL Generation & Expiry Cleanup Job", "Bandwidth & Storage Capacity Planning"]),
    10: ("Design an API Rate Limiter", ["Algorithms: Token Bucket & Leaky Bucket", "Algorithms: Fixed Window & Sliding Window Log/Counter", "Distributed Rate Limiting with Redis & Token Sync"]),
    11: ("Consistent Hashing Framework", ["Rehashing Problem & Hash Ring", "Virtual Nodes for Load Distribution", "Use Cases in DynamoDB, Cassandra & Memcached"]),
    12: ("Design a Notification System", ["Multi-Channel Delivery (SMS, Email, Push)", "Priority Queues & Rate Limiting Consumers", "Delivery Guarantee (At-least-once) & Deduplication"]),
    13: ("Design a Distributed File System (S3-like)", ["Metadata Storage vs Block Storage", "Object Upload Flow & Multipart Upload", "Data Replication & Strong vs Eventual Consistency"]),
    14: ("Design a Scalable Web Crawler", ["URL Frontier & Politeness Policies", "HTML Parser & Content Deduplication (SimHash)", "Distributed Crawling & Failure Recovery"]),
    15: ("Design a Distributed Message Queue", ["Commit Log Storage Engine", "Producer & Consumer Pull/Push Models", "Partitioning & High Availability (ISR, Leaders)"]),
    16: ("Design a Proximity Search Service (Yelp)", ["Geohashing vs Quadtrees", "SQL Spatial Indexes vs In-Memory Search", "Read-Heavy Query Optimization & Cache Layer"]),
    17: ("Design Search Autocomplete (Typeahead)", ["Trie Data Structure & Trie Serialization", "Prefix Hash Table & Query Frequency Aggregator", "Caching at Browser/CDN and Real-Time Update Pipeline"]),
    18: ("Design a Real-Time Chat System", ["Connection Management (WebSockets/TCP)", "Presence Server & Online/Offline Status", "Message Storage Strategy: NoSQL (Cassandra/HBase) vs Relational"]),
    19: ("Design a Video Streaming Platform", ["Video Transcoding & Encoding Pipeline", "Content Delivery Network (CDN) & Edge Caching", "Adaptive Bitrate Streaming (HLS/DASH) & Video Metadata DB"]),
    20: ("Design a News Feed / Timeline System", ["Fanout-on-Read vs Fanout-on-Write", "Feed Generation & Storage Strategy", "Handling Celebrities & Hybrid Fanout Approach"]),
    21: ("Design a Collaborative Real-Time Editor", ["Conflict Resolution: Operational Transformation (OT)", "Conflict Resolution: Conflict-free Replicated Data Types (CRDT)", "WebSocket Connection Management & Operation Logging"]),
    22: ("Design a Search Engine (ElasticSearch-like)", ["Inverted Index Construction & Document Indexing", "Distributed Query Processing & Document Scoring", "Segment Merging & Real-Time Write Path"]),
    23: ("Design a Ticket Booking System (Ticketmaster)", ["Concurrency & Race Conditions in Seat Selection", "Distributed Transactions vs Database Locks (Pessimistic/Optimistic)", "Temporary Seat Reservations & Expiry Queue"]),
    24: ("Design a High-Concurrency Flash Sale System", ["Hot Key Caching & Redis Lua Scripts", "Database Write Buffering & Asynchronous Processing", "Over-selling Prevention & Rate Limiting"]),
    25: ("Design a Distributed Job Scheduler", ["Task Queue & Worker Pool Architecture", "Cron Expression Parsing & Dynamic Scheduling", "Handling Worker Failures & At-Least-Once Execution"]),
    26: ("Design a Ride-Hailing Service", ["Geospatial Indexing & Real-Time Location Tracking", "Driver-Passenger Matching Algorithm", "Dynamic Pricing (Surge Pricing) Architecture"]),
    27: ("Design an Ad Click Aggregation System", ["Real-Time Stream Processing (Flink/Spark Streaming)", "MapReduce & Batch Aggregation for Auditing", "Handling Late/Duplicate Data & Deduplication"]),
    28: ("Design a Digital Wallet System", ["Double-Entry Ledger Design & Balance Tracking", "Distributed Transactions & 2-Phase Commit (2PC)", "Idempotency Keys & Payment Gateway Integration"]),
    29: ("Design a Logging & Metrics Collector", ["Push-Based vs Pull-Based Metrics Gathering", "Time-Series Database (TSDB) Storage & Compression", "Log Ingestion (Logstash/Fluentd) & Elasticsearch Indexing"]),
    30: ("Design a Distributed Tracing System", ["Trace ID & Span ID Propagation via HTTP Headers", "Trace Context Collector & In-Memory Buffering", "Sampling Strategies to Control Storage Cost"]),
    31: ("Design an E-Commerce System", ["Microservices Decomposition & Domain-Driven Design (DDD)", "Shopping Cart Service (Session Cache vs DB)", "Order Management & Saga Pattern Orchestration"]),
    32: ("Distributed Transactions & Consensus", ["Two-Phase Commit (2PC) & Three-Phase Commit (3PC)", "Saga Pattern: Choreography vs Orchestration", "Raft & Paxos Consensus Algorithms (Conceptual Overview)"]),
    33: ("Design a Live Streaming Platform", ["RTMP/WebRTC Ingestion & Transcoding", "HLS Delivery at Scale & Chat Integration", "Low Latency Buffering & Edge Stream Replicators"]),
    34: ("Design a Distributed Database", ["Log-Structured Merge-Tree (LSM-Tree) vs B-Tree", "Write-Ahead Log (WAL) & MemTable", "SSTables & Compaction Strategies"]),
    35: ("Design a Distributed Config Service (ZooKeeper)", ["Consensus-Based Configuration Storage", "Watcher Mechanism & Event Notification", "Split-Brain Mitigation & Leader Election"]),
    36: ("Design a Multi-Region Active-Active System", ["Multi-Region Data Replication & Conflict Resolution", "Anycast Routing & Latency Optimization", "Failover & Disaster Recovery Procedures"]),
    37: ("Design an Enterprise API Gateway", ["Routing, Authentication & Rate Limiting", "Service Discovery & Load Balancing Integration", "Service Mesh Architecture: Envoy & Istio Sidecars"]),
    38: ("Design a Multiplayer Game Server", ["Real-Time State Synchronization & UDP Protocol", "Matchmaking Service & Queue Management", "Sharding Game Rooms & Latency Mitigation"]),
    39: ("Design an Email System", ["Mail User Agent, Transfer Agent & Delivery Agent", "Storage Strategy for Millions of Emails (Metadata vs Body)", "Search Indexing & Real-Time Sync via IMAP/Websockets"]),
    40: ("Design a Cloud Storage Service", ["File Chunking & Delta Sync (Block-level Updates)", "Metadata Sync Protocol & Client Architecture", "Conflict Resolution when Editing Files"]),
    41: ("System Design Interview Blueprint", ["Requirement Clarification & API Definition", "High-Level Design & Component Selection", "Deep Dive, Scaling, Bottlenecks & Trade-offs"]),
    42: ("API Schema Design & Evolution", ["Forward & Backward Compatibility in APIs", "Protobuf, Thrift & Avro Schema Formats", "Schema Registry & Version Control"]),
    43: ("Design a Distributed Lock Manager", ["Locking with Redis (Redlock Algorithm)", "Consensus-Based Locking (ZooKeeper/etcd)", "Fencing Tokens for Avoiding Split-Brain/Stale Locks"]),
    44: ("Design an Alerting System", ["Rule Engine for Event Evaluation", "Notification Aggregation, De-duplication & Routing", "Sliding Window Alert Conditions & Query Engine Integration"]),
    45: ("Design a Global Ride-Hailing Platform", ["Unified Capstone: Scaling Geospatial Indices", "Real-Time Matching, Dynamic Pricing & Billing Integration", "Active-Active Multi-Region Data Replication & Disaster Recovery"]),
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

SYSTEM_PROMPT += """

PDF AND READING STYLE:
- Use a professional black-and-white base: near-black body text, white cards, subtle grey borders.
- Use color only for hierarchy: blue for Backend, green for Agentic AI, amber for System Design, red for warnings.
- Bold important terms with <strong>...</strong>, especially definitions, trade-offs, interview keywords, and production risks.
- Keep paragraphs short for mobile reading. Prefer compact bullets where it improves scanning.
"""


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


def prompt_system_design(day, sd_title, sd_topics):
    sd_str = _fmt(sd_topics)
    prev = day - 1 if day > 1 else 1
    return f"""Generate the SYSTEM DESIGN section and BACKEND CODING CHALLENGE for Day {day} of 45 of a Backend & Agentic AI Bootcamp.

System Design Focus: {sd_title}

Topics/Subtopics to cover:
{sd_str}

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


Wrap the entire System Design section in its own white card div with inline styles.
Use a bold section header: "System Design — Day {day}: {sd_title}".
Depth should be SLightly harder (in the sense from junior dev style to senior dev style) than Day {prev}."""

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


def require_section(label, html):
    html = strip_fences(html)
    if not html:
        raise RuntimeError(f"[{label}] DeepSeek returned an empty response.")
    print(f"[{label}] Section ready ({len(html.encode('utf-8')) / 1024:.1f} KB)")
    return f"{SECTION_MARKERS[label]}\n{html}"


def validate_final_html(html):
    missing = [label for label, marker in SECTION_MARKERS.items() if marker not in html]
    if missing:
        raise RuntimeError(f"[generate] Missing generated section(s): {', '.join(missing)}")


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def build_html(day, b_title, a_title, sd_title, backend_html, ai_html, sysdesign_html):
    pct = round(day / TOTAL_DAYS * 100)
    progress_bar = (
        f'<div style="background:#e5e7eb;border-radius:6px;height:12px;margin:12px 0 4px 0;">'
        f'<div style="width:{pct}%;background:#2563eb;height:12px;border-radius:6px;"></div>'
        f'</div>'
    )
    dashboard = f"""
    <div style="background:#111827;color:white;border-radius:10px;padding:30px;margin-bottom:24px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <div style="font-size:13px;opacity:0.82;margin-bottom:4px;">45-Day Backend & Agentic AI Bootcamp</div>
      <div style="font-size:28px;font-weight:800;margin-bottom:8px;letter-spacing:0;">Day {day} / {TOTAL_DAYS}</div>
      {progress_bar}
      <div style="font-size:13px;opacity:0.75;margin-top:8px;">{pct}% complete</div>
      <div style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap;">
        <span style="background:#eff6ff;color:#1e3a8a;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:700;">Backend: {b_title}</span>
        <span style="background:#f0fdf4;color:#166534;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:700;">AI: {a_title}</span>
        <span style="background:#fff7ed;color:#c2410c;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:700;">System Design: {sd_title}</span>
      </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>45-Day Bootcamp — Day {day}: {b_title}</title>
<style>
  body {{
    color: #111827;
    background: #f3f4f6;
    line-height: 1.62;
  }}
  strong {{
    color: #030712;
    font-weight: 800;
  }}
  h1, h2, h3 {{
    color: #111827;
    letter-spacing: 0;
  }}
  h2 {{
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
  }}
  a {{
    color: #1d4ed8;
  }}
  @media print {{
    body {{
      background: #ffffff !important;
      padding: 0 !important;
      font-size: 11.5pt;
    }}
    div {{
      break-inside: avoid-page;
    }}
    pre, code {{
      white-space: pre-wrap !important;
      word-break: break-word !important;
    }}
  }}
  @media screen and (max-width: 640px) {{
    body {{
      padding: 10px !important;
      font-size: 15px;
    }}
    div {{
      max-width: 100% !important;
    }}
  }}
</style>
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
    sd_title, sd_topics = SYSTEM_DESIGN.get(day, ("System Design Review", ["Mixed review"]))

    print(f"[generate] Day {day} — Backend: {b_title} | AI: {a_title} | System Design: {sd_title}")
    print("[generate] Making 3 API calls...")

    sections = {
        "backend": require_section(
            "backend",
            call_deepseek(prompt_backend(day, b_title, b_topics), "backend"),
        ),
        "ai": require_section(
            "ai",
            call_deepseek(prompt_ai(day, a_title, a_topics), "ai"),
        ),
        "sysdesign": require_section(
            "sysdesign",
            call_deepseek(prompt_system_design(day, sd_title, sd_topics), "sysdesign"),
        ),
    }
    print("[generate] All 3 API calls completed. Building final newsletter...")

    html = build_html(
        day, b_title, a_title, sd_title,
        sections["backend"],
        sections["ai"],
        sections["sysdesign"],
    )
    validate_final_html(html)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) / 1024
    print(f"[generate] Saved {OUTPUT_FILE} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
