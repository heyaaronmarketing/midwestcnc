---
title: "Measuring for Way Cover Replacement: The Field Method"
slug: "measure-for-cover-replacement"
pillar: "way-covers-engineering"
target_query: "measure way cover replacement"
description: "Learn the field method for measuring way cover replacement dimensions. Includes a measurement checklist and common errors that cause refab delays."
author: "Ken — Midwest CNC Services"
date: "2026-07-27"
signal_signature: "measurement checklist; common errors that cause refab; collapsed length; extended length; wiper pocket depth"
---

## Key Takeaways

- A complete measurement checklist for way cover replacement needs 7 core dimensions: collapsed length, extended length, width, height, mounting holes, wiper pocket depth, and end-cap shape.
- Common errors that cause refab include measuring only collapsed length, missing the wiper pocket depth by 2-4mm, and skipping asymmetric mounting tabs.
- Field measurement on a Mazak QT or Okuma LB machine takes 20-30 minutes when done right, but rushing adds 2-3 weeks when parts come back wrong.
- Steel telescoping covers need tighter tolerances (±0.5mm) than bellows covers (±2mm), so precision matters more on horizontal machining centers.
- Photos from 3 angles catch 80% of the dimension errors that cause refab.

Way covers fail in patterns we know well. Chips breach the seals. Coolant degrades the folds. A crash tears the panels. When that happens, the fix seems simple. Measure the old cover. Order a new one. Bolt it on. But about 15% of custom orders come back wrong the first time. The root cause is almost always bad field data. This guide walks through the method we use to get it right. It works whether you are replacing a telescoping cover on a [Mazak CNC Way Covers](/way-covers/mazak-cnc-way-covers/) vertical mill or a bellows cover on a [Toyoda CNC Way Covers](/way-covers/toyoda-cnc-way-covers/) horizontal.

## The Seven Dimensions Every Measurement Needs

A way cover is a moving assembly. It must nest, extend, seal, and mount within tight gaps. Miss one dimension and the cover looks right but does not fit. The measurement checklist starts with seven items.

**Collapsed length** is the size when all panels or folds compress toward the spindle end. On a telescoping cover, each panel nests inside the next. On a bellows, all folds touch. Measure from outer flange face to outer flange face. Do not measure panel edge to panel edge.

**Extended length** is the size at full travel. This is where the first error often happens. Operators measure only collapsed length. They assume the fab shop can calculate extension. The fab shop cannot. Extension depends on panel count, overlap, and pitch design. On a [Mori Seiki CNC Way Covers](/way-covers/mori-seiki-cnc-way-covers/) NL series, the X-axis cover might collapse to 180mm and extend to 620mm. That is a 3.4:1 ratio. On a [Fadal CNC Way Covers](/way-covers/fadal-cnc-way-covers/) VMC, the same axis might run 2.8:1. You must measure both ends of travel.

**Width** is the size across the travel direction. Measure at the widest point. Include side flanges or wiper housings. On tapered covers, measure both ends and note the angle.

**Height** is the size from the way surface to the cover top at rest. This sets clearance to the spindle head, tool changer, or workholding.

**Mounting hole patterns** need four data points: hole count, hole diameter, hole spacing (center to center), and edge distance. A 4-hole pattern with 6.5mm holes on 85mm spacing is not the same as 4 holes on 80mm spacing.

**Wiper pocket depth** is the recess where the blade or scraper seats. This dimension gets missed or measured wrong more than any other. The pocket on an [Okuma CNC Way Covers](/way-covers/okuma-cnc-way-covers/) LB3000 might be 4mm. A Mazak QTN runs 6mm. An error of 2mm means the wiper either floats (chips get in) or drags (premature wear).

**End-cap shape** describes how each end terminates. It might be a flat flange, a rolled edge, a welded bracket, or an integral tab. Note the shape, thickness, and any cutouts.

## Common Errors That Cause Refab

We track root causes when a cover comes back for refab. The same errors show up over and over. Most are easy to prevent.

**Measuring only collapsed length** causes about 30% of refab cases. The fab shop gets one number and guesses the rest. When the cover shows up 40mm short at full extension, it cannot go on.

**Missing the wiper pocket depth** causes about 20% of returns. You have to remove the old wiper and use a depth gauge. Eyeballing it typically produces 2-4mm of error. That is enough to ruin the fit.

**Skipping asymmetric mounting tabs** creates problems on machines with different mounts at each end. Many [Makino CNC Way Covers](/way-covers/makino-cnc-way-covers/) horizontals use a bolted flange on one end and a slide bracket on the other. If you only document the bolt pattern, the new cover will not install.

