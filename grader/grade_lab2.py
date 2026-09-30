#!/usr/bin/env python3
"""
Lab 2 self-check  --  CS460 Module 4 (Wind Farm & DNP3, 24 pts)
===============================================================
Students fill lab2_answers.json and run:
    python3 grade_lab2.py lab2_answers.json
Instant feedback; resubmit any time. Instructor runs the same grader for the
recorded score. Correctness anchors are salted SHA-256 hashes (no answers in
source); open-ended Q4 gets a keyword check + human-review flag.

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
    # allow hostname:port form (wtg-1:20000)
    m2 = re.search(r'(:20000)\b', s)
    return "dnp3:20000" if m2 else s

def _norm_creds(s):
    s = s.lower().strip().replace(" ", "")
    return s.replace(":", "/")

def grade(path):
    try: ans = json.load(open(path))
    except Exception as e: print(f"ERROR reading {path}: {e}"); sys.exit(2)
    print("="*60); print("LAB 2 SELF-CHECK"); print("="*60)

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

    # Q4 (9): Modbus vs DNP3 -> keyword check + human review
    q4 = str(ans.get("q4_modbus_vs_dnp3","")).lower()
    hits = sum(bool(re.search(p, q4)) for p in
               [r'register', r'typed|analog|binary|point', r'select.?before.?operate|sbo',
                r'timestamp|event', r'unsolicit'])
    q4_ok = len(q4.strip()) >= 80 and hits >= 3
    print(f"[{'SEEN' if q4_ok else '----'}] Q4 Modbus vs DNP3       {'(>=3 concrete differences, ready for review)' if q4_ok else '0/9'}")
    if not q4_ok: print("     -> name at least three concrete differences (data model, addressing, SBO, events/timestamps, unsolicited)")

    auto = q1 + q2 + q3
    print("-"*60)
    print(f"AUTO-CHECKED: {auto}/15   (Q4 = 9 pts: keyword-screened, instructor-reviewed)")
    print("Fix any '----' items and resubmit.")
    return auto

if __name__ == "__main__":
    a=[x for x in sys.argv[1:] if not x.startswith("--")]
    if not a: print("usage: python3 grade_lab2.py lab2_answers.json"); sys.exit(2)
    grade(a[0])
