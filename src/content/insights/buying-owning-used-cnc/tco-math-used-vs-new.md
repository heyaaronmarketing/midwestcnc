---
title: "Total Cost of Ownership: Used vs. New"
slug: "tco-math-used-vs-new"
pillar: "buying-owning-used-cnc"
target_query: "cnc total cost of ownership"
description: "CNC total cost of ownership math comparing used vs. new machines. Real numbers across 7 cost categories over a 10-year horizon."
author: "Ken — Midwest CNC Services"
date: "2026-11-23"
signal_signature: "7 cost categories over 10 years; acquisition at 35-45 percent of new; $8,000-$15,000 per year in scheduled service; $150-$300 per hour of lost production; spindle rebuild at $6,500-$18,000"
---

## Key Takeaways

- CNC total cost of ownership includes 7 cost categories over 10 years: acquisition, installation, maintenance, unscheduled repairs, consumables, energy, and eventual disposition.
- A used machine typically sells at acquisition at 35-45 percent of new, but maintenance and repair costs in years 1-5 often run 1.5-2x higher than a new machine under manufacturer coverage.
- Shops should budget $8,000-$15,000 per year in scheduled service for a used VMC or lathe, depending on spindle hours and control generation.
- Downtime cost is the hidden multiplier—at $150-$300 per hour of lost production, a single major failure can dwarf the initial purchase savings.
- The break-even point where used makes financial sense typically falls between 5-7 years of ownership, assuming the machine was properly inspected before purchase.

The purchase price on the auction listing is maybe 20% of what that machine will actually cost you over the next decade. I have watched shops buy a $65,000 used horizontal, congratulate themselves on the savings, and then spend $40,000 in unplanned repairs over 36 months because the ballscrews were worn and the spindle bearings were marginal at delivery. The math still worked out for them—barely. It only worked because they understood total cost of ownership before they wrote the check, not after the first emergency service call.

## The 7-Category TCO Framework

This framework covers 7 cost categories over 10 years. These categories come from tracking actual service invoices, parts costs, and downtime reports across the brands we work on regularly: Mazak, Haas, Okuma, Doosan, DMG Mori, and Fanuc-controlled machines.

**Category 1: Acquisition cost.** The purchase price, including auction fees, broker commissions, and any pre-purchase inspection costs. For used equipment, budget 1-3% of purchase price for a qualified inspection if you are buying sight-unseen.

**Category 2: Rigging and installation.** Moving a 15,000-pound VMC costs $3,500-$8,000 depending on distance. A 40,000-pound horizontal with a pallet changer might run $12,000-$20,000. New machines often include installation in the purchase agreement. Used machines rarely do.

**Category 3: Scheduled maintenance.** This covers the preventive work: way lube systems, hydraulic oil changes, filter replacements, annual alignment verification, spindle inspections. For a used machine running two shifts, budget $8,000-$15,000 per year in scheduled service. New machines under manufacturer coverage typically see $3,000-$6,000 annually in owner-responsible maintenance.

**Category 4: Unscheduled repairs.** The failures that stop production. Spindle bearings, ballscrew replacement, servo drive failures, control board issues. This is where used machines diverge sharply from new. A new machine under manufacturer coverage might see $500-$2,000 in unscheduled repair costs annually. A used machine outside coverage? We typically see $5,000-$25,000 per year, depending on age, condition, and how hard it runs. For more on how repair lead times affect your planning, see [Spindle Rebuild Lead Time: What Actually Drives It](/insights/spindle-diagnostics/spindle-rebuild-lead-time/).

**Category 5: Consumables.** Tooling, coolant, way oil, filters, wipers. These costs are roughly equivalent between used and new machines of similar specification. Budget $4,000-$10,000 annually depending on production volume.

**Category 6: Energy.** A 30-HP spindle VMC running two shifts draws roughly $8,000-$12,000 in electricity annually at Midwest industrial rates. Older machines often run less efficiently. Expect 10-20% higher energy costs for pre-2010 equipment versus current production.

