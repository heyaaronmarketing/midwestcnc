---
title: "Pre-Call Diagnostic: Questions That Save You Money"
slug: "pre-call-diagnostic-questions"
pillar: "field-service-logistics"
target_query: "cnc service call preparation"
description: "Use our 7-question intake process before your CNC service call. Each question rules out failure modes and cuts diagnostic time on-site."
author: "Ken — Midwest CNC Services"
date: "2026-11-08"
signal_signature: "7-question intake; what each question rules out; fault codes and alarm history; spindle warm-up behavior; intermittent versus consistent"
---

## Key Takeaways

- The 7-question intake we use before dispatch cuts on-site diagnostic time by 30 to 45 minutes on a typical call.
- Knowing whether a fault is intermittent versus consistent changes which test gear we load—wrong gear means a return trip at your cost.
- Spindle warm-up behavior alone can rule out thermal drift, bearing preload loss, or encoder issues before we arrive.
- Fault codes and alarm history from the last 48 hours give us a timeline that points toward electrical, mechanical, or software root causes.
- Shops that document the sequence of events before failure reduce their average diagnostic bill by one to two labor hours.

A service call starts before the truck leaves Waterloo. The 15 minutes after a machine faults shape the entire job. Good info means we arrive with the right parts and a working theory. Poor info means we spend your money figuring out what you could have told us. This is not about making your life harder. It is about making the call shorter. Every question in our intake exists because it rules something out.

## The 7-Question Intake: What We Ask and Why

When you call or submit through our [CNC Machine Repair Services](/repairs/) form, we walk through seven questions. This 7-question intake shapes how we prepare. Each question has a clear diagnostic purpose.

**Question 1: What is the machine make, model, and control?**

A Mazak VTC-200C with a Mazatrol Fusion 640M has different board layouts than a Haas VF-2 with a Classic Control. The [Haas Classic Control Repair (pre-NGC)](/repairs/haas-cnc-machine-repair/haas-classic-control/) page shows why pre-NGC machines have specific power supply failure patterns that NGC machines do not share. "It's a Haas vertical" leaves us guessing.

What each question rules out: The exact control version lets us skip entire categories of known issues. Fanuc 0i-TD controls differ from 0i-TF. Mazatrol Matrix differs from Matrix 2 for servo tuning. The answer changes what we bring.

**Question 2: What fault codes and alarm history are you seeing?**

Pull the alarm history screen. Most controls show the last 20 to 100 alarms with timestamps. We want alarm numbers, sequence, and time window. One alarm is useful. The pattern over 48 hours is diagnostic.

An SV0401 servo alarm on Fanuc could be a motor, drive, cable, or feedback device. But if SV0401 appears after thermal alarms on the spindle amp, the path narrows. On Mazak machines with Mitsubishi drives, an AL-20 after 2+ hours of run time points toward heat rather than wiring.

What this rules out: Fault codes and alarm history eliminate shotgun work. No thermal alarms before an axis fault? We skip cooling systems. Servo alarms tied to specific tool positions? We check interference or cable routing first.

**Question 3: Is the fault intermittent versus consistent?**

Most shops skip this detail. A machine that faults every time on a specific cut is a different path than a machine that faults randomly over three shifts.

Consistent faults point to hard failures: dead parts, broken wires, mechanical binds. Intermittent faults point to thermal growth, marginal connections, or EMI. Test gear differs. For intermittent electrical faults, we bring data loggers and thermal cameras. For consistent mechanical faults, we bring dial indicators and laser gear.

What this rules out: Intermittent versus consistent tells us if we are chasing a part or chasing a condition. "It faults randomly" means longer diagnostics and monitoring gear that can capture events over time.

**Question 4: What was the machine doing when the fault occurred?**

"It just stopped" is not helpful. "It faulted during a roughing pass in O1234, tool 7, at Z-2.500" is very helpful.

We want: What operation? What tooling? What material? What feeds and speeds? Was the spindle under load? Was the axis in rapid or feed mode? Was coolant on?

A spindle fault during heavy cuts points toward bearing load or heat. The same alarm during an air cut points toward encoder or drive issues. Our [Spindle Diagnostics & Repair Decisions](/insights/spindle-diagnostics/) pillar covers how context shapes the rebuild decision.

What this rules out: Operation context rules out load-related versus idle-state failures. A servo alarm during rapids differs from a servo alarm during threading. Knowing the operation points us toward specific subsystems.

**Question 5: What is the spindle warm-up behavior?**

For spindle issues, this question is gold. Before the fault started, what did the spindle do at warm-up? Did runout increase after sitting overnight? Did noise change after 20 minutes? Did speed vary under load?

