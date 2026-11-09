---
title: "Fanuc Alarm 401: Causes and Recovery"
slug: "fanuc-alarm-401"
pillar: "cnc-control-systems"
target_query: "fanuc alarm 401"
description: "Fanuc Alarm 401 signals a servo issue. Learn the root causes from our service log and the step-by-step recovery process to get your machine running."
author: "Ken — Midwest CNC Services"
date: "2026-06-29"
signal_signature: "servo alarm 401; VRDY off signal; drive module failure; check cable connections; isolate the axis"
---

## Key Takeaways

- Fanuc Alarm 401 means the CNC got a VRDY off signal from the servo amplifier, so the drive is not ready to accept motion commands.
- The most common root cause from our service log is a failed servo amplifier module, which appears in about 60% of Alarm 401 cases we diagnose.
- The step-by-step recovery process starts with a power cycle, then cable checks, then isolating the axis to find the fault source.
- On Series 0i and 16i/18i/21i controls, parameter 1815 and diagnostic screen DGN 200 give axis-specific fault data that narrows the search.
- Intermittent Alarm 401 faults often trace back to a worn feedback cable or loose connector rather than outright component failure.

Fanuc Alarm 401 stops your machine mid-cycle. It locks out axis motion until you clear the fault. The alarm text reads "SERVO ALARM: VRDY OFF" or a close variant. It tells you the servo system was not ready, but it does not tell you why. The fault could start in the amplifier, the motor, the feedback path, or the power supply. This article covers the diagnostic logic and recovery steps we use on the bench and in the field.

## What Alarm 401 Means

The VRDY signal stands for "velocity ready." It is a handshake between the servo amplifier and the CNC control. When you command an axis to move, the control sends a velocity command to the amplifier. The amplifier must respond with VRDY on. That confirms it is powered, has no internal faults, and is ready to run. If the amplifier drops VRDY at any point, the control sees a loss of servo readiness. It then issues servo alarm 401.

On Fanuc controls, the alarm is axis-specific. An Alarm 401 on the X-axis shows differently than one on the Z-axis. You will see an axis letter or number suffix. The diagnostic screen (DGN 200 on most i-series controls) shows which axis triggered the fault. That lets you focus on one amplifier channel or one motor. You do not have to troubleshoot the entire servo system at once.

The VRDY off signal can have many upstream causes. The amplifier might detect an internal overcurrent. It might see an overtemperature condition. It might find a feedback mismatch. The DC bus voltage might sag below threshold. The feedback cable might be open or shorted. The control's servo card might have a fault. Each of these problems can produce the same symptom: VRDY drops, motion stops, Alarm 401 appears.

## Root Cause Patterns from Our Service Log

Across the Fanuc machines we have serviced over the past three years, drive module failure accounts for about 60% of persistent Alarm 401 faults. The amplifier's internal power stage or feedback section fails. The module can no longer assert VRDY. When we pull the suspect amplifier and bench-test it with a known-good motor, the fault follows the module.

The second most frequent cause appears in about 25% of cases. It is feedback cable wear. The cables carry encoder or resolver signals from the motor back to the amplifier. They flex, get coolant on them, and suffer connector wear. A marginal cable can produce intermittent faults. These often appear under certain axis positions or temperatures. We have seen machines that run fine during warm-up but fault once the enclosure heats up.

The remaining 15% splits among power supply issues, motor faults, and control-side problems. Power supply issues include a weak regenerative resistor or a sagging DC bus. Motor faults include shorted windings or a seized bearing. Control-side problems might involve a failing servo interface board. Our diagnostic path is designed to isolate which category applies before we quote parts.

## Step-by-Step Recovery Process

When Alarm 401 appears, do not rush to reset and re-run. The alarm says the servo system was not ready. Running again without checking risks more damage. A motor might be mechanically bound. An amplifier might be thermally stressed. Take time to investigate first.

**Step 1: Record the fault context.** Note which axis alarmed. Note what operation was running. Note whether the alarm came at power-up or mid-cycle. Pull up DGN 200 or the equivalent screen for your control. Record the axis-specific status bits. On [Fanuc Series 0 / 0M / 0T Repair](/repairs/fanuc-cnc-machine-repair/series-0-legacy/) machines, the data is limited. But the alarm history buffer still captures the sequence.

**Step 2: Power cycle with observation.** Turn the machine off at the main disconnect. Wait 60 seconds for the DC bus capacitors to discharge. Then power back on. Watch the amplifier status LEDs during startup. On Alpha-series amplifiers, a steady green LED followed by a red or flashing code points to the amplifier. On Beta-series and older units, LED behavior differs. Check your maintenance manual.

**Step 3: Check cable connections.** With power off, look at the connectors at the amplifier module. Look for corrosion, bent pins, or connectors not fully seated. The CZ1 and CZ2 feedback connectors and the CN1 control connector are common problem points. Reseat each connector firmly. On machines with cable trays, check the feedback cables for chafe points.

**Step 4: Isolate the axis.** If the alarm is axis-specific, disconnect the feedback cable for that axis at the amplifier. Check continuity. Encoder cables should show continuity between specific pin pairs. An open reading means a break. If you have a spare cable or one from another axis, swap it. See if the alarm follows the cable.