**Category 7: Disposition.** What is the machine worth at end of ownership? New machines depreciate fastest in years 1-3, then stabilize. Used machines hold value more consistently if maintained. A $200,000 new VMC might sell for $80,000 after 10 years. A $75,000 used machine of equivalent age might sell for $35,000. This residual value offsets total ownership cost.

## Worked Example: Used vs. New VMC Over 10 Years

Here are real numbers comparing two scenarios. Both are 40-taper vertical machining centers with 10,000-RPM spindles, running two shifts in a job shop environment.

**Scenario A: New machine at $185,000**

| Category | Years 1-3 | Years 4-7 | Years 8-10 | 10-Year Total |
|----------|-----------|-----------|------------|---------------|
| Acquisition | $185,000 | — | — | $185,000 |
| Installation | $6,000 | — | — | $6,000 |
| Scheduled maintenance | $12,000 | $20,000 | $18,000 | $50,000 |
| Unscheduled repairs | $3,000 | $24,000 | $30,000 | $57,000 |
| Consumables | $21,000 | $28,000 | $21,000 | $70,000 |
| Energy | $27,000 | $36,000 | $27,000 | $90,000 |
| Disposition credit | — | — | ($80,000) | ($80,000) |
| **Net 10-year TCO** | | | | **$378,000** |

**Scenario B: Used machine (8 years old) at $72,000**

| Category | Years 1-3 | Years 4-7 | Years 8-10 | 10-Year Total |
|----------|-----------|-----------|------------|---------------|
| Acquisition | $72,000 | — | — | $72,000 |
| Pre-purchase inspection | $1,500 | — | — | $1,500 |
| Installation | $7,500 | — | — | $7,500 |
| Scheduled maintenance | $30,000 | $40,000 | $30,000 | $100,000 |
| Unscheduled repairs | $36,000 | $45,000 | $35,000 | $116,000 |
| Consumables | $21,000 | $28,000 | $21,000 | $70,000 |
| Energy | $32,000 | $43,000 | $32,000 | $107,000 |
| Disposition credit | — | — | ($18,000) | ($18,000) |
| **Net 10-year TCO** | | | | **$456,000** |

In this example, the used machine costs $78,000 more over 10 years despite the $113,000 lower acquisition price. The difference comes from higher maintenance burden, more unscheduled repairs, and lower resale value at disposition.

The critical variable is not in this table yet: downtime cost.

## The Downtime Multiplier

The numbers above assume both machines have equivalent uptime. They will not. This is where the [Production Downtime Cost: Framing the Urgency](/insights/field-service-logistics/production-downtime-cost-framing/) calculation matters.

A typical Midwest job shop bills $85-$150 per machine hour. Fully loaded internal costs often run higher. Using a conservative estimate of $150-$300 per hour of lost production, here is what unscheduled downtime actually costs:

The used machine in our example will likely see 40-80 more hours of unplanned downtime annually than the new machine. Those hours go to waiting for parts, waiting for service, dealing with nuisance failures that a newer machine would not have. At $200/hour lost production:

- 60 extra downtime hours × 10 years × $200/hour = $120,000 in additional production loss

Add that to the $456,000 TCO and the used machine is now at $576,000 versus $378,000 for new. The gap has widened to nearly $200,000.

## When Used Machines Make Financial Sense

The numbers above look bad for used equipment. They represent a worst-case scenario: a machine bought without proper inspection, running in a high-demand production environment. Used machines absolutely make financial sense in several situations.

**Lower utilization environments.** A machine running one shift with 30% uptime will not accumulate the wear that breaks our math. Maintenance costs scale with hours, not years. A lightly used machine might hit the 10-year TCO break-even at year 4-5.

**Specific platform advantages.** Some older machines are better suited to certain work. The control generation matters significantly. See [Used Okuma: OSP Era and Resale](/insights/buying-owning-used-cnc/used-okuma-osp-era-impact/) for how OSP generations affect long-term parts availability. A shop doing prototype work might prefer the simplicity of an older Fanuc 18i control over a newer 31i.

