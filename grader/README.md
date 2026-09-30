# Module 4 self-check autograders

Run these to check your own work before you submit. **You can resubmit any time
this term** — use the grader to see exactly what's missing, fix it, and resubmit.

## Lab 1 (Document Interactions, 24 pts)
Put your answers in `lab1_answers.json`:
```json
{
  "q1_trusted_flows": ["10.11.12.100:PORT -> 10.11.12.102:502", "..."],
  "q2_new_interaction": {"what_i_did": "...", "flow": "A:port -> B:port"},
  "q3_adversary_changes": "how the AitM changes the interactions ...",
  "q4_long_windows": "why long snapshot windows matter ..."
}
```
```
python3 grader/grade_lab1.py lab1_answers.json
```

## Lab 2 (Wind Farm & DNP3, 24 pts)
Put your answers in `lab2_answers.json`:
```json
{
  "q1_trusted_flows": ["FARM_IP:port -> WTG_IP:20000", "..."],
  "q2_hmi_credentials": "user/pass",
  "q3_new_interaction": {"what_i_did": "...", "flow": "A:port -> B:port"},
  "q4_modbus_vs_dnp3": "at least three concrete differences ..."
}
```
```
python3 grader/grade_lab2.py lab2_answers.json
```

## MP 1 (100 pts)
Bundle your required files into `mp1.zip` (`check.json`, `break.json`,
`secure.json`, `facts.yml`, `fix.txt`, `navigator.json`, plus your detection
artifact), then:
```
python3 grader/grade_mp1.py mp1.zip
```

## How grading works
- **Deterministic, no LLM.** The graders print `PASS` / `----` per rubric item.
- Correctness answers are checked against **salted hashes** — the source reveals
  no answer key. Written questions are scored by **concept coverage** (the
  grader prints which concepts/categories it detected).
- The **same grader**, run by the instructor, produces your recorded score.
- The graders are reversible by design. If you'd rather reverse-engineer how one
  grades than take it at face value, that's a fair challenge in a security course.
