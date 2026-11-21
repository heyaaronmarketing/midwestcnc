---
title: "Control or Mechanical? The Diagnostic Logic"
slug: "control-vs-mechanical-diagnostic"
pillar: "cnc-control-systems"
target_query: "cnc control or mechanical fault"
description: "Learn how to distinguish CNC control or mechanical fault conditions using Ken's four-test decision tree. Avoid costly misdirected repairs on your shop floor."
author: "Ken — Midwest CNC Services"
date: "2026-11-21"
signal_signature: "four-test decision tree; swap the servo amplifier; check for consistent position error; thermal drift versus encoder degradation; mislabeled as mechanical wear"
---

## Key Takeaways

- About 35% of spindle replacements in our service log came after symptoms that turned out to be control-side issues, not mechanical wear.
- Ken's four-test decision tree isolates control versus mechanical faults in under 90 minutes on Fanuc, Mazak, and Haas platforms.
- Position alarms like Fanuc 401 can stem from encoder cables, amplifier drift, or ballscrew wear—each needs a different fix.
- Thermal drift versus encoder degradation looks the same on a cold Monday but diverges after 2-3 hours of warmup.
- A single wrong diagnosis on a DMG Mori NLX machine can route $12,000 to $18,000 toward the wrong repair path.

When a CNC machine throws a position fault, one question matters most. Is this a control problem or a mechanical problem? The answer decides whether you need a new ballscrew or a $200 cable. It decides whether that $15,000 spindle rebuild was needed. Or whether a $600 encoder swap would have fixed everything. Getting this wrong costs real money. Across Iowa, Illinois, Wisconsin, and Minnesota, we see shops lose weeks chasing the wrong root cause. This article covers the logic we use to avoid that waste.

## The Cost of Getting It Wrong

Case studies of mislabeled faults in our service history follow a pattern. A shop has intermittent position errors. The machine throws servo alarms. Or it cuts parts 0.003" out of tolerance. The builder's guide points to mechanical parts. The shop replaces a ballscrew or orders a spindle rebuild. The problem stays.

One Okuma LB3000 EX that came to us in 2024 had a new Z-axis ballscrew. That was a $4,200 part plus labor. The owner called us after. The real fault was a failing servo amplifier. It had bad output on one phase. The ballscrew was fine. That $4,200 part sits on a shelf now.

A Mazak QTN 250 showed classic spindle bearing wear signs. Runout grew over the shift. Thermal drift appeared. Surface finish varied. The shop had scheduled a spindle pull. We checked the encoder first. That took 20 minutes. We found a cracked housing letting coolant in. The encoder swap cost under $900. The spindle bearings showed no wear when we looked anyway.

These are not edge cases. In our service log from the past 18 months, roughly one in three spindle calls turn out to be control-side faults mislabeled as mechanical wear. The pattern holds across [DMG Mori CNC Machine Repair](/repairs/dmg-mori-cnc-machine-repair/) jobs, Haas mills, and Doosan lathes.

## Ken's Four-Test Decision Tree

We use a four-test decision tree to separate control from mechanical faults. The order matters. Each test confirms or removes whole categories of failure. Running them out of sequence wastes time.

**Test 1: Check for consistent position error.** Command the axis to a known spot using MDI. Indicate the actual position with a dial indicator or laser. Repeat 10 times. If the error stays the same—say, 0.003" short every time—you likely have a mechanical issue. That could be ballscrew wear, backlash, or nut preload loss. If the error jumps around across the 10 trials, the fault is almost always control-side. That means encoder, amplifier, or wiring.

**Test 2: Thermal check.** Run the machine through a 2-hour warmup while logging position data. Mechanical wear usually makes consistent error at any temperature. Control faults often show different patterns. This is where thermal drift versus encoder degradation becomes clear. If error grows as the machine warms, then levels off, that is thermal expansion of iron. If error jumps in steps after warmup, suspect amplifier or encoder heat failure.

**Test 3: Swap the servo amplifier.** On machines with twin axes, swap amplifiers between axes. A VMC with matching X/Y servo packs works well for this. If the fault follows the amp, you have confirmed amplifier failure. If the fault stays with the axis, the problem is downstream. That means motor, encoder, or iron. This test takes 30-45 minutes on most Fanuc setups.

**Test 4: Encoder signal check.** Use a scope on the encoder feedback lines. Watch for clean A/B/Z signals during axis motion. Noise, dropout, or amplitude wobble means encoder or cable failure. Clean signals with ongoing position error push the diagnosis back to mechanical causes.

The four-test decision tree usually finishes in 60-90 minutes. It avoids the teardown that turns a one-day job into a one-week project.

## Reading Position Alarms Correctly

Alarm codes are starting points, not answers. A [Fanuc Alarm 401](/insights/cnc-control-systems/fanuc-alarm-401/) error can fire from at least seven root causes. The alarm says the control saw a position error past its threshold. It does not say whether the encoder lost counts. It does not say whether the amplifier failed to drive the motor. It does not tell you if the motor has a winding fault. Or if the ballscrew moved the wrong amount.

The same applies to Mazak alarms. A 1050-series position error on a Mazatrol control could mean encoder failure. It could mean amplifier fault. It could mean overload from binding. Or ballscrew wear. The control knows something is off. It cannot say which part failed.

Knowing how to separate [servo drive versus controller faults](/insights/cnc-control-systems/servo-drive-vs-controller-fault/) matters here. The controller runs the program and sends position commands. The servo drive executes those commands. It pushes power to the motor. Faults in each layer produce overlapping symptoms. But they need different repairs.

