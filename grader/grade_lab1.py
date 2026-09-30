#!/usr/bin/env python3
"""
Lab 1 self-check  --  CS460 Module 4 (Document Interactions, 24 pts)
====================================================================
Students fill lab1_answers.json (template below) and run:
    python3 grade_lab1.py lab1_answers.json
Gives instant feedback so they can fix and resubmit. The SAME grader run by
the instructor produces the recorded score.

Correctness anchors are stored as SALTED SHA-256 HASHES, so this file reveals
no answers even in source. Open-ended answers get a structural check plus a
HUMAN-REVIEW flag (prose can't be mechanically graded). Obfuscate per README
to also hide the checking logic.

Template (lab1_answers.json):
{
  "q1_trusted_flows": ["10.11.12.100:PORT -> 10.11.12.102:502", "..."],
  "q2_new_interaction": {"what_i_did": "...", "flow": "A:port -> B:port"},
  "q3_adversary_changes": "how the AitM changes the interactions ...",
  "q4_long_windows": "why long snapshot windows matter ..."
}
"""
import sys, os, json, hashlib, re

SALT = "cs460-m4-l1-v1"   # change SALT + regenerate hashes to rotate answers
# salted sha256 of normalized correctness anchors (set with make_hashes.py)
ANCHORS = {
    # Q1: the main controller must be documented polling the anemometer on 502
    "q1_anemometer_poll": "c40ea532f6ed509a34ae7c45c49b4eb1dca3ae8279fe58cf6015b7de11b5ead6",
    # normalized form hashed: "10.11.12.100->10.11.12.102:502"
}

def _h(s):
    return hashlib.sha256((SALT + "|" + s).encode()).hexdigest()

def _norm_flow(s):
    s = s.lower().replace(" ", "")
    s = s.replace("→", "->").replace("=>", "->").replace("--", "-")
    m = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?', s)
    # canonical: src_ip->dst_ip:dstport   (drop ephemeral src port)
    if len(m) >= 2:
        src = m[0][0]; dst = m[-1][0]; dport = m[-1][1] or ""
        return f"{src}->{dst}:{dport}"
    return s

def grade(path):
    try: ans = json.load(open(path))
    except Exception as e: print(f"ERROR reading {path}: {e}"); sys.exit(2)
    score = 0; review = []
    print("="*60); print("LAB 1 SELF-CHECK"); print("="*60)

    # Q1 (6): trusted flows, format + the anemometer poll anchor
    flows = ans.get("q1_trusted_flows", [])
    fmt_ok = isinstance(flows, list) and sum(1 for f in flows if _norm_flow(str(f)).count(".")>=6) >= 2
    anem = any(_h(_norm_flow(str(f))) == ANCHORS["q1_anemometer_poll"] for f in flows)
    q1 = (3 if fmt_ok else 0) + (3 if anem else 0)
    print(f"[{'PASS' if q1==6 else '----'}] Q1 trusted flows        {q1}/6")
    if not fmt_ok: print("     -> list flows as src IP:port -> dst IP:port (need at least the steady-state ones)")
    if not anem:  print("     -> make sure you documented the main controller polling the anemometer on :502")

    # Q2 (6): a new non-adversarial interaction you caused (structural)
    q2o = ans.get("q2_new_interaction", {})
    q2 = 6 if isinstance(q2o, dict) and str(q2o.get("what_i_did","")).strip() and \
             _norm_flow(str(q2o.get("flow",""))).count(".")>=6 else 0
    print(f"[{'PASS' if q2==6 else '----'}] Q2 new interaction      {q2}/6")
    if q2==0: print("     -> describe what you did AND give its flow as src IP:port -> dst IP:port")

    # Q3 (6): how the adversary changes interactions during AitM -> human review
    q3txt = str(ans.get("q3_adversary_changes","")).strip()
    q3_ok = len(q3txt) >= 60
    print(f"[{'SEEN' if q3_ok else '----'}] Q3 adversary changes    {'(ready for review)' if q3_ok else '0/6'}")
    if not q3_ok: print("     -> explain the new/altered flows the AitM introduces (e.g. the attacker in the path, zeroed reads)")
    else: review.append("Q3 (6 pts) -- reviewed by instructor")

    # Q4 (6): why long snapshot windows -> human review
    q4txt = str(ans.get("q4_long_windows","")).strip()
    q4_ok = len(q4txt) >= 60
    print(f"[{'SEEN' if q4_ok else '----'}] Q4 long windows         {'(ready for review)' if q4_ok else '0/6'}")
    if not q4_ok: print("     -> explain periodic/low-frequency traffic a short capture can miss")
    else: review.append("Q4 (6 pts) -- reviewed by instructor")

    score = q1 + q2
    print("-"*60)
    print(f"AUTO-CHECKED: {score}/12   (Q3+Q4 = 12 pts are instructor-reviewed)")
    if review: print("Ready for review: " + "; ".join(review))
    print("Fix any '----' items and resubmit. You can resubmit any time this term.")
    return score

if __name__ == "__main__":
    a=[x for x in sys.argv[1:] if not x.startswith("--")]
    if not a: print("usage: python3 grade_lab1.py lab1_answers.json"); sys.exit(2)
    grade(a[0])
