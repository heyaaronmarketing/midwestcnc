---
title: "Trunnion-Adjacent Covers on 5-Axis: Why Bellows Win"
slug: "trunnion-bellows-on-5-axis"
pillar: "way-covers-engineering"
target_query: "5 axis way cover bellows"
description: "5 axis way cover bellows outperform telescoping designs near trunnions. Learn the geometric envelope explanation and common failure points driving this choice."
author: "Ken — Midwest CNC Services"
date: "2026-11-10"
signal_signature: "geometric envelope explanation; common failure points; angular displacement exceeds 120 degrees; accordion-style bellows fold inward; debris accumulation at wiper seals"
---

## Key Takeaways

- Trunnion covers on 5-axis machines handle angular displacement that exceeds 120 degrees in A-axis rotation while sealing against coolant and chips.
- Bellows last 2-3 service intervals longer than telescoping plates in trunnion spots because accordion-style bellows fold inward rather than sliding.
- The geometric envelope explanation for bellows centers on curved travel paths that plates cannot follow without binding.
- Common failure points include wiper seal wear, fold cracking, and debris accumulation at wiper seals during indexing.
- Custom bellows take 10-14 days versus 3-6 weeks from OEM sources when field dimensions are accurate.

The trunnion table on a 5-axis VMC creates a cover problem most shops ignore until failure stops the spindle. The Haas UMC-750, DMG Mori DMU 50, and Doosan DVF 5000 all use bellows near their trunnions. Why? Linear covers can't handle rotary motion. This article explains the engineering behind that choice. We'll cover why bellows win, where plates still make sense, and how to spec replacements.

## The Curved Path Problem

Every way cover shields ballscrews, guides, and encoders from chips and coolant. On X, Y, and Z axes, covers span straight lines. You calculate stroke, add wiper overlap, and pick the right material. Simple geometry.

Trunnions break that model. The A-axis on a typical 5-axis VMC swings through 120 to 150 degrees. The B-axis adds up to 360 degrees of rotation. Covers near these rotary centers trace arcs, not lines.

This is the geometric envelope explanation in action. The "envelope" is the 3D space a cover sweeps through. For a trunnion, that space forms a partial toroid—like a slice of a donut. Telescoping plates slide on nested rails. They work in straight lines. They bind on curves.

The inner radius of a tilt arc concentrates all the compression force. Plates wedge against each other there. We see this on [Haas UMC Series Way Covers](/way-covers/haas-cnc-way-covers/umc-series/) when shops try flat plates instead of OEM bellows. Jamming starts within 200-400 hours of real 5-axis work.

## How Bellows Handle Rotation

Bellows fold inward on themselves. They don't slide. That makes them fit curved paths in ways plates cannot.

Each fold acts like a hinge. When the trunnion tilts, folds on one side compress tighter. Folds on the other side open. No plates drag. No wipers scrape nested surfaces. The accordion-style bellows fold inward along the arc naturally.

Material matters too. Trunnion bellows use layered polyester with PVC or urethane coating. Spring steel frames inside keep folds from collapsing or bunching. The steel holds shape under compression and extension.

On [Doosan DVF / FM Way Covers](/way-covers/doosan-cnc-way-covers/5-axis-verticals/), the OEM uses 12 folds for the A-axis cover. Each fold handles about 10 degrees of compression. That gives 120 degrees of range—matching the DVF 5000's A-axis spec of +30 to -120 degrees exactly.

## Common Failure Points

Even bellows wear out under 5-axis stress. Knowing where they fail helps you time replacements.

**Fold cracking.** This is the failure we see most often. PVC coating fatigues at fold creases after 8,000 to 15,000 hours. Cracks start as hairlines. They spread until the fold splits open. Coolant gets in within days of a visible crack.

**Debris accumulation at wiper seals.** Bellows still need perimeter seals at mounting points. Brush or lip wipers trap chips over time. Rotation grinds trapped debris against the seal. It wears fast. On high-chip aluminum work, check seals every 2,000 hours.

**Spring steel corrosion.** Internal frames rust when coolant soaks through fabric. Rusted frames lose spring force. Folds get "lazy" and don't extend fully. Slack lets chips migrate into protected areas.

