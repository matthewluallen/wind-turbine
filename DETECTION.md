# Detection — starter kit (MP1 defense requirement)

This folder supports the **defense half** of Module 4 / MP1. The attack lab shows how an
adversary-in-the-middle can rewrite Modbus responses so the operator's HMI lies while the
turbine runs normally. For MP1 you must also produce **one detection artifact** that would
*catch* a step in your attack chain, and map each remediation to a recognized OT standard.

This is a **starter** — extend it with your own rule/threshold for your chosen chain.

## Three places to detect the Module 4 attack

1. **ARP anomaly (Layer 2).** The AitM relies on `arpspoof`, which produces conflicting
   ARP replies (two MACs claiming one IP). This is the most reliable *network* signal.
2. **Modbus integrity (Layer 7).** Function-code-4 read responses suddenly returning
   all-zero registers for a sensor that was live is anomalous.
3. **Ground-truth delta (process layer).** The ot-sim ground-truth module publishes the
   real values to the message bus (what Grafana reads). An alert on
   `abs(hmi_value - ground_truth_value) > threshold` catches the lie regardless of how it
   was injected — the strongest OT detection.

Below are two **working** starter artifacts: one for Layer 2 (arpwatch) and one for the
process layer (a ground-truth delta script). Submit one (extended for your chain) for MP1.

## Starter detection A — ARP spoofing with `arpwatch` (Layer 2)

`arpwatch` watches ARP traffic on an interface and records the IP↔MAC bindings it sees.
When `arpspoof` points a protected IP at the attacker's MAC, the binding changes and
arpwatch logs it — that log line *is* the detection.

```bash
# install: apt-get install -y arpwatch     (Debian/Ubuntu)
# run on the interface that sees the OT segment (e.g. the sim bridge):
sudo arpwatch -i <iface> -f /tmp/arp.dat -N    # -N = don't background; logs to syslog/stderr
```

During the attack you'll see lines like:

```
changed ethernet address  10.11.12.102  <new attacker MAC>  (was <real anemometer MAC>)
flip flop                  10.11.12.102  <MAC A> <-> <MAC B>
```

`changed ethernet address` / `flip flop` for a protected IP (the anemometer at
`10.11.12.102`, the controller at `10.11.12.100`) is the arpspoof signature. Tune out
legitimate churn (DHCP, NIC swaps) before alerting.

> **Why not a Suricata rule here?** Stock Suricata does **not** ship ARP rule keywords —
> `arp` can't be used as a signature protocol and there are no `arp.*` keywords
> (confirmed on Suricata 8.0). Detect ARP spoofing with `arpwatch` (above) or a Zeek
> script, not a Suricata signature. If you want a Suricata artifact, target a layer it
> parses and write a rule + a short note on what it fires on.

## Starter detection B — ground-truth delta (process layer, recommended & runnable)

This is the strongest OT detection: compare the value on the **operator path** (the HMI,
read over Modbus) against the **ground truth** the ot-sim ground-truth module publishes to
OpenSearch (what Grafana shows). A sustained disagreement means someone is lying on the
operator path — it fires no matter how the lie was injected (network AitM, or data
tampering).

```python
#!/usr/bin/env python3
"""Ground-truth delta detector. Usage: detect_gtdelta.py hmi.csv ground_truth.csv
Each CSV: two columns  ts,value  (one reading per row)."""
import sys, csv

THRESHOLD = 1.0        # m/s; tune per signal
MIN_CONSECUTIVE = 3    # require a sustained divergence, not a one-sample blip

def load(p):
    out = {}
    with open(p) as f:
        for row in csv.reader(f):
            if not row or row[0].lower() in ("ts", "time", "timestamp"):
                continue
            out[row[0]] = float(row[1])
    return out

def main():
    if len(sys.argv) != 3:
        print("usage: detect_gtdelta.py hmi.csv ground_truth.csv"); sys.exit(2)
    hmi, gt = load(sys.argv[1]), load(sys.argv[2])
    run = 0; alerts = []
    for ts in sorted(set(hmi) & set(gt)):
        if abs(hmi[ts] - gt[ts]) > THRESHOLD:
            run += 1
            if run >= MIN_CONSECUTIVE:
                alerts.append((ts, hmi[ts], gt[ts]))
        else:
            run = 0
    if alerts:
        print(f"ALERT: HMI disagrees with ground truth on {len(alerts)} sample(s) "
              f"-- possible AitM / data-integrity attack")
        for ts, h, g in alerts[:5]:
            print(f"  ts={ts}  hmi={h}  ground_truth={g}  delta={abs(h-g):.2f}")
        sys.exit(1)
    print("OK: HMI tracks ground truth within threshold")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

Feed it the HMI series (from your Modbus capture / HMI export) and the ground-truth series
(from OpenSearch/Grafana) for the same window. It alerts only on a **sustained** gap
(`MIN_CONSECUTIVE` samples) so a single transient mismatch doesn't page anyone.

## Standards mapping (use in your `fix.txt`)

Map each remediation to one control, e.g.:

- **Network segmentation / zones & conduits** → IEC 62443-3-3 SR 5.1; NIST SP 800-82r3 (network architecture / segmentation).
- **Detect & alert on anomalies** → NIST SP 800-82r3 (monitoring); IEC 62443-3-3 SR 6.2 (continuous monitoring).
- **Integrity / authenticity of comms** → IEC 62443-3-3 SR 3.1 (communication integrity).

## What to submit for MP1

- Your detection artifact (the arpwatch config + a captured alert line, **or** the
  ground-truth delta script), plus a short paragraph on what it fires on and its
  false-positive tradeoffs.
- Each remediation in `fix.txt` mapped to one NIST SP 800-82 or IEC 62443 control.
