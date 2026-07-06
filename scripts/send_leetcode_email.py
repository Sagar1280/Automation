"""
send_leetcode_email.py
Reads leetcode_output.html and sends it as an HTML email.
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

SMTP_HOST  = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT  = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER  = os.environ["SMTP_USER"]
SMTP_PASS  = os.environ["SMTP_PASS"]
TO_EMAIL   = os.environ.get("TO_EMAIL", "Sagarmurali2004@gmail.com")
CURRENT_DAY = int(os.environ.get("CURRENT_DAY", "1"))
INPUT_FILE  = "leetcode_output.html"

PLAN_TOPICS = {
    1:"Arrays — Basics & Traversal",2:"Arrays — Two Pointers",3:"Arrays — Sliding Window",
    4:"Strings — Basics & Manipulation",5:"Strings — Palindromes & Anagrams",
    6:"Strings — Substrings & Pattern Matching",7:"Arrays & Strings — Mixed Review",
    8:"HashMap & HashSet Fundamentals",9:"Frequency Counting with HashMap",
    10:"Prefix Sums & Subarray Problems",11:"Two Sum Variants & Hashing",
    12:"Sorting — Basic Algorithms",13:"Sorting — Custom Comparators",
    14:"Hashing + Sorting — Mixed Review",15:"Linked Lists — Basics & Traversal",
    16:"Linked Lists — Reversal Patterns",17:"Linked Lists — Fast & Slow Pointers",
    18:"Linked Lists — Merge & Sort",19:"Stacks — Basics & Applications",
    20:"Queues & Deques",21:"Stack & Queue — Mixed Review",
    22:"Recursion — Fundamentals",23:"Recursion — Backtracking Intro",
    24:"Binary Search — Basics",25:"Binary Search — On Answer",
    26:"Binary Search — Rotated & Variants",27:"Recursion + Binary Search — Mixed Review",
    28:"Week 4 Consolidation",29:"Binary Trees — Basics & DFS",
    30:"Binary Trees — BFS & Level Order",31:"Binary Trees — Path Problems",
    32:"Binary Search Trees",33:"BST — Validation, Insert, Delete",
    34:"Binary Trees — LCA",35:"Trees — Mixed Review",
    36:"Heaps & Priority Queues",37:"Top-K Problems with Heaps",
    38:"Graphs — BFS",39:"Graphs — DFS & Connected Components",
    40:"Graphs — Cycle Detection",41:"Graphs — Topological Sort",
    42:"Heap + Graph — Mixed Review",43:"DP — Introduction & Memoization",
    44:"DP — 1D Problems",45:"DP — Knapsack Variants",
    46:"DP — LCS",47:"DP — LIS",48:"DP — Coin Change",
    49:"DP — Mixed Review",50:"DP — 2D Grid Problems",
    51:"DP — String DP",52:"Backtracking — Subsets & Permutations",
    53:"Backtracking — Combinations & N-Queens",54:"Backtracking — Sudoku & Word Search",
    55:"DP + Backtracking — Mixed Review",56:"Advanced Trees — Tries",
    57:"Graphs — Dijkstra",58:"Graphs — Bellman-Ford",
    59:"Graphs — Union Find",60:"Graphs — MST",
    61:"Graphs — Advanced BFS",62:"Graphs — SCC",
    63:"Graphs — Mixed Hard Review",64:"Segment Trees",
    65:"Fenwick Tree",66:"Monotonic Stack & Queue",
    67:"Interval Problems",68:"Bit Manipulation",
    69:"Math & Number Theory",70:"Advanced DS — Mixed Review",
    71:"Design — LRU Cache",72:"Design — LFU Cache",
    73:"Design — Twitter Feed",74:"Design — Rate Limiter",
    75:"Design — Autocomplete",76:"Design — File System",
    77:"Design — Mixed Review",78:"Mock Interview — Arrays & Strings",
    79:"Mock Interview — Trees & Graphs",80:"Mock Interview — DP",
    81:"Mock Interview — Mixed FAANG",82:"Mock Interview — Google",
    83:"Mock Interview — Amazon",84:"Mock Interview — Meta",
    85:"Hard — DP on Trees",86:"Hard — Graph + DP",
    87:"Hard — String Advanced",88:"Hard — Geometry",
    89:"Hard — Competitive Programming",90:"Final Review — Full Sprint",
}

def build_message(html_body: str) -> MIMEMultipart:
    topic = PLAN_TOPICS.get(CURRENT_DAY, "Mixed Review")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"💻 LeetCode Daily — Day {CURRENT_DAY}/90 | {topic} | 2 Easy + 2 Medium + 1 Hard"
    msg["From"]    = f"LeetCode Daily <{SMTP_USER}>"
    msg["To"]      = TO_EMAIL

    plain = (
        f"Day {CURRENT_DAY}/90 — {topic}\n\n"
        "Today's 5 questions: 2 Easy, 2 Medium, 1 Hard\n"
        "All questions are free on LeetCode.\n"
        "Open in an HTML email client for the full experience."
    )

    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    attachment = MIMEBase("text", "html")
    attachment.set_payload(html_body.encode("utf-8"))
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition", "attachment",
        filename=f"leetcode_day_{CURRENT_DAY:02d}.html",
    )
    msg.attach(attachment)
    return msg


def send_email(msg: MIMEMultipart) -> None:
    print(f"[email] Connecting to {SMTP_HOST}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        print(f"[email] Logging in as {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASS)
        print(f"[email] Sending to {TO_EMAIL}...")
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
    print(f"[email] LeetCode Day {CURRENT_DAY} sent to {TO_EMAIL}")


def main():
    path = Path(INPUT_FILE)
    if not path.exists():
        print(f"[email] ERROR: {INPUT_FILE} not found.")
        sys.exit(1)
    html = path.read_text(encoding="utf-8")
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"[email] Loaded {INPUT_FILE} ({size_kb:.1f} KB)")
    if size_kb > 90:
        print(f"[email] Warning: {size_kb:.1f} KB — Gmail may clip. Full content in attachment.")
    msg = build_message(html)
    send_email(msg)


if __name__ == "__main__":
    main()
