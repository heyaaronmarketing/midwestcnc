---
title: "Servo Drive vs. CNC Controller Faults: How to Distinguish"
slug: "servo-drive-vs-controller-fault"
pillar: "cnc-control-systems"
target_query: "cnc servo drive vs controller fault"
description: "Learn to distinguish CNC servo drive faults from controller faults using alarm codes, fault logs, and swap-test isolation methods."
author: "Ken — Midwest CNC Services"
date: "2026-11-19"
signal_signature: "alarm-isolation decision tree; fault-log isolation sequence; drive-side versus control-side; swap-test isolation; parameter backup before board swap"
---

## Key Takeaways

- Servo drive faults generate axis-specific alarms with current or voltage codes, while controller faults produce system-wide errors on multiple axes.
- The alarm-isolation decision tree asks one key question: does the fault follow the axis or follow the board slot when you swap parts.
- In our service log, 60-70% of "drive faults" trace to wiring, feedback cables, or encoder problems—not the drive itself.
- Fanuc drives report overcurrent with 400-series alarms, while Siemens SINAMICS uses F7xxx codes for hardware and F8xxx for communication.
- Always complete a parameter backup before board swap to avoid turning a quick test into a multi-day recovery.

A CNC servo alarm makes most shops suspect the drive first. The drive is visible. It runs warm. It has clear failure modes. But in our shop, controller-side issues cause nearly as many calls as drive failures. CPU faults, comm dropouts, and bad position data all mimic drive problems. Telling them apart saves both time and money. A $3,500 drive swap fixes nothing if a $200 fiber cable is the real culprit. This guide covers the fault-log isolation sequence we use to find drive-side versus control-side origin in the first hour.

## How Drives and Controllers Split the Work

A servo drive takes low-voltage commands and outputs high current to move the motor. The controller runs the program, handles axis math, and closes the position loop via encoder feedback. When something fails, symptoms point to which side broke.

Drive faults involve power. Overcurrent, overvoltage, regen overload, thermal shutdown—these show up as axis-specific alarms. They cite amperage, bus voltage, or heatsink temp. On a Fanuc system, Alarm 401 often appears with a drive-level code pointing to current. For details on that alarm, see [Fanuc Alarm 401: Causes and Recovery](/insights/cnc-control-systems/fanuc-alarm-401/).

Controller faults involve logic or data. A bad CPU board might error on all axes at once. A failing fiber ring (FSSB on Fanuc, DRIVE-CLiQ on Siemens) might show random dropouts. A corrupt position counter can cause runaway even with a healthy drive and motor.

Feedback sits in the overlap zone. Encoder faults can trip either side. On older systems where encoder signals route through the drive, a bad encoder faults the drive. On newer serial-feedback designs, the same failure may fault the controller instead.

## The Alarm-Isolation Decision Tree

We follow a set sequence to sort drive faults from controller faults. The alarm-isolation decision tree has five steps.

**Step 1: Read the alarm, then the sub-code.** Most controls report a main alarm plus a detail code. Fanuc stores these in DGNOS pages. Siemens logs them with timestamps. The sub-code often names the failing part.

**Step 2: Check if the fault is axis-specific or system-wide.** If only X faults while Y and Z work, look downstream—drive, motor, encoder, wiring on that axis. If all axes fault together at power-up, look upstream—controller, power supply, comm bus.

**Step 3: Review fault-log timestamps.** A capacitor failure trips at power-on. A thermal fault builds over 8-12 minutes. A comm dropout may happen randomly. The pattern tells you where to dig. Our fault-log isolation sequence starts here. We have seen thermal faults with the same 10-minute buildup each time. That points to airflow. Random faults without a heat link often mean noise or wiring.

**Step 4: Run swap-test isolation.** On machines with identical axes, swap drives between X and Y. If the fault moves with the drive, replace it. If the fault stays on X no matter what drive is there, the problem is wiring, motor, or encoder.

**Step 5: Check feedback cables.** A single broken shield can mimic drive failure. We carry a cable tester on every call. For more on what we bring, see [What We Bring on a Field Call](/insights/field-service-logistics/what-service-truck-carries/).

## Common Drive Faults and Their Signs

Servo drives fail in known ways. Match the symptom to the cause.

**Overcurrent faults** (Fanuc Alarm 401 with SV0401, Siemens F7900) mean the drive saw amps past safe limits. Causes: motor winding short, cable breakdown, failed output transistor. Test by meggering the motor. Healthy windings show at least 1 MΩ to ground. Below 100 kΩ is trouble.