Spindle warm-up behavior tells us about preload, lubrication, and encoder health. A spindle that runs rough cold but smooths after 15 minutes suggests lube or preload issues. One that starts smooth and degrades under load suggests bearing failure.

For [Spindle Service on Haas Classic Control (Pre-NGC)](/spindle-grinding/haas-spindle-repair/haas-classic-control/) machines, belt-driven spindles show different warm-up patterns than direct-drive units. We prepare based on your description.

What this rules out: Warm-up data rules out thermal calibration issues versus real mechanical wear. It tells us if we are looking at a parameter tweak or a rebuild.

**Question 6: Have you made any recent changes?**

This covers: software updates, parameter edits, tooling swaps, fixture swaps, coolant changes, building electrical work, new nearby equipment, or maintenance like way lube changes.

Shops sometimes feel awkward here. That is not the point. We are not blaming anyone. We are cutting variables. New coolant last week plus thermal alarms this week? Data point. New welder on the same circuit plus servo faults? Data point.

What this rules out: Recent changes rule out correlation causes. A machine that ran fine for two years and faulted after a parameter restore is different from one with slow decay.

**Question 7: What is the machine's production role?**

This is logistics, not sales. A machine costing $5,000 per shift in lost output gets different dispatch than a backup with spare capacity.

We dispatch from Waterloo, Iowa, across seven states. [Field Service & Logistics (Midwest)](/insights/field-service-logistics/) coverage means some calls are rapid and some are scheduled. Knowing urgency helps us plan. A four-day window means we can ship parts ahead, cutting wait time on-site.

What this rules out: Criticality helps us choose air freight versus ground for a replacement drive. A primary machine may justify that cost. A secondary machine may not.

## What Your Answers Change About Our Prep

The 7-question intake shapes what we load and what theory we walk in with.

Example 1: Your answers show a Doosan Puma 2600SY with consistent spindle alarms during heavy turning, warm-up roughness growing over 30 minutes, no recent changes. We load spindle diagnostic gear, common replacement bearings for that platform, and prepare for on-site bearing work or a ship-to-bench recommendation.

Example 2: Your answers show a Haas VF-3 with intermittent X-axis faults, no pattern, and a recent building electrical upgrade. We load data loggers, power quality analyzers, and cable test gear. We prepare for electrical work, not mechanical.

The loadout gap is real. Mechanical tools to an electrical problem wastes time. Electrical gear to a spindle bearing failure wastes time. The intake is how we dodge those mismatches.

## Gaps That Cost Money

In 30 years of field calls, certain patterns repeat. These are the common gaps:

**Gap 1: "It just started doing this."** The alarm history shows intermittent faults going back weeks. The machine gave warnings. Shops got busy. Earlier data would have helped.

**Gap 2: "We didn't change anything."** A parameter restore happened three days before the fault. Or a tech topped off way lube with the wrong viscosity. Small changes often correlate.

**Gap 3: "The spindle sounds fine to me."** Floor noise masks spindle wear. A 30-second listen with a stethoscope during warm-up catches problems before hard-stop alarms.

**Gap 4: "I don't have the alarm numbers."** We spend 20 minutes at the control pulling what you could pull in 2 minutes. That is your labor cost, not ours.

These are not character flaws. They are patterns across hundreds of calls per year. The intake surfaces this info before we are on your clock.

## What to Have Ready Before You Call

Based on what each question rules out, gather this before you reach out through [Technical Insights](/insights/) or our quote form:

1. Nameplate data: make, model, serial, control type, software version.
2. Screenshots or photos of the alarm screen and history. USB export is even better.
3. A written timeline: when the fault first appeared, when it became steady, what the machine was doing each time.
4. A description of spindle warm-up behavior, if spindle-related.
5. A list of any changes in the past 30 days: maintenance, software, tooling, fixtures, electrical, nearby gear.
6. Your schedule: how critical is this machine, how much flexibility do you have.

This prep takes 15 to 20 minutes. It often saves 1 to 2 hours of on-site time. At field rates, the math favors you.

## Sources & References

- Service call logs from Midwest CNC Services field operations, 2020-2025.
- Fanuc alarm code docs for 0i-TD and 0i-TF controls.
- Haas guides for Classic Control (pre-NGC) and NGC platforms.
- Mazak bulletins for Fusion 640M and Matrix control families.
- Dispatch and parts data from our Waterloo, Iowa base.

## When to Bring This Work to Us

If your machine is down and you have the info above, you are ready. Shops that prep fault codes and alarm history, note spindle warm-up behavior, and flag intermittent versus consistent faults get faster, cheaper repairs. That is arithmetic, not pitch.

Learn more [About Midwest CNC Services | Waterloo, Iowa](/about/) and our work across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. When ready, [request a quote](/get-a-quote/) and include the docs you gathered. We will arrive prepared.