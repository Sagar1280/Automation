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

    return f"""You are an expert competitive programming coach and senior software engineer at a FAANG company.

Generate a daily LeetCode practice email for Day {day} of 90.

## TODAY'S FOCUS
- Topic: {topic}
- Phase: {phase}
- Day: {day} / 90
- Recent topics covered: {prev_str}

## RULES
1. Select exactly 5 questions: 2 Easy, 2 Medium, 1 Hard
2. ALL questions must be FREE on LeetCode (no LeetCode Premium required)
3. Questions must be REAL LeetCode problems with correct problem numbers and URLs
4. Questions must be relevant to today's topic: {topic}
5. Also include 1-2 relevant GFG (GeeksforGeeks) article links per question where applicable
6. Difficulty must progress — Day {day} should be harder than Day {day-5 if day > 5 else 1}
7. Do NOT repeat problems from recent days
8. For each question provide a complete, thorough breakdown

## FOR EACH OF THE 5 QUESTIONS, INCLUDE ALL OF THE FOLLOWING:

### Question Card must contain:
- Problem title and number
- Difficulty badge (Easy/Medium/Hard) with color coding
- LeetCode URL (format: https://leetcode.com/problems/problem-slug/)
- GFG URL if a relevant article exists (format: https://www.geeksforgeeks.org/...)
- Problem statement (brief, clear)
- Examples (2 examples with input/output/explanation)
- Constraints
- Intuition — explain the "aha moment" in plain English
- Approach — step-by-step algorithm
- Time Complexity with explanation
- Space Complexity with explanation
- Java solution (clean, production-quality, with comments)
- Python solution (clean, Pythonic, with comments)
- Common mistakes beginners make
- Follow-up questions interviewers ask
- Similar problems to practice next

## EMAIL STRUCTURE

### Header
- "Day {day}/90 — {topic}" 
- Phase badge: {phase}
- Progress bar showing {day}/90
- Today's topic overview (2-3 sentences on WHY this topic matters for interviews)
- Estimated solve time

### Question Cards (5 total — 2 Easy, 2 Medium, 1 Hard)
Full breakdown as described above for each question.

### Daily Tips Section
- 1 interview tip specific to today's topic
- 1 common pattern to recognize
- 1 time/space optimization trick

### Tomorrow Preview
- Topic for Day {day+1 if day < 90 else 1}
- What to expect

## FORMATTING REQUIREMENTS
Output must be a complete, beautiful HTML document suitable for Gmail.
- Use inline CSS only (Gmail strips <style> tags)
- Max width 800px, centered
- Card-based layout with box-shadows: box-shadow: 0 2px 8px rgba(0,0,0,0.1)
- Difficulty badges: Easy=green(#00b8a3), Medium=orange(#ffa116), Hard=red(#ff375f)
- Code blocks: background:#1e1e1e, color:#d4d4d4, font-family:monospace, padding:16px, border-radius:8px
- Progress bar: HTML div with gradient
- Color scheme: professional dark accents with white cards
- LeetCode links styled as: background:#ffa116, color:white, padding:6px 12px, border-radius:4px, text-decoration:none
- GFG links styled as: background:#2f8d46, color:white, padding:6px 12px, border-radius:4px, text-decoration:none
- Section headers with left colored border (4px solid)
- The output must be a SINGLE complete HTML document starting with <!DOCTYPE html>
- Do NOT use external images or external CSS files
- Inline all styles

The result should look like a premium coding bootcamp email — professional, dense with knowledge, and immediately actionable."""


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