**Known history machines.** A machine with complete service records from a single owner, sold because of a plant closure rather than reliability problems, is a different risk profile than an auction machine with unknown provenance. We have seen shops get excellent value from machines they inspected themselves or bought from facilities they knew.

**Planned capital for initial repairs.** The smart play when buying used is to budget for immediate work. If a spindle rebuild at $6,500-$18,000 is in your first-year plan rather than a surprise, the math changes. Same with ballscrew replacement, way cover restoration (see [The Hidden Cost of Running with Damaged Covers](/insights/way-covers-engineering/hidden-cost-damaged-covers/)), or control component refreshes.

## The Control vs. Iron Value Split

Separating the value of the iron from the value of the control helps shops evaluate used equipment. The [Used Fanuc-Controlled Machines: Control vs. Iron Value](/insights/buying-owning-used-cnc/used-fanuc-machines-control-vs-iron/) article covers this in detail. The short version: a solid casting with worn-out controls is not necessarily a bad buy if retrofit economics work. A newer control on a machine with geometry problems is usually not worth saving.

For used machines under consideration:

- Get geometry verification (straightness, squareness, positioning accuracy) separate from control functionality checks
- Check parts availability for the specific control generation
- Understand retrofit costs if control replacement becomes necessary

A full Fanuc control retrofit runs $45,000-$85,000 depending on axis count and integration complexity. The same logic applies to other OEMs. The [Used DMG Mori: Identifying Post-Merger Machines](/insights/buying-owning-used-cnc/used-dmg-mori-post-merger/) piece explains why the 2015 merger matters for parts sourcing.

## Building Your Own TCO Spreadsheet

Here is how to build a realistic TCO model for a specific machine you are evaluating.

**Step 1: Establish baseline costs.** Get the acquisition price firmed up. Include buyer's premium if auction, inspection costs, and rigging quotes. Call riggers before bidding.

**Step 2: Request service history.** Any reputable seller can provide maintenance logs. No logs? Discount the machine 15-20% in your model to account for unknown condition, or walk away.

**Step 3: Get platform-specific maintenance estimates.** Call a service provider who works on that brand. Ask what scheduled maintenance costs for that platform in your utilization scenario. We do this regularly for shops in our [service area](/service-area/).

**Step 4: Build a repair reserve.** For a used machine outside manufacturer coverage, reserve 15-20% of acquisition cost annually for unscheduled repairs in years 1-3. If nothing breaks, you have funded future repairs.

**Step 5: Factor in your downtime cost.** Be honest about what an hour of lost production costs your operation. Multiply by expected additional downtime versus a new machine. 40-80 hours annually is a reasonable estimate for well-maintained used equipment.

**Step 6: Estimate disposition value.** Look at current asking prices for machines 10 years older than what you are buying. That is roughly your end-of-ownership value.

## Sources and References

The TCO framework and cost ranges in this article come from service log aggregation across machines we have worked on in Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Specific cost ranges:

- Rigging estimates from regional machinery movers serving the Midwest
- Energy calculations from DOE industrial motor efficiency data and Midwest utility rate schedules
- Depreciation curves from auction results tracked 2019-2024 across major platforms

For more context on the buying decision, the [Buying & Owning Used CNC](/insights/buying-owning-used-cnc/) pillar page links to era-specific guides and inspection checklists.

## When to Bring This Work to Us

If you are evaluating a used machine purchase and want an independent assessment of likely repair costs, we can help. We perform pre-purchase inspections across the Midwest. We check spindle condition, geometry, control health, and subsystem wear. We also provide platform-specific maintenance cost estimates based on what we actually see in the field.

If you already own the machine and are trying to decide between major repair and replacement, the same TCO math applies. You just have better information since you have actual service history. Our [repairs](/repairs/) work covers the diagnostics needed to build an accurate repair-vs-replace comparison.

Ready to get real numbers for your situation? [Request a quote](/get-a-quote/) and tell us what you are evaluating.