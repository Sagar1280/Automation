"""
generate_leetcode.py
Calls DeepSeek API to generate a daily LeetCode practice email
with 5 curated questions (2 easy, 2 medium, 1 hard) based on a
structured 90-day plan from beginner to advanced.
All questions are free-tier on LeetCode with direct links.
"""

import os
import sys
import time
import requests

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.environ["DEEPSEEK_API_KEY"]
CURRENT_DAY = int(os.environ.get("CURRENT_DAY", "1"))
OUTPUT_FILE = "leetcode_output.html"

# ---------------------------------------------------------------------------
# 90-day topic plan
# ---------------------------------------------------------------------------
PLAN = {
    # Week 1 - Arrays & Strings Basics
    1:  {"topic": "Arrays — Basics & Traversal", "phase": "Beginner"},
    2:  {"topic": "Arrays — Two Pointers", "phase": "Beginner"},
    3:  {"topic": "Arrays — Sliding Window", "phase": "Beginner"},
    4:  {"topic": "Strings — Basics & Manipulation", "phase": "Beginner"},
    5:  {"topic": "Strings — Palindromes & Anagrams", "phase": "Beginner"},
    6:  {"topic": "Strings — Substrings & Pattern Matching", "phase": "Beginner"},
    7:  {"topic": "Arrays & Strings — Mixed Review", "phase": "Beginner"},
    # Week 2 - Hashing & Prefix Sums
    8:  {"topic": "HashMap & HashSet Fundamentals", "phase": "Beginner"},
    9:  {"topic": "Frequency Counting with HashMap", "phase": "Beginner"},
    10: {"topic": "Prefix Sums & Subarray Problems", "phase": "Beginner"},
    11: {"topic": "Two Sum Variants & Hashing", "phase": "Beginner"},
    12: {"topic": "Sorting — Basic Algorithms", "phase": "Beginner"},
    13: {"topic": "Sorting — Custom Comparators", "phase": "Beginner"},
    14: {"topic": "Hashing + Sorting — Mixed Review", "phase": "Beginner"},
    # Week 3 - Linked Lists
    15: {"topic": "Linked Lists — Basics & Traversal", "phase": "Beginner"},
    16: {"topic": "Linked Lists — Reversal Patterns", "phase": "Beginner"},
    17: {"topic": "Linked Lists — Fast & Slow Pointers", "phase": "Beginner"},
    18: {"topic": "Linked Lists — Merge & Sort", "phase": "Intermediate"},
    19: {"topic": "Stacks — Basics & Applications", "phase": "Intermediate"},
    20: {"topic": "Queues & Deques", "phase": "Intermediate"},
    21: {"topic": "Stack & Queue — Mixed Review", "phase": "Intermediate"},
    # Week 4 - Recursion & Binary Search
    22: {"topic": "Recursion — Fundamentals", "phase": "Intermediate"},
    23: {"topic": "Recursion — Backtracking Intro", "phase": "Intermediate"},
    24: {"topic": "Binary Search — Basics", "phase": "Intermediate"},
    25: {"topic": "Binary Search — On Answer", "phase": "Intermediate"},
    26: {"topic": "Binary Search — Rotated & Variants", "phase": "Intermediate"},
    27: {"topic": "Recursion + Binary Search — Mixed Review", "phase": "Intermediate"},
    28: {"topic": "Week 4 Consolidation — Arrays, Hashing, LinkedList, BS", "phase": "Intermediate"},
    # Week 5 - Trees
    29: {"topic": "Binary Trees — Basics & DFS", "phase": "Intermediate"},
    30: {"topic": "Binary Trees — BFS & Level Order", "phase": "Intermediate"},
    31: {"topic": "Binary Trees — Path Problems", "phase": "Intermediate"},
    32: {"topic": "Binary Search Trees", "phase": "Intermediate"},
    33: {"topic": "BST — Validation, Insert, Delete", "phase": "Intermediate"},
    34: {"topic": "Binary Trees — Lowest Common Ancestor", "phase": "Intermediate"},
    35: {"topic": "Trees — Mixed Review", "phase": "Intermediate"},
    # Week 6 - Heaps & Graphs Intro
    36: {"topic": "Heaps & Priority Queues", "phase": "Intermediate"},
    37: {"topic": "Top-K Problems with Heaps", "phase": "Intermediate"},
    38: {"topic": "Graphs — Representation & BFS", "phase": "Intermediate"},
    39: {"topic": "Graphs — DFS & Connected Components", "phase": "Intermediate"},
    40: {"topic": "Graphs — Cycle Detection", "phase": "Intermediate"},
    41: {"topic": "Graphs — Topological Sort", "phase": "Intermediate"},
    42: {"topic": "Heap + Graph — Mixed Review", "phase": "Intermediate"},
    # Week 7 - Dynamic Programming Intro
    43: {"topic": "DP — Introduction & Memoization", "phase": "Intermediate"},
    44: {"topic": "DP — 1D Problems (Climbing Stairs, House Robber)", "phase": "Intermediate"},
    45: {"topic": "DP — Knapsack Variants", "phase": "Intermediate"},
    46: {"topic": "DP — Longest Common Subsequence", "phase": "Intermediate"},
    47: {"topic": "DP — Longest Increasing Subsequence", "phase": "Intermediate"},
    48: {"topic": "DP — Coin Change & Unbounded Knapsack", "phase": "Intermediate"},
    49: {"topic": "DP — Mixed Review Day 1", "phase": "Intermediate"},
    # Week 8 - Advanced DP & Backtracking
    50: {"topic": "DP — 2D Grid Problems", "phase": "Advanced"},
    51: {"topic": "DP — String DP (Edit Distance, Regex)", "phase": "Advanced"},
    52: {"topic": "Backtracking — Subsets & Permutations", "phase": "Advanced"},
    53: {"topic": "Backtracking — Combinations & N-Queens", "phase": "Advanced"},
    54: {"topic": "Backtracking — Sudoku & Word Search", "phase": "Advanced"},
    55: {"topic": "DP + Backtracking — Mixed Review", "phase": "Advanced"},
    56: {"topic": "Advanced Trees — Tries", "phase": "Advanced"},
    # Week 9 - Advanced Graphs
    57: {"topic": "Graphs — Shortest Path (Dijkstra)", "phase": "Advanced"},
    58: {"topic": "Graphs — Bellman-Ford & SSSP", "phase": "Advanced"},
    59: {"topic": "Graphs — Union Find / Disjoint Sets", "phase": "Advanced"},
    60: {"topic": "Graphs — Minimum Spanning Tree (Kruskal/Prim)", "phase": "Advanced"},
    61: {"topic": "Graphs — Advanced BFS (01-BFS, Multi-source)", "phase": "Advanced"},
    62: {"topic": "Graphs — Strongly Connected Components", "phase": "Advanced"},
    63: {"topic": "Graphs — Mixed Hard Review", "phase": "Advanced"},
    # Week 10 - Advanced Data Structures
    64: {"topic": "Segment Trees & Range Queries", "phase": "Advanced"},
    65: {"topic": "Binary Indexed Tree (Fenwick Tree)", "phase": "Advanced"},
    66: {"topic": "Monotonic Stack & Queue", "phase": "Advanced"},
    67: {"topic": "Interval Problems (Merge, Insert, Sweep Line)", "phase": "Advanced"},
    68: {"topic": "Bit Manipulation", "phase": "Advanced"},
    69: {"topic": "Math & Number Theory Problems", "phase": "Advanced"},
    70: {"topic": "Advanced DS — Mixed Review", "phase": "Advanced"},
    # Week 11 - System Design Coding Patterns
    71: {"topic": "Design Problems — LRU Cache", "phase": "Advanced"},
    72: {"topic": "Design Problems — LFU Cache & In-Memory Store", "phase": "Advanced"},
    73: {"topic": "Design Problems — Twitter/News Feed", "phase": "Advanced"},
    74: {"topic": "Design Problems — Rate Limiter & Hit Counter", "phase": "Advanced"},
    75: {"topic": "Design Problems — Autocomplete & Search", "phase": "Advanced"},
    76: {"topic": "Design Problems — File System & Directory", "phase": "Advanced"},
    77: {"topic": "Design — Mixed Review", "phase": "Advanced"},
    # Week 12 - Mock Interview Sprint
    78: {"topic": "Mock Interview Day 1 — Arrays & Strings", "phase": "Advanced"},
    79: {"topic": "Mock Interview Day 2 — Trees & Graphs", "phase": "Advanced"},
    80: {"topic": "Mock Interview Day 3 — DP", "phase": "Advanced"},
    81: {"topic": "Mock Interview Day 4 — Mixed FAANG Set", "phase": "Advanced"},
    82: {"topic": "Mock Interview Day 5 — Google Focus", "phase": "Advanced"},
    83: {"topic": "Mock Interview Day 6 — Amazon Focus", "phase": "Advanced"},
    84: {"topic": "Mock Interview Day 7 — Meta Focus", "phase": "Advanced"},
    # Week 13 - Final Hard Problems
    85: {"topic": "Hard Problems — DP on Trees", "phase": "Advanced"},
    86: {"topic": "Hard Problems — Graph + DP Combos", "phase": "Advanced"},
    87: {"topic": "Hard Problems — String Advanced (Z-algorithm, KMP)", "phase": "Advanced"},
    88: {"topic": "Hard Problems — Geometry & Sweep Line", "phase": "Advanced"},
    89: {"topic": "Hard Problems — Competitive Programming Set", "phase": "Advanced"},
    90: {"topic": "Final Review — Full Sprint All Topics", "phase": "Advanced"},
}