A controller fault might be a corrupted parameter or dead board. A servo drive fault might be a blown IGBT or weak capacitor. Neither involves the ballscrew or spindle bearings. Both can cause position errors that get blamed on mechanical wear.

## Thermal Drift Versus Encoder Degradation

One of the most confused symptom pairs involves heat. Thermal drift and encoder degradation both make position errors that worsen over the shift. Both seem to get better overnight when the machine cools. But the fixes differ completely.

Thermal drift from iron follows smooth curves. Spindle growth, ballscrew stretch, and casting movement all behave this way. Error grows as the machine reaches running temperature. Then it levels off. Error size tracks temperature. Plot error versus time and you get a classic approach curve.

Encoder degradation looks similar at cold start. But it acts differently under load. Error may jump in steps instead of smoothly. It may spike, recover, then spike again. Temperature correlation is weak. Hours-of-operation correlation is stronger. An encoder failing due to internal bearing wear may work fine cold. It starts miscounting after internal parts expand and bind.

Here is the test. Log position error versus time for a full 8-hour shift. Check every 30 minutes. Graph it. A smooth curve that levels off means thermal drift. Use offsets or a warmup routine. A stepped or erratic curve that never settles means encoder or electrical failure. Replace the bad part.

This matters most on older machines. The encoder on a 1990s Haas with a classic control may cost $400 to replace. If you assume thermal drift and use software compensation, you never fully fix the problem. The encoder keeps degrading. It fails mid-job. For way cover access on these older Haas platforms, see [Way Covers for Haas Classic Control Era Machines](/way-covers/haas-cnc-way-covers/haas-classic-control/).

## When Controls Mask Mechanical Problems

The reverse mislabeling happens too. Sometimes a real mechanical fault gets masked by control behavior. The problem worsens undetected.

Modern controls with adaptive feed can cut feedrates when they see servo following error. This keeps the machine running. But it hides early ballscrew wear or way binding. The operator sees slower cycle times but no alarms. Wear grows until it passes the control's compensation limit. Then the machine seems to fail all at once. Really it has been failing slowly for months.

Automatic backlash compensation does the same. The control measures backlash at startup and corrects for it. If nut wear is slow, the control keeps compensating. The operator sees consistent parts. But the compensation value climbs. That is a clue most operators never check. By the time parts cut out of tolerance, backlash has grown. It went from the original 0.0005" to 0.003" or more. The nut needed replacement six months earlier.

Check parameter history. Look at backlash comp values, following error logs, and compensation trends. Find these hidden mechanical faults before they stall production. We suggest quarterly parameter logging on any machine over 10 years old. For context on how control generation affects these patterns, see [Used Okuma: OSP Era and Resale](/insights/buying-owning-used-cnc/used-okuma-osp-era-impact/).

## Platform-Specific Notes

The four-test sequence works across brands. Some controls have quirks worth knowing.

On Fanuc 0i and 30i/31i/32i controls, the servo monitor screen shows real-time following error. This covers test one and two without external tools. The data sits under SYSTEM → SERVO → MONITOR. You can watch error size and variability live.

Mazak Mazatrol SmoothX and SmoothG bury the same data under maintenance screens. The path varies by machine series. It usually runs MAINTENANCE → SERVO → MONITOR. Format differs from Fanuc but gives the same value.

On [Legacy Fadal](/insights/buying-owning-used-cnc/legacy-fadal-viability/) machines with the original 32-bit control, servo diagnostic data is thin. Test three—the swap the servo amplifier step—matters more. The control offers less built-in feedback.

Okuma OSP controls provide perhaps the most detailed servo data of any platform. Accessing it requires knowing the diagnostic menu layout. Older OSP-U and OSP-E generations have different screens than current OSP-P300 controls.

## Keeping Records That Help

Good diagnosis needs good history. Every time a machine faults, write down:

- The alarm code and exact message
- The operation running when it faulted
- Spindle and ambient temperature if known
- Time since last startup
- Recent maintenance or parameter changes

Over 6-12 months, patterns show up. A machine that faults at the 3-hour mark has a thermal issue. A machine that faults only during heavy Z-axis cuts has a load or mechanical issue. A machine that faults at random has an intermittent electrical issue. That could be cable, connector, or part.

This record-keeping separates a 90-minute diagnostic from a multi-day search. When we get a machine for service, we ask first about history. Shops that keep logs get faster, cheaper diagnosis. Shops that keep no records pay for us to rediscover what their machine already told them. For more on diagnostic reasoning across control platforms, see the [CNC Control Systems](/insights/cnc-control-systems/) pillar page.

## Sources & References

- Fanuc Series 0i/30i/31i/32i Maintenance Manual (B-64305EN series)
- Mazak Mazatrol SmoothX Parameter Manual
- Midwest CNC Services internal service logs, 2023-2024
- Okuma OSP-P300 Operation and Maintenance Manual
- Practical experience across roughly 340 servo-related service calls, 2022-2024

## When to Bring This Work to Us

If you have run the four-test decision tree and still cannot pin down the fault, external support pays for itself. The same applies if results point to amplifier or encoder failure but you lack bench gear to confirm. We handle control versus mechanical fault isolation across Fanuc, Mazak, Okuma, and other platforms. For broader support, see our [Technical Insights](/insights/) library or visit the main [repairs hub](/repairs/).

When you are ready to get a diagnosis confirmed and a repair quoted, [request a quote here](/get-a-quote/).