# Detection — starter kit (MP1 defense requirement)

This folder supports the **defense half** of Module 4 / MP1. The attack lab shows how an
adversary-in-the-middle can rewrite Modbus responses so the operator's HMI lies while the
turbine runs normally. For MP1 you must also produce **one detection artifact** that would
*catch* a step in your attack chain, and map each remediation to a recognized OT standard.

This is a **starter** — extend it with your own rule/threshold for your chosen chain.

## Three places to detect the Module 4 attack

1. **ARP anomaly (Layer 2).** The AitM relies on `arpspoof`, which produces conflicting
   ARP replies (two MACs claiming one IP). This is the most reliable network signal.
2. **Modbus integrity (Layer 7).** Function-code-4 read responses suddenly returning
   all-zero registers for a sensor that was live is anomalous.
3. **Ground-truth delta (process layer).** The ot-sim ground-truth module publishes the
   real values to the message bus (what Grafana reads). An alert on
   `abs(hmi_value - ground_truth_value) > threshold` catches the lie regardless of how it
   was injected — the strongest OT detection.

## Starter Suricata rule — ARP spoofing (edit for your addresses)

```
# Fires when an ARP reply maps a protected IP to an unexpected MAC.
# Replace <ANEMOMETER_MAC> / <CONTROLLER_MAC> with the real ones from your capture.
alert arp any any -> any any (msg:"OT AitM: unexpected MAC for 10.11.12.102 (anemometer)"; \
  arp.opcode:2; arp.spa:10.11.12.102; arp.sha:!<ANEMOMETER_MAC>; sid:1000001; rev:1;)
alert arp any any -> any any (msg:"OT AitM: unexpected MAC for 10.11.12.100 (controller)"; \
  arp.opcode:2; arp.spa:10.11.12.100; arp.sha:!<CONTROLLER_MAC>; sid:1000002; rev:1;)
```

## Starter ground-truth delta check (pseudocode)

```python
# Compare the value on the operator path (Modbus/HMI) against the ground-truth bus.
# Real values come from the ground-truth module (OpenSearch/Grafana); HMI value from Modbus.
THRESHOLD = 1.0  # tune per signal
if abs(hmi_wind_speed - ground_truth_wind_speed) > THRESHOLD:
    alert("Integrity: HMI wind speed disagrees with ground truth — possible AitM")
```

## Standards mapping (use in your `fix.txt`)

Map each remediation to one control, e.g.:

- **Network segmentation / zones & conduits** → IEC 62443-3-3 SR 5.1; NIST SP 800-82r3 (network architecture / segmentation).
- **Detect & alert on anomalies** → NIST SP 800-82r3 (monitoring); IEC 62443-3-3 SR 6.2 (continuous monitoring).
- **Integrity / authenticity of comms** → IEC 62443-3-3 SR 3.1 (communication integrity).

## What to submit for MP1

- Your detection artifact (a rule file, a threshold script, or a documented alert), plus a
  short paragraph on what it fires on and its false-positive tradeoffs.
- Each remediation in `fix.txt` mapped to one NIST SP 800-82 or IEC 62443 control.