def build_prompt(day: int) -> str:
    info = PLAN.get(day, {"topic": "Mixed Review", "phase": "Advanced"})
    topic = info["topic"]
    phase = info["phase"]
    prev_topics = [PLAN[d]["topic"] for d in range(max(1, day-7), day)]
    prev_str = ", ".join(prev_topics) if prev_topics else "None"

    return f"""You are an expert competitive programming coach.

Generate a daily coding practice email for Day {day} of 90.

## TODAY'S FOCUS
- Topic: {topic}
- Phase: {phase}
- Day: {day} / 90
- Recent topics covered: {prev_str}

## STRICT RULES — READ CAREFULLY
1. Select exactly 5 questions: 2 Easy, 2 Medium, 1 Hard
2. ALL questions must be FREE on LeetCode (no LeetCode Premium required)
3. Questions must be REAL, well-known problems with correct problem numbers and URLs
4. Questions must be relevant to today's topic: {topic}
5. DO NOT include any solutions, code, hints, or approaches — questions only
6. DO NOT include time/space complexity — questions only
7. DO NOT include "how to solve" guidance of any kind
8. Include both a LeetCode link AND a GFG link for each question where available
9. Difficulty must match the phase: {phase}
10. Do NOT repeat problems from recent days

## FOR EACH OF THE 5 QUESTIONS INCLUDE ONLY:
- Question number (1–5) and difficulty label
- Problem title and LeetCode problem number
- A ONE sentence description of what the problem asks (no hints, no approach)
- LeetCode link (free tier): https://leetcode.com/problems/problem-slug/
- GFG link if available: https://www.geeksforgeeks.org/...
- Nothing else — no solutions, no code, no hints

## EMAIL STRUCTURE

### Header section:
- Title: "Day {day}/90 — {topic}"
- Phase badge: {phase}
- Progress bar (HTML/CSS) showing {day} out of 90
- One paragraph (2–3 sentences) on WHY this topic is important for interviews — concepts only, no solutions
- Estimated time to solve all 5: X–Y minutes

### 5 Question Cards
One card per question, clean and minimal. Each card contains ONLY:
- Question number + difficulty badge
- Problem name + LeetCode number
- One-sentence problem description (what it asks, not how to solve)
- "Solve on LeetCode" button link
- "Read on GFG" button link (if available)

### Daily Tip section (3 items):
- 1 pattern recognition tip for today's topic (what to look for, NOT how to solve)
- 1 common interview mistake to avoid on this topic
- 1 question to ask yourself before starting any problem of this type

### Tomorrow Preview:
- Topic for Day {day+1 if day < 90 else 1}
- One sentence on what to expect

## FORMATTING REQUIREMENTS
Output must be a complete, beautiful HTML document suitable for Gmail.
- Use inline CSS only (Gmail strips <style> tags)
- Max width 800px, centered, background #f5f5f5
- Each question in a white card: background:white, border-radius:12px, padding:24px, margin-bottom:16px, box-shadow:0 2px 8px rgba(0,0,0,0.08)
- Difficulty badges inline: Easy=background:#e6f7f4,color:#00b8a3 | Medium=background:#fff4e5,color:#ffa116 | Hard=background:#fff0f0,color:#ff375f — all bold, border-radius:4px, padding:3px 10px
- "Solve on LeetCode" button: background:#ffa116, color:white, padding:8px 16px, border-radius:6px, text-decoration:none, font-weight:bold, display:inline-block, margin-right:8px
- "Read on GFG" button: background:#2f8d46, color:white, padding:8px 16px, border-radius:6px, text-decoration:none, font-weight:bold, display:inline-block
- Progress bar: div with background:#e0e0e0, inner div width:{round(day/90*100)}%, background:linear-gradient(90deg,#ffa116,#ff375f), height:10px, border-radius:5px
- Header card: background:linear-gradient(135deg,#1a1a2e,#16213e), color:white, padding:32px, border-radius:12px, margin-bottom:24px
- Section headers: font-size:18px, font-weight:bold, border-left:4px solid #ffa116, padding-left:12px, margin:24px 0 12px 0
- The output must be a SINGLE complete HTML document starting with <!DOCTYPE html>
- Do NOT use external images or external CSS files
- Inline ALL styles on every element

The email should feel clean, motivating, and distraction-free — like a daily challenge card, not a tutorial."""


