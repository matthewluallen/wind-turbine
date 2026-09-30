#!/usr/bin/env python3
"""
Lab 2 self-check  --  CS460 Module 4 (Wind Farm & DNP3, 24 pts)
===============================================================
Fill lab2_answers.json and run:
    python3 grade_lab2.py lab2_answers.json
Instant feedback; resubmit any time. Instructor runs the same grader for the
recorded score.

FULLY DETERMINISTIC (no LLM). Correctness anchors are salted SHA-256 hashes
(no answers in source). Q4 (Modbus vs DNP3) now auto-scores by CONCEPT
COVERAGE: 3 points per distinct difference-category named, capped at 9. It
prints the categories it detected so the instructor can spot-check for
keyword-stuffing.

Template (lab2_answers.json):
{
  "q1_trusted_flows": ["FARM_IP:port -> WTG_IP:20000", "..."],
  "q2_hmi_credentials": "user/pass",
  "q3_new_interaction": {"what_i_did": "...", "flow": "A:port -> B:port"},
  "q4_modbus_vs_dnp3": "at least three concrete differences ..."
}
"""
import sys, os, json, hashlib, re

SALT = "cs460-m4-l2-v1"
ANCHORS = {
    "q1_dnp3_poll":  "0298b18ddda97c1283e342f688ddf34ec0b9a55a91c2764b4ceea0593ba0d913",   # farm -> wtg:20000
    "q2_hmi_creds":  "9bbbe38e25f255a4732c13d3d9bc7e4cd22655ad5072ae7d765d54d7b8c8e922",   # foo/bar
}

def _h(s): return hashlib.sha256((SALT + "|" + s).encode()).hexdigest()

def _norm_flow(s):
    s = s.lower().replace(" ", "").replace("→","->").replace("=>","->")
    m = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?', s)
    if len(m) >= 2:
        return f"{m[0][0]}->{m[-1][0]}:{m[-1][1] or ''}"
    m2 = re.search(r'(:20000)\b', s)
    return "dnp3:20000" if m2 else s

def _norm_creds(s):
    s = s.lower().strip().replace(" ", "")
    return s.replace(":", "/")

def grade(path):
    try: ans = json.load(open(path))
    except Exception as e: print(f"ERROR reading {path}: {e}"); sys.exit(2)
    print("="*64); print("LAB 2 SELF-CHECK  (deterministic; no LLM)"); print("="*64)

    # Q1 (6): DNP3 farm->turbine flows
    flows = ans.get("q1_trusted_flows", [])
    fmt_ok = isinstance(flows, list) and len(flows) >= 1
    dnp3 = any(_h(_norm_flow(str(f))) == ANCHORS["q1_dnp3_poll"] or ":20000" in str(f) for f in flows)
    q1 = (3 if fmt_ok else 0) + (3 if dnp3 else 0)
    print(f"[{'PASS' if q1==6 else '----'}] Q1 trusted flows        {q1}/6")
    if not fmt_ok: print("     -> list flows as src IP:port -> dst IP:port")
    if not dnp3:  print("     -> document the farm controller polling a turbine over DNP3 on :20000")

    # Q2 (3): HMI credentials (anchor)
    creds = _norm_creds(str(ans.get("q2_hmi_credentials","")))
    q2 = 3 if _h(creds) == ANCHORS["q2_hmi_creds"] else 0
    print(f"[{'PASS' if q2==3 else '----'}] Q2 HMI credentials      {q2}/3")
    if q2==0: print("     -> give the Farm HMI username/password (see farm repo README / login banner)")

    # Q3 (6): new non-adversarial interaction (structural)
    q3o = ans.get("q3_new_interaction", {})
    q3 = 6 if isinstance(q3o, dict) and str(q3o.get("what_i_did","")).strip() and \
             _norm_flow(str(q3o.get("flow",""))).count(".")>=6 else 0
    print(f"[{'PASS' if q3==6 else '----'}] Q3 new interaction      {q3}/6")
    if q3==0: print("     -> describe what you did AND its flow as src IP:port -> dst IP:port")

    # Q4 (9): Modbus vs DNP3 -> coverage score, 3 pts per distinct difference category
    q4txt = str(ans.get("q4_modbus_vs_dnp3","")).strip()
    categories = {
        "data-model":        r'register|coil|typed|analog|binary|point type|data model',
        "addressing":        r'address|point index|\bindex\b|group.?variation|\bobject\b|\bgroup\b',
        "control-semantics": r'select.?before.?operate|\bsbo\b|direct.?operate|control relay|operate command',
        "events-timestamps": r'timestamp|time.?tag|event|sequence of events|\bsoe\b|time.?stamped',
        "unsolicited":       r'unsolicit|report.?by.?exception|\brbe\b|push|spontaneous',
        "integrity":         r'\bcrc\b|checksum|integrity|robust|reliab',
        "transport-port":    r'\b20000\b|\b502\b|\bports?\b',
    }
    tl = q4txt.lower()
    q4_cats = [k for k, pat in categories.items() if re.search(pat, tl)]
    q4 = 0 if len(q4txt) < 60 else min(9, 3 * len(q4_cats))
    print(f"[{'PASS' if q4==9 else '----'}] Q4 Modbus vs DNP3       {q4}/9   (categories: {', '.join(q4_cats) or 'none'})")
    if q4 < 9: print("     -> name at least three concrete difference categories: data model, addressing, "
                     "control (select-before-operate), events/timestamps, unsolicited reporting, integrity, transport/port")

    total = q1 + q2 + q3 + q4
    print("-"*64)
    print(f"AUTO-SCORED TOTAL: {total}/24")
    print("Q4 is scored by concept coverage (deterministic, no LLM); the")
    print("instructor may spot-check for keyword-stuffing.")
    print("Fix any '----' items and resubmit.")
    return total

if __name__ == "__main__":
    a=[x for x in sys.argv[1:] if not x.startswith("--")]
    if not a: print("usage: python3 grade_lab2.py lab2_answers.json"); sys.exit(2)
    grade(a[0])