**Mounting frame fatigue.** Bellows bolt to aluminum or steel frames. Trunnion tilt loads these frames in cycles. Fasteners loosen after 5,000-10,000 hours. Thread-locker at install helps. Frame fastener checks should be in your PM list.

[DMG Mori CNC Way Covers](/way-covers/dmg-mori-cnc-way-covers/) on DMU machines show one pattern worth noting. On certain 2018-2020 builds, the adhesive bond between bellows and frame fails before the fabric wears. If your DMU's trunnion cover peels at the frame edge, it's an adhesive issue. You'll need a new frame with the new bellows.

## Where Plates Still Win

Bellows dominate near trunnions. Plates still work better for linear axes—even on 5-axis machines.

X, Y, and Z still travel in straight lines. Plates handle straight motion well. The nested overlap design fits that geometry. Plates also resist chip impact better than fabric. A heavy chip dents a steel plate. It may puncture a bellows.

[Mazak CNC Way Covers](/way-covers/mazak-cnc-way-covers/) on the VARIAXIS show this hybrid approach. Bellows cover the trunnion. Steel plates cover X and Y. Mazak's engineers chose this because linear axes see heavier chip loads. The trunnion area needs flex that only bellows provide.

The cover decision comes down to three questions:

1. Is the travel path straight or curved?
2. How heavy is the chip load in that zone?
3. What coolant chemistry is in play?

Curved travel means bellows. High chip loads on straight travel mean plates. Aggressive coolant chemistry is a separate material question.

## How to Spec Replacement Bellows

When a trunnion bellows fails, you can go OEM or custom. Both paths work. The right choice depends on timing and precision needs.

**OEM parts** match dimensions exactly. They fit existing frames because they match original drawings. Lead times run 3-6 weeks for common platforms. Cost falls between $800 and $2,500 depending on machine and size.

**Custom fabrication** is faster—10-14 business days with good field data. But you must measure accurately. Critical dimensions include:

- Compressed length (minimum fold stack)
- Extended length (full deployment)
- Cross-section width and height
- Mounting bolt pattern
- Material thickness

[Okuma CNC Way Covers](/way-covers/okuma-cnc-way-covers/) on MU-V machines need trapezoidal profiles. That differs from the rectangular shapes common elsewhere. Measure cross-section at both compressed and extended positions. The angle changes under compression. Fabricators need both numbers.

For [Way Covers for Heidenhain TNC Era Machines](/way-covers/dmg-mori-cnc-way-covers/heidenhain-tnc/), watch out for obsolete part numbers. Pre-acquisition naming conventions may not match current DMG Mori catalogs. Cross-reference before ordering.

[Haas CNC Way Covers](/way-covers/haas-cnc-way-covers/) benefit from Haas's standard parts system. The UMC-750 and UMC-1000 use the same trunnion bellows. Parts stay available and priced reasonably. Not every maker does this. Doosan uses different bellows across the DVF 5000, 6500, and 8000 despite the shared family name.

## Install Tips That Prevent Early Failure

Bellows install orientation matters. Folds must compress inward, not balloon outward. Backwards install causes binding on the first A-axis move.

Pre-tension matters for spring-frame bellows. They ship partly compressed. Don't stretch them to full length during install. That removes the spring force that organizes folds during compression. Keep bellows at 70-80% extension while mounting. Let the axis cycle position them naturally.

Sealant at frame junctions is not optional. OEM bellows ship without perimeter sealant. That's your job. Use flexible silicone or urethane rated for coolant. RTV silicone works but needs 24 hours to cure before coolant hits it. We prefer Loctite 5900 for trunnion jobs. It reaches handling strength in 4 hours.

## Sources and References

This article draws from our 2022-2025 service logs covering trunnion bellows work on 47 5-axis VMCs. Platforms include Haas, DMG Mori, Doosan, Mazak, and Okuma. Material data references Hennig and Beakbane technical sheets. Angular displacement specs come from OEM machine documentation for the platforms named.

## When to Bring This Work to Us

A cracked or peeling trunnion cover needs attention in weeks, not months. Running with a failed bellows puts ballscrews and encoders at risk. Those components cost 10-20 times what the cover costs.

We handle OEM sourcing and custom builds for trunnion bellows across major 5-axis platforms. Field measurement help is available in Iowa. Photo and spec consultation works for our broader service area. Start at [/get-a-quote/](/get-a-quote/) with your machine model and a photo of the current cover.