**Bus voltage faults** (Fanuc Alarm 9 or 400-series, Siemens F7801/F7802) mean DC bus went out of range. Causes: supply problems, regen energy on fast decel, or aged caps. On Fanuc β-series drives from the 1990s, cap aging after 15-20 years is common.

**IPM or IGBT faults** mean the power module failed. The drive won't power up, or it faults with a hardware code. The fix is replacement or rebuild if the control board survived.

**Thermal faults** (Fanuc Alarm 404, Siemens F7805) mean the heatsink hit its limit. Check fans, filters, and ambient temp. A clogged filter can push temps from 45°C to 85°C.

On older Fanuc platforms, the drive-vs-control value split matters for repair decisions. See [Used Fanuc-Controlled Machines: Control vs. Iron Value](/insights/buying-owning-used-cnc/used-fanuc-machines-control-vs-iron/).

## Common Controller Faults and Their Signs

Controller faults cost more and hide better. Spot them early.

**Comm faults** (Fanuc Alarm 8 with FSSB errors, Siemens F8xxx) mean the serial link dropped. Causes: failing fiber cable, dirty optical port, or bad interface board. Plastic fiber yellows with age. Light loss rises until the link flakes out.

**Position data errors** mean feedback reaching the CPU is bad. Causes: failing interface board, noise on serial lines, or dead encoder battery. On Okuma OSP controls, battery voltage matters. See [Used Okuma: OSP Era and Resale](/insights/buying-owning-used-cnc/used-okuma-osp-era-impact/).

**CPU board faults** show as many unrelated alarms, hangs, or display glitches. On Fanuc 16/18 controls, a dying lithium cell can corrupt SRAM. Symptoms look like drive trouble but vanish when you reload the backup.

**Supply faults** in the cabinet hit everything downstream. A weak 24V rail can brown out interface boards. That shows up as drive comm errors.

## Field Sequence We Use

Here is how we work a servo-fault call.

1. **Log all alarms before clearing.** Write down main codes, sub-codes, and axis tags. Photograph the screens.

2. **Read the fault buffer.** The last 20 entries often show a pattern one snapshot misses.

3. **Power cycle and watch.** A fault at power-on points to hardware. A fault after homing, motion, or heat points elsewhere.

4. **Isolate the axis.** Unplug the motor from the suspect drive. If the fault clears, check motor or wiring. If it stays, the drive may be bad.

5. **Swap-test isolation.** Move drives between axes. See if the fault follows.

6. **Parameter backup before board swap.** This step is non-negotiable. Skipping it can turn a quick test into days of recovery.

7. **Check simple things.** Loose plugs, dirty fan filters, and corroded terminals cause many faults. We have cleared Alarm 401 by tightening one encoder connector.

For Mazak turning centers with older controls, adapt to the platform. See [Mazak Turning Legacy Repair](/repairs/mazak-cnc-machine-repair/turning-legacy/).

## When Both Sides Are Involved

Sometimes the fault spans both drive and controller. A failing drive can send noise back into the control, tripping healthy axes. A comm dropout can leave the drive undefined, damaging outputs. When signs point both ways, fix the clear failure first—swap the bad drive—then verify controller health.

Spindle drives add layers. They talk to the spindle motor, orient system, and bearings. A bad spindle can overload a good drive. For spindle diagnosis, see [Fanuc Spindle Repair](/spindle-grinding/fanuc-spindle-repair/) or the legacy notes at [Spindle Service on Fanuc Series 0 / 0M](/spindle-grinding/fanuc-spindle-repair/series-0-legacy/).

## Sources & References

- Fanuc Series 30i/31i/32i Maintenance Manual (B-64485EN), alarm tables and diagnostics
- Siemens SINAMICS S120 Faults and Alarms manual, F7xxx and F8xxx codes
- Internal service log data, 2019-2024 bench and field repairs
- Our [CNC Control Systems](/insights/cnc-control-systems/) pillar for related coverage

## When to Bring This Work to Us

If you have pinned the fault to the drive, we rebuild most Fanuc, Siemens, and Mitsubishi units on our bench with 5-7 day turn. If the fault keeps moving or you cannot decide drive-side versus control-side, our field techs carry test gear and swap parts to find it on-site. We handle the electronics and any mechanical issues stressing the system.

For a quote, [submit details through our form](/get-a-quote/) with your machine model, control type, and alarm codes. Screen photos help us stage the right parts.