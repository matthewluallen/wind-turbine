#!/usr/bin/env python3
"""
MP1 self-check / autograder  --  CS460 Module 4
================================================
Students run this against their mp1.zip to get instant rubric feedback and
iterate before submitting. The SAME script, run by the instructor/CI with
--official, produces the recorded score (see README: the client is reversible
by design -- reversing it is an accepted bonus; the official score is produced
where students can't touch it).

Usage (student self-check):   python3 grade_mp1.py mp1.zip
Usage (official, instructor): python3 grade_mp1.py mp1.zip --official

Exit code 0 = all mechanical checks passed; non-zero = something to fix.
This file validates STRUCTURE (Caldera Event Log schema, required files,
navigator layer, detection artifact, standards mapping). It contains no
answer keys, so it is safe to ship in source; obfuscate per the README to
hide the grading logic/weights as well.
"""
import sys, os, json, zipfile, io, re

# --- rubric weights (Canvas MP1 = 100) -------------------------------------
RUBRIC = {
    "files_format":        5,
    "facts_yml":          10,
    "check_json":         12,
    "break_json":         17,
    "fix_txt":            15,
    "secure_json":        20,
    "navigator_json":      6,
    "detection_artifact": 10,
    "standards_mapping":   5,
}
REQUIRED_FILES = ["check.json", "break.json", "secure.json", "facts.yml",
                  "fix.txt", "navigator.json"]
# every Caldera Event Log entry must carry these (confirmed from caldera source)
EVENT_REQUIRED = {
    "operation_metadata": ["operation_name", "operation_start"],
    "ability_metadata":   ["ability_id", "ability_name"],
    "agent_metadata":     ["paw"],
}

class Report:
    def __init__(self): self.items=[]; self.score=0
    def add(self, key, ok, earned, hint=""):
        self.items.append((key, ok, earned, RUBRIC.get(key,0), hint)); self.score+=earned
    def show(self, official=False):
        print("="*66); print(f"MP1 {'OFFICIAL' if official else 'SELF-CHECK'} REPORT"); print("="*66)
        for key, ok, earned, poss, hint in self.items:
            mark = "PASS" if ok else "----"
            print(f"[{mark}] {key:<20} {earned:>3}/{poss:<3}" + (f"   -> {hint}" if hint and not ok else ""))
        print("-"*66); print(f"MECHANICAL TOTAL: {self.score}/100")
        print("Note: correctness of the attack/remediation content is reviewed by a human;")
        print("this checks that the artifacts are present, valid, and well-formed.")

def _load_zip(path):
    if not os.path.exists(path): print(f"ERROR: {path} not found"); sys.exit(2)
    try: z=zipfile.ZipFile(path)
    except Exception as e: print(f"ERROR: not a valid zip: {e}"); sys.exit(2)
    return {os.path.basename(n): z.read(n) for n in z.namelist() if not n.endswith('/')}

def _json(files, name):
    try: return json.loads(files[name].decode("utf-8", "replace")), None
    except KeyError: return None, "missing"
    except Exception as e: return None, f"invalid JSON ({e})"

def _check_event_log(obj):
    """Return (ok, hint). Caldera Event Logs = a JSON array of event objects."""
    if not isinstance(obj, list) or not obj:
        return False, "expected a non-empty JSON array of Caldera events (Download -> Event Logs)"
    ev = obj[0]
    if not isinstance(ev, dict):
        return False, "events must be JSON objects"
    for block, keys in EVENT_REQUIRED.items():
        if block not in ev: return False, f"event missing '{block}' (re-export Event Logs, don't hand-edit)"
        for k in keys:
            if k not in ev[block]: return False, f"event {block} missing '{k}'"
    return True, ""

def grade(path, official=False):
    r = Report(); files = _load_zip(path)

    # 1. files & format
    missing = [f for f in REQUIRED_FILES if f not in files]
    r.add("files_format", not missing, 0 if missing else RUBRIC["files_format"],
          f"missing: {', '.join(missing)}" if missing else "")

    # 2. facts.yml present & non-trivial
    fy = files.get("facts.yml", b"")
    ok = bool(fy) and b":" in fy
    r.add("facts_yml", ok, RUBRIC["facts_yml"] if ok else 0,
          "facts.yml missing or empty (Caldera operation facts)")

    # 3/4/6 Caldera Event Logs
    for name, key in (("check.json","check_json"),("break.json","break_json"),("secure.json","secure_json")):
        obj, err = _json(files, name)
        if err: r.add(key, False, 0, err); continue
        ok, hint = _check_event_log(obj); r.add(key, ok, RUBRIC[key] if ok else 0, hint)

    # 5. fix.txt present & has remediation narration
    ft = files.get("fix.txt", b"").decode("utf-8","replace")
    ok = len(ft.strip()) >= 80
    r.add("fix_txt", ok, RUBRIC["fix_txt"] if ok else 0,
          "fix.txt too short -- narrate the commands/config you applied")

    # 7. navigator.json = valid ATT&CK Navigator layer
    nav, err = _json(files, "navigator.json")
    if err: r.add("navigator_json", False, 0, err)
    else:
        ok = isinstance(nav, dict) and "techniques" in nav and ("name" in nav or "domain" in nav)
        r.add("navigator_json", ok, RUBRIC["navigator_json"] if ok else 0,
              "not a Navigator layer (needs name/domain + techniques[])")

    # 8. detection artifact (any of: detection.*, a rule file, or an alert doc)
    det = next((n for n in files if re.search(r'(detection|suricata|zeek|\.rules?$)', n, re.I)), None)
    dok = det is not None and len(files[det].strip()) > 20
    r.add("detection_artifact", dok, RUBRIC["detection_artifact"] if dok else 0,
          "include a detection file (e.g. detection.txt): a rule/threshold + 1-paragraph explanation")

    # 9. standards mapping inside fix.txt (NIST 800-53/800-82 or IEC 62443)
    smap = bool(re.search(r'(800-53|800-82|iec\s*62443|62443-3-3|sr\s*\d)', ft, re.I))
    r.add("standards_mapping", smap, RUBRIC["standards_mapping"] if smap else 0,
          "map each remediation to a control (NIST 800-53 per 800-82, or IEC 62443-3-3 SR) in fix.txt")

    r.show(official)
    return r.score

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    official = "--official" in sys.argv
    if not args:
        print("usage: python3 grade_mp1.py mp1.zip [--official]"); sys.exit(2)
    score = grade(args[0], official)
    sys.exit(0 if score == 100 else 1)