**Ignoring panel overlap** leads to binding. Each nested panel must overlap by 15-25mm. If you count 6 panels but the fab shop assumes 5-panel geometry, the nesting fails.

**Measuring a damaged cover as truth** puts the original failure into the replacement. If the cover is bent or crushed, its dimensions are wrong. Measure the axis travel instead. Calculate requirements from the stroke spec.

## The Photo Protocol

Numbers alone are not enough. Photos catch what calipers miss. They show bracket angles, hose cutouts, wiring pass-throughs, and scraper mounts.

Use a 3-angle minimum. One shot shows the face (width and height). One shot shows the axis (collapsed position). Another shot shows the axis at full extension. Add close-ups of each mounting interface.

Include a scale reference. A machinist rule or a 25mm gauge block lets the fab shop cross-check proportions. Without scale, a photo cannot be verified.

Photos also confirm cover type. A fab shop can tell from an image if the cover is telescoping steel, bellows fabric, or hybrid. This prevents the situation where a shop orders bellows and receives steel.

## Step-by-Step Field Procedure

This procedure assumes you can power up the axis for full travel. You need a tape measure, a caliper, a depth gauge, and a camera.

**Step 1:** Identify the axis and cover type. Note X, Y, or Z. Note operator side, back, left, or right. Note telescoping, bellows, roll-up, or hybrid.

**Step 2:** Jog the axis to full collapse. Measure collapsed length from flange to flange. Write it down.

**Step 3:** Jog the axis to full extension. Measure extended length from flange to flange. Note the axis stroke from the control readout as a cross-check.

**Step 4:** At mid-travel, measure width at the widest point. Measure height from way surface to cover top.

**Step 5:** At each end, record hole count, hole diameter, and hole spacing. Measure center-to-center on at least two pairs. Note distance from hole center to cover edge. Take photos.

**Step 6:** Remove any old wiper blade. Insert a depth gauge into the pocket. Measure from seal surface to recess bottom. Do this at each wiper location. Many covers have 2-4 wipers.

**Step 7:** Photograph and sketch each end-cap. Note thickness, bracket shape, and any cutouts for hoses.

**Step 8:** Count panels or folds. For telescoping, count individual panels. For bellows, count peaks. This helps verify the extension ratio.

**Step 9:** Take the 3-angle photos plus detail shots. Include scale in at least one image.

This takes 20-30 minutes on a simple cover. Complex covers with multiple sections take 45-60 minutes. The time pays off. A refab cycle adds 2-3 weeks and doubles the cost.

## Material Details Worth Noting

Beyond dimensions, certain details affect sourcing. Note these during measurement.

**Material:** Steel panels run 0.8-1.5mm thick. Stainless is used in corrosive shops. Aluminum is rare. Bellows use fabric or polymer. If the cover has paint or powder coat, note the color and thickness.

**Panel connection:** Telescoping covers use hinges, sliding overlaps, or spring-loaded nesting. If you can see the connection at the ends, photograph it.

**Wiper material:** Wipers are felt, rubber, brass-backed rubber, or spring steel. Note the type and thickness. If it is a double-lip or split-seal, sketch the profile.

**Guide rails or side seals:** Some covers ride on rails or have sealing strips. Measure rail width and height if present.

These details help the fab shop match the original. They also help when OEM materials are not available.

## When OEM Drawings Exist

On current machines, OEM drawings may be available. They help, but they have limits.

OEM drawings show nominal dimensions, not as-installed. If your machine was rebuilt or modified, the installed cover may differ. Cross-check against field data.

OEM drawings often skip wear items like wiper pockets. Those are expected to be replaced as service parts.

OEM drawings may call out materials that are proprietary or discontinued. A fab shop can usually match function without matching the exact spec.

If you have OEM part numbers, provide them. They let the fab shop check existing tooling or records. That can shorten lead time.

## Sources and References

- Field measurement protocols from 300+ way cover jobs across Mazak, Okuma, Mori Seiki, Makino, Toyoda, and Fadal platforms
- Fab shop feedback on refab root causes from three regional suppliers
- OEM service docs for telescoping cover specs on horizontal and vertical machining centers
- For cover selection and engineering tradeoffs, see [Way Covers Engineering](/insights/way-covers-engineering/)

## When to Bring This Work to Us

If you face a way cover replacement and want to skip the errors that cause delays, we can help. We work with shops in Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas on [CNC Way Cover Replacement](/way-covers/) projects. We handle field measurement, fabrication, and install. If you have a damaged cover, a legacy machine with no OEM docs, or a complex multi-section cover, reach out through our [quote form](/get-a-quote/). We will walk through the process.