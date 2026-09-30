#!/usr/bin/env python3
"""
One-command self-check for CS460 Module 4.

    python3 grader/selfcheck.py

What it does:
  * If an answers file (lab1_answers.json / lab2_answers.json) or mp1.zip is in
    the CURRENT folder, it grades it and prints your score.
  * If nothing is there yet, it writes a ready-to-edit answer template and tells
    you to fill it in -- then run this again.

You never have to remember the individual grader commands or hand-write JSON.
Resubmit any time this term.
"""
import os, sys, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATES = {
    "lab1_answers.json": {
        "_how_to": "Fill in your answers, then run:  python3 grader/selfcheck.py",
        "q1_trusted_flows": [
            "10.11.12.100:PORT -> 10.11.12.102:502",
            "(add the other steady-state polls: yaw .101, blades .103/.104/.105)"
        ],
        "q2_new_interaction": {"what_i_did": "", "flow": "A:port -> B:port"},
        "q3_adversary_changes": "",
        "q4_long_windows": ""
    },
    "lab2_answers.json": {
        "_how_to": "Fill in your answers, then run:  python3 grader/selfcheck.py",
        "q1_trusted_flows": ["FARM_IP:port -> WTG_IP:20000"],
        "q2_hmi_credentials": "user/pass",
        "q3_new_interaction": {"what_i_did": "", "flow": "A:port -> B:port"},
        "q4_modbus_vs_dnp3": ""
    },
}

GRADERS = [
    ("lab1_answers.json", "grade_lab1.py"),
    ("lab2_answers.json", "grade_lab2.py"),
    ("mp1.zip",           "grade_mp1.py"),
]

def run(grader, target):
    subprocess.run([sys.executable, os.path.join(HERE, grader), target])

def _untouched(path):
    """True if the file is still the pristine template we created (nothing filled in)."""
    try:
        d = json.load(open(path))
    except Exception:
        return False
    if "_how_to" not in d:
        return False
    prose = str(d.get("q3_adversary_changes","")) + str(d.get("q4_modbus_vs_dnp3","")) + str(d.get("q4_long_windows",""))
    creds = str(d.get("q2_hmi_credentials","user/pass"))
    return prose.strip() == "" and creds in ("", "user/pass")

def main():
    graded = False
    skipped = []
    for target, grader in GRADERS:
        if os.path.exists(target):
            if target.endswith(".json") and _untouched(target):
                skipped.append(target)
                continue
            if graded: print()
            run(grader, target)
            graded = True

    for s in skipped:
        print(f"(skipped {s} -- it's still the blank template; fill it in when you get to that lab)")

    if graded:
        return

    # Nothing to grade -- set the student up.
    made = []
    for name, tpl in TEMPLATES.items():
        if not os.path.exists(name):
            with open(name, "w") as f:
                json.dump(tpl, f, indent=2)
            made.append(name)

    print("Nothing to grade in this folder yet.")
    if made:
        print("\nI created these answer template(s) for you:")
        for m in made:
            print(f"  - {m}")
        print("\nOpen the file for your lab, fill in your answers, then run:")
    else:
        print("\nFill in your answers file, then run:")
    print("    python3 grader/selfcheck.py")
    print("\nFor MP1: put your mp1.zip in this folder and run the same command.")

if __name__ == "__main__":
    main()
