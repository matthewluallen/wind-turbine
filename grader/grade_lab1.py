#!/usr/bin/env python3
"""
Lab 1 self-check  --  CS460 Module 4 (Document Interactions, 24 pts)
====================================================================
Fill lab1_answers.json (template below) and run:
    python3 grade_lab1.py lab1_answers.json
Instant feedback; resubmit any time. The SAME grader run by the instructor
produces the recorded score.

This grader is FULLY DETERMINISTIC (no LLM). Correctness anchors are salted
SHA-256 hashes (no answers in source). The two written questions (Q3, Q4) are
scored by CONCEPT COVERAGE -- a keyword/regex check for the specific ideas the
rubric asks for -- so they now auto-score too. Coverage scoring is generous and
game-able by keyword-stuffing; it prints which concepts it detected so the
instructor can spot-check. Obfuscate per README to hide the checking logic.

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
    # the five steady-state polls: main controller -> each device on Modbus/502
    "anemometer": "c40ea532f6ed509a34ae7c45c49b4eb1dca3ae8279fe58cf6015b7de11b5ead6",
    "yaw":        "fdd81e72eb8eec64654983a0daf4048593f8ca6c28079c8e3013b970dd32e9fa",
    "blade1":     "fa29ae1f24ace1e65ef7c89a3d1b154c7bcd8992251a5c9157e4d77ce8d2a18a",
    "blade2":     "ebadf234fe44286aba577f0696295835e868f6ef9eb43951552791d6a5bccfbe",
    "blade3":     "b25de8dc4432101a49558df2c5ab994b06efdd188574db97c0c33f660ce38ba9",
}

def _h(s):
    return hashlib.sha256((SALT + "|" + s).encode()).hexdigest()

def _norm_flow(s):
    s = s.lower().replace(" ", "")
    s = s.replace("→", "->").replace("=>", "->").replace("--", "-")
    m = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?', s)
    if len(m) >= 2:
        src = m[0][0]; dst = m[-1][0]; dport = m[-1][1] or ""
        return f"{src}->{dst}:{dport}"
    return s

def _coverage(text, concepts):
    t = (text or "").lower()
    hits = {k: bool(re.search(pat, t)) for k, pat in concepts.items()}
    return [k for k, v in hits.items() if v], hits

def _score_prose(text, concepts, max_pts, min_len=40, per=2):
    """Deterministic coverage score: `per` points per distinct concept, capped
    at max_pts, but 0 if the answer is too short to be a real answer."""
    text = (text or "").strip()
    matched, hits = _coverage(text, concepts)
    if len(text) < min_len:
        return 0, matched
    return min(max_pts, per * len(matched)), matched

def grade(path):
    try: ans = json.load(open(path))
    except Exception as e: print(f"ERROR reading {path}: {e}"); sys.exit(2)
    print("="*64); print("LAB 1 SELF-CHECK  (deterministic; no LLM)"); print("="*64)

    # Q1 (6): trusted flows -- 3 format + 3 for coverage of the device polls
    flows = ans.get("q1_trusted_flows", [])
    norm = [_norm_flow(str(f)) for f in flows] if isinstance(flows, list) else []
    fmt_ok = sum(1 for f in norm if f.count(".") >= 6) >= 2
    matched = {name for name, hv in ANCHORS.items() if any(_h(f) == hv for f in norm)}
    anem = "anemometer" in matched
    content = 0
    if anem:
        content = min(3, 1 + (1 if len(matched) >= 3 else 0) + (1 if len(matched) >= 5 else 0))
    q1 = (3 if fmt_ok else 0) + content
    print(f"[{'PASS' if q1==6 else '----'}] Q1 trusted flows        {q1}/6   (documented {len(matched)}/5 device polls)")
    if not fmt_ok: print("     -> list flows as src IP:port -> dst IP:port (need at least the steady-state ones)")
    if not anem:  print("     -> include the main controller polling the anemometer on :502")
    elif len(matched) < 5: print("     -> full credit wants every steady-state poll: anemometer, yaw, and the 3 blade controllers on :502")

    # Q2 (6): a new non-adversarial interaction you caused (structural)
    q2o = ans.get("q2_new_interaction", {})
    q2 = 6 if isinstance(q2o, dict) and str(q2o.get("what_i_did","")).strip() and \
             _norm_flow(str(q2o.get("flow",""))).count(".")>=6 else 0
    print(f"[{'PASS' if q2==6 else '----'}] Q2 new interaction      {q2}/6")
    if q2==0: print("     -> describe what you did AND give its flow as src IP:port -> dst IP:port")

    # Q3 (6): how the adversary changes interactions during AitM (coverage-scored)
    q3_concepts = {
        "in-the-middle":       r'man.?in.?the.?middle|in the middle|aitm|on.?path|interpos|sits? between|between the',
        "arp-spoof":           r'arp|spoof|poison',
        "rewrite/zero-modbus": r'rewrit|zero|zeroe|modif|alter|falsif|tamper|fake',
        "new-flows":           r'new (flow|interaction|conversation)|attacker.*(controller|anemometer|\.200)|redirect|iptables|reroute|10\.11\.12\.200',
    }
    q3, q3m = _score_prose(str(ans.get("q3_adversary_changes","")), q3_concepts, 6)
    print(f"[{'PASS' if q3==6 else '----'}] Q3 adversary changes    {q3}/6   (concepts: {', '.join(q3m) or 'none'})")
    if q3 < 6: print("     -> cover the attacker in the path, ARP spoofing, rewritten/zeroed Modbus responses, and the new attacker<->device flows")

    # Q4 (6): why long snapshot windows matter (coverage-scored)
    q4_concepts = {
        "periodic/low-freq":    r'periodic|infrequent|low.?frequency|rare|occasional|intermittent|seldom',
        "short-capture-misses": r'short|brief|miss|would not (see|catch)|not (see|captur)|too short|snapshot',
        "polling-cadence":      r'interval|cadence|cycle|poll|every \d|per (second|minute)|seconds|minutes|timing',
        "baseline-completeness":r'baseline|normal|complete|full picture|represent|steady.?state|establish',
    }
    q4, q4m = _score_prose(str(ans.get("q4_long_windows","")), q4_concepts, 6)
    print(f"[{'PASS' if q4==6 else '----'}] Q4 long windows         {q4}/6   (concepts: {', '.join(q4m) or 'none'})")
    if q4 < 6: print("     -> explain periodic/low-frequency traffic, why a short capture misses it, polling cadence, and baseline completeness")

    total = q1 + q2 + q3 + q4
    print("-"*64)
    print(f"AUTO-SCORED TOTAL: {total}/24")
    print("Q3/Q4 are scored by concept coverage (deterministic, no LLM); the")
    print("instructor may spot-check written answers for keyword-stuffing.")
    print("Fix any '----' items and resubmit -- any time this term.")
    return total

if __name__ == "__main__":
    a=[x for x in sys.argv[1:] if not x.startswith("--")]
    if not a: print("usage: python3 grade_lab1.py lab1_answers.json"); sys.exit(2)
    grade(a[0])