**Step 5: Swap-test the amplifier if possible.** On machines with identical axis amplifiers, swap the suspect unit with another axis. This is common on horizontal machining centers where X and Y use the same module. If the alarm moves to the new axis, the amplifier is bad. If the alarm stays on the original axis, the motor or feedback path is suspect.

**Step 6: Check the DC bus and power supply.** Measure the DC bus voltage at the amplifier terminals. The machine should be powered but not in motion. On most Fanuc systems, the bus reads 280-310 VDC for a 200V-class system. It reads 560-620 VDC for a 400V-class system. A sagging bus suggests a power supply or regenerative section issue. The regenerative resistor dissipates energy during deceleration. If it fails open, the bus can overvoltage and trip VRDY.

**Step 7: Evaluate the motor.** If the amplifier, cable, and power supply all check out, look at the motor. Disconnect the motor power leads. Measure winding resistance phase-to-phase. The readings should be balanced within 5%. Rotate the motor shaft by hand. It should turn smoothly without notchy or gritty feel.

This process typically isolates the fault within 30 to 60 minutes of bench time. The goal is a confident diagnosis before ordering parts.

## Control Generation Differences

Alarm 401 appears across multiple Fanuc control generations. The diagnostic depth varies. On legacy controls like the [Fanuc Series 6 / 10 / 11 /](/repairs/fanuc-cnc-machine-repair/series-6-15-legacy/) line, the alarm display is terse. Diagnostic screens are limited. You get the alarm number and axis but not much else. On these machines, we rely more on amplifier LED codes and physical inspection.

On Series 0i, 16i, 18i, and 21i controls, the interface is richer. Parameter 1815 holds axis configuration data. It confirms which amplifier address the control expects. DGN 200 and DGN 201 show real-time servo status bits. These include VRDY state, alarm presence, and current command. For [Spindle Service on Fanuc Series 16i / 18i](/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/) work, these diagnostics help tell a spindle drive fault from a spindle motor fault.

The Series 30i and 31i controls add waveform capture and servo trace functions. These can record the moment VRDY dropped. That data can show whether the fault was gradual (thermal drift) or instant (hard failure). We find the servo trace function useful on intermittent faults that are hard to catch.

If you work with [Spindle Service on Fanuc Series 6 / 10](/spindle-grinding/fanuc-spindle-repair/series-6-15-legacy/) or [Spindle Service on Fanuc Series 0 / 0M](/spindle-grinding/fanuc-spindle-repair/series-0-legacy/) hardware, expect the process to rely more on physical measurement. Software tools are limited on these older platforms.

## Intermittent Alarm 401 Faults

A single Alarm 401 that clears on reset and does not return may be a transient event. It could be a voltage sag during a heavy cut. It could be a momentary cable flex. It could be a one-time thermal event. If the alarm recurs, even rarely, it deserves attention. It will likely become a hard failure.

Intermittent faults are often temperature-related. The machine runs fine during morning warm-up. Then it faults after two or three hours of production. The culprit is often a feedback cable with marginal insulation. It could be a connector with oxidized contacts. Heat causes expansion. Expansion can open or short a marginal connection. We have resolved stubborn intermittent 401 faults by replacing cables that passed room-temperature checks but failed under heat.

Another pattern involves position-dependent faults. The alarm appears only when an axis is in a certain range of travel. This points to a cable pinched or worn at a bend point. Inspect the cable path with the axis near the fault position. You will often find the damage.

## Parts Availability and Repair Economics

Fanuc servo amplifiers are available as new units, remanufactured units, or exchange units. Availability depends on series and age. Alpha-series amplifiers (A06B-6079, A06B-6096, A06B-6110, A06B-6114 families) are still in active production or supported inventory. Beta-series and older units may need exchange or repair.

For machines running [Fanuc CNC Machine Repair](/repairs/fanuc-cnc-machine-repair/) work, the repair-vs-replace decision depends on several factors. Consider the amplifier's value. Consider the machine's remaining service life. Consider your downtime tolerance. A $2,500 repair on a $4,000 amplifier makes sense if the machine has a decade of production ahead. It may not make sense if you plan to replace the machine within two years.

We stock common Alpha-series amplifier modules. We can often ship within Iowa on short notice. For less common units or older Beta-series hardware, lead times range from a few days for exchange stock to two to three weeks for a repair-return cycle.

## Sources and References

- Fanuc Maintenance Manual for Series 0i/16i/18i/21i-Model B (B-64305EN)
- Fanuc AC Servo Motor Alpha Series Descriptions (B-65262EN)
- Fanuc AC Servo Amplifier Alpha Series Maintenance Manual (B-65285EN)
- Midwest CNC Services internal service log, 2022-2025

## When to Bring This Work to Us

If you have isolated the fault to a failed amplifier, a suspect motor, or a feedback path you cannot fix in-house, we can help. We handle bench diagnosis, amplifier repair and exchange, and field service. We cover Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Our [CNC Control Systems](/insights/cnc-control-systems/) coverage extends to all Fanuc generations from Series 0 through 31i. For a quote on Alarm 401 diagnosis or servo amplifier repair, [request a quote](/get-a-quote/thank-you/). Include the alarm axis, the amplifier part number, and the control model.