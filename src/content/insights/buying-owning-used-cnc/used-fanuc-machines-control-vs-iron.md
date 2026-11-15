---
title: "Used Fanuc-Controlled Machines: Control vs. Iron Value"
slug: "used-fanuc-machines-control-vs-iron"
pillar: "buying-owning-used-cnc"
target_query: "used fanuc cnc machine"
description: "Learn how control vintage drives total value when buying a used Fanuc CNC machine. Inspection tips, era pricing, and diagnostic routines from 30 years of field work."
author: "Ken — Midwest CNC Services"
date: "2026-11-15"
signal_signature: "how control vintage drives total value; Ken's diagnostic-on-purchase routine; Series 0i-D commands 15-25% premium; servo amp replacement runs $2,800 to $6,500; parameter backup battery state"
---

## Key Takeaways

- On a used Fanuc machine, how control vintage drives total value often matters more than the iron beneath it.
- Ken's diagnostic-on-purchase routine catches 80% of hidden electrical problems in under 45 minutes.
- A Fanuc Series 0i-D commands 15-25% premium over an 0i-B on the same iron due to parts support.
- Servo amp replacement runs $2,800 to $6,500 based on axis count and series generation.
- Machines running Fanuc 0M, 6M, or 10M controls are now in end-of-support territory where parts come from salvage only.

A shop lists a used Fanuc CNC machine for $45,000. What are you buying? The 1998 Mori Seiki SL-25 might show 22,000 spindle hours and a cracked way cover. Yet if it runs a Fanuc 18i-T in good shape, that control alone is worth $8,000 to $12,000 on the secondary market. Flip the scenario. A clean 2005 Mazak Quick Turn with a failing Fanuc 16i-T looks like a deal at $35,000. Then you price a control swap at $18,000 to $25,000. The iron and the control are separate value items. Knowing both is where due diligence pays off. This guide covers how to split that value when shopping for [Buying & Owning Used CNC](/insights/buying-owning-used-cnc/) equipment.

## The Control Sets the Value Floor

A Fanuc control is a computer bolted to a machine tool. The iron—ways, spindle, ballscrews, castings—wears over decades. The control ages in a different way. Components go obsolete. Firmware stops getting updates. Boards become salvage-only items.

A Hardinge lathe from 1992 with a Fanuc 0T might cut good parts today. When that main CPU board fails, you shop eBay. You hope someone in Taiwan has stock. This reality shows how control vintage drives total value in ways spindle hours cannot capture.

A 2012 machine with a Fanuc 0i-MD has a parts pipeline into the 2030s. A 1996 machine with a Fanuc 0M has a parts pipeline that ended in 2015. Both might produce the same parts today. Only one has a clear repair path next year.

The breakpoint in the Midwest market falls around 2005 to 2008. Machines before that window often run Series 0, 6, 10, 15, 16, or 18 controls. Those are obsolete or heading there. Machines after that window run 0i-B, 0i-C, or 0i-D variants. Parts are easier to find. If you are looking at a machine needing [Fanuc Series 0 / 0M / 0T Repair](/repairs/fanuc-cnc-machine-repair/series-0-legacy/), add salvage sourcing to your cost estimate.

## Control Families by Era

Fanuc's numbering confuses buyers. Here is a breakdown by era and market position.

**Series 0M / 0T / 0-Mate (1985-1995).** These ran on Hardinge, Mori Seiki, Wasino, and Okuma machines. The boards are 16-bit. Replacements are salvage-only. A working 0M today is worth $1,500 to $3,000 as a spare. Finding a CPU board can take months. Machines in this era are priced on iron alone. The control is a liability.

**Series 6 / 10 / 11 / 15 (1988-1998).** The 6 and 10 were workhorses on larger Mazak, Okuma, and Mori Seiki mills. The 15 ran high-end 5-axis work. All are now obsolete. A working 15-B might fetch $4,000 to $7,000. Drive and power supply failures are often terminal. Budget $3,000 to $8,000 for a control problem within 24 months. [Spindle Service on Fanuc Series 6 / 10](/spindle-grinding/fanuc-spindle-repair/series-6-15-legacy/) machines makes sense only if the control is stable.

**Series 16i / 18i / 21i (1998-2008).** These mark the shift to 32-bit boards and better service access. A Fanuc 18i-T in good shape still has parts for most boards. Some drive modules are getting scarce. Machines here are the sweet spot for shops wanting ability without new-machine cost. Pay a 10-15% premium for a verified 18i over an equal 16i or 21i. The support timeline is the reason.

**Series 0i-A / 0i-B / 0i-C (2004-2015).** The 0i family is Fanuc's mid-market standard. The 0i-A is aging out. The 0i-B and 0i-C remain well-supported. A Series 0i-D commands 15-25% premium over an 0i-B on the same iron. The 0i-D ships with current firmware, better networking, and longer board support.

**Series 0i-F / 30i / 31i / 32i (2015-present).** Current controls. Machines with these hold value. The support window runs another 10-15 years. A 2018 Doosan with a 0i-TF differs from a 2008 Doosan with a 0i-TB even if castings and spindle are alike.

## Ken's Diagnostic-on-Purchase Routine

Before signing for used iron, a 45-minute pass catches most hidden electrical issues. This is Ken's diagnostic-on-purchase routine from 30 years of bench and field work.

**Step 1: Cold start and alarm check.** Power the machine from cold. Watch the boot. Any alarm that clears on startup needs a look. Pull alarm history. Fanuc stores 100 to 200 alarms. A pattern of servo alarms on one axis tells you something the seller may not share.

**Step 2: Parameter backup battery state.** Every Fanuc has a lithium battery backing parameter memory. Below 2.8V means the machine is one outage away from losing its setup. A seller who skipped battery care may have skipped other things. Check the date code. A 2015 battery on a 2012 machine suggests decent upkeep. An original 2012 battery is a yellow flag.