def call_deepseek(day: int, max_retries: int = 3) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": build_prompt(day)},
        ],
        "max_tokens": 8192,
        "temperature": 0.3,
        "stream": False,
    }

    for attempt in range(1, max_retries + 1):
        print(f"[leetcode] Attempt {attempt}/{max_retries} — calling DeepSeek for Day {day}...")
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {})
            print(f"[leetcode] Success — tokens: {tokens}")
            return content
        except requests.exceptions.Timeout:
            print(f"[leetcode] Timeout on attempt {attempt}.")
        except requests.exceptions.HTTPError as e:
            print(f"[leetcode] HTTP error: {e.response.status_code} {e.response.text}")
            if e.response.status_code in (400, 401, 403):
                raise
        except Exception as e:
            print(f"[leetcode] Error on attempt {attempt}: {e}")

        if attempt < max_retries:
            wait = 15 * attempt
            print(f"[leetcode] Waiting {wait}s before retry...")
            time.sleep(wait)

    raise RuntimeError(f"Failed after {max_retries} attempts.")


def ensure_html(content: str, day: int) -> str:
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    if not content.lower().startswith("<!doctype"):
        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LeetCode Daily — Day {day}</title>
</head>
<body>
{content}
</body>
</html>"""
    return content


def main():
    print(f"[leetcode] Generating questions for Day {CURRENT_DAY}...")
    html = call_deepseek(CURRENT_DAY)
    html = ensure_html(html, CURRENT_DAY)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"[leetcode] Saved to {OUTPUT_FILE} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