**Step 3: Servo tuning and error check.** Run each axis through full travel at rapid and feed. Listen for grinding or hesitation. Pull the servo diagnostic screen. Check following error under load. A tuned axis shows under 10 pulses at feed. An axis at 30 to 50 pulses is worn or electrical. Budget repair either way.

**Step 4: Spindle load and heat.** Run the spindle at rated RPM for 5 to 10 minutes. Watch the load meter. A healthy spindle at no load shows 5-15% depending on design. A spindle at 25-30% no-load is bearing-worn or drive-limited. [Fanuc Spindle Repair](/spindle-grinding/fanuc-spindle-repair/) runs $4,000 to $9,000 based on spindle size.

**Step 5: Way cover walk-around.** Torn covers mean coolant and chips reached the way system. That speeds wear on guides or box ways. [Fanuc CNC Way Covers](/way-covers/fanuc-cnc-way-covers/) are replaceable. The damage they let in may not be. Look under them if the seller allows. Rust on ways is a red flag.

This pass does not replace a full check. It catches 80% of problems that cause surprise bills in year one.

## Pricing the Split

When you look at a used Fanuc machine, split the asking price in two.

**Iron value** covers the bed, castings, spindle, ballscrews, ways, ATC, coolant system, and enclosure. A well-kept Mori Seiki SL-25 bed and spindle is worth the same whether it runs a Fanuc 18i-T or a Siemens 840D. Iron value drops slowly if kept up. It drops fast if neglected.

**Control value** covers the CNC, drives, servo amps, power supply, panel, and cabling. A Fanuc 18i-T in working shape is worth $8,000 to $14,000. A Fanuc 0M is worth $1,500 to $3,000 and falling. Control value tracks an obsolescence curve, not a wear curve.

A real example: a 2004 Daewoo Puma 240 with a Fanuc 18i-T listed at $28,000. The iron is decent. It has 22,000 spindle hours, original ballscrews with some backlash, and intact covers. The control boots clean. Alarms are minor. Servo tuning is fine. Iron value is about $12,000 to $15,000. Control value is about $8,000 to $10,000. The price is fair.

Now a 1998 Okuma LB-15 with a Fanuc 0T-C listed at $18,000. The iron is cleaner—14,000 spindle hours, reground ways in 2010, newer ballscrews. But the 0T is obsolete. Iron value is $14,000 to $18,000. Control value is $2,000 to $3,000. The price is high because the control limits useful life.

This split matters for [Fanuc CNC Machine Repair](/repairs/fanuc-cnc-machine-repair/) planning. A machine where control value tops iron value is a retrofit choice if the control fails. A machine where iron value tops control value is a parts donor or rebuild project.

## Five-Year Ownership Cost by Era

Ownership cost over five years varies by control generation. These estimates come from our service history in Iowa, Illinois, Minnesota, Wisconsin, Nebraska, and Missouri.

**Series 0M / 0T (pre-1995).** Budget $6,000 to $15,000 in control repairs over five years if the machine runs in production. Parts sourcing takes time. A main board failure may mean a 6 to 12 week wait. Servo amp replacement runs $2,800 to $6,500 based on axis count and series. Those amps are hard to find.

**Series 16i / 18i (1998-2008).** Budget $3,000 to $8,000 over five years. Parts are available but not cheap. The 18i-T is still a solid choice if kept up.

**Series 0i-B / 0i-C (2008-2015).** Budget $2,000 to $5,000 over five years. This group has the best mix of ability, parts, and price on the used market.

**Series 0i-D and newer (2015-present).** Budget $1,000 to $3,000 over five years. Most of this is consumables like batteries and fans. These are under Fanuc's active support.

These numbers assume the machine is checked at purchase. A machine bought without a check can double these costs in year one. Our [Technical Insights](/insights/) library covers checks by subsystem.

## When Iron Matters More

Sometimes control age is secondary. If you buy for the spindle, turret, or ATC and plan to retrofit, the Fanuc is just a short-term tool. Retrofit houses can swap a failing 0M for a Centroid or Mach4 setup for $12,000 to $20,000 based on axis count.

The iron-first buyer looks for:

- Solid castings with no cracks or repairs
- Spindle with rebuild history or low hours
- Way system with wear under 0.001" on a level
- ATC that indexes cleanly
- Hydraulic and pneumatic systems without leaks

A 1992 Mori Seiki MV-40 with a failing Fanuc 11M might be worth $8,000 to $12,000 to a retrofit buyer. The same machine with a working 11M is not worth much more. The 11M adds short-term function, not long-term value.

Retrofit choices also apply to machines that outlived their OEM control support. [Way Covers for Siemens 840D Era Machines](/way-covers/dmg-mori-cnc-way-covers/siemens-840d/) can be sourced apart from the control. That keeps the iron useful after a swap.

## Sources & References

- Fanuc America parts bulletins (2020-2024)
- Midwest CNC Services service log (2019-2024)
- Secondary market data from Machinery Values, Surplus Record, and eBay sales
- Retrofit cost estimates from three Midwest integrators

## When to Bring This Work to Us

If you are looking at a used Fanuc machine and want a check before signing, we do pre-purchase visits across our seven-state area. We can run Ken's diagnostic-on-purchase routine on-site. We pull alarm history, check servo tuning, and give you a repair budget for the first 24 months. If the machine needs work after you buy, we handle [Fanuc CNC Machine Repair](/repairs/fanuc-cnc-machine-repair/) from drive swaps to full control overhauls. Reach out through our [quote form](/get-a-quote/) with the make, model, control, and seller location. We will scope the job from there.