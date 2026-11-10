---
title: "What We Bring on a Field Call (and What We Don't)"
slug: "what-service-truck-carries"
pillar: "field-service-logistics"
target_query: "cnc field service truck contents"
description: "CNC field service truck contents explained: what diagnostic tools, drives, and spare parts we carry on every call, and what stays back at the shop."
author: "Ken — Midwest CNC Services"
date: "2026-11-10"
signal_signature: "4-channel scope rated to 200 MHz; we do not carry spindle cartridges; Fanuc αi and βi servo amplifiers; thermal imaging camera; spindle encoders in stock"
---

## Key Takeaways

- Our service truck carries over 340 items. These include diagnostic gear, common drives, power supplies, and hand tools. This loadout resolves about 70% of field issues on the first visit.
- A 4-channel scope rated to 200 MHz and thermal imaging camera form the diagnostic backbone. Finding the actual failure matters more than swapping parts blind.
- We do not carry spindle cartridges, large servo motors, or complete control units. Field installation of these parts often creates more problems than it solves.
- The truck inventory reflects 30 years of field data. Items that fail often, fail without warning, and install safely on-site earn their place.
- Drive boards for Fanuc, Mitsubishi, and Siemens controls are the highest-value cargo. These parts fail without warning. Ship times from distributors run 3-10 business days.

When a production line goes down, the clock starts. What rolls up in our truck decides whether you cut chips that afternoon or wait a week for parts. From our base in [Waterloo CNC Repair & Service](/service-area/waterloo-iowa/), we have refined this loadout through thousands of calls. We cover Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Every item earns its spot through a simple test: does it help us diagnose well and fix safely in a shop that isn't ours?

## The Diagnostic Layer Comes First

A truck full of parts means nothing if you swap the wrong one. We front-load every call with measurement before any wrench comes out.

The scope is the most important tool on the truck. We carry a 4-channel scope rated to 200 MHz. It handles encoder feedback, spindle drive waveforms, and serial data lines. Most intermittent faults—the ones that alarm once a shift and then clear—only show up under signal analysis. Swapping a $2,400 drive board on a hunch is costly guessing.

The thermal imaging camera catches what the scope misses. Failing capacitors, loose bus bars, and overloaded contactors all run hot before they throw alarms. A 15-second thermal sweep of a drive cabinet often points right at the problem. This helps most when the original alarm code is vague.

We also carry Renishaw ballbar cables for alignment checks. When a customer reports drift or circle errors, confirming geometric condition before pulling covers saves hours. Sometimes the issue is a worn way, not the drive.

Digital meters, meggers for insulation testing, and calibrated clamps round out the kit. The megger gets used on every spindle motor check. Insulation breakdown hides until it fails hard. A 500V test at temperature catches motors that pass cold.

## Parts We Carry for On-Site Swaps

Certain parts fail often, fail without warning, and install cleanly in field conditions. These earn truck space.

Our drive board stock covers three control families. They make up about 80% of machines in our [Service Area Coverage](/service-area/). We keep Fanuc αi and βi servo amplifiers, spindle amps, and power supply modules. Mitsubishi MDS-B and MDS-C series drives travel with us. So do Siemens 611D and S120 modules. A single drive swap that gets a machining center running beats any other repair we do.

Power supplies fail almost as often as drives. They also diagnose quickly. We carry switching supplies in the 5V, 12V, and 24V ranges common to Fanuc, Mazak, and Haas. A $180 supply on the truck beats the same supply that ships in three days.

Encoders, resolvers, and feedback cables make up the next tier. Spindle encoders take mechanical abuse and electrical noise. We have spindle encoders in stock: Fanuc α-series, Heidenhain ERN and ROD series, and Tamagawa resolvers. Feedback cables fail from flex and coolant. Carrying pre-made cables in standard lengths means we can restore closed-loop control fast.

Contactors, relays, and fuses seem boring but cause many calls. A failed coolant pump contactor throws a generic alarm. We carry spares in common frame sizes from Fuji, Mitsubishi, and Allen-Bradley. We also stock fuses for drive input stages.

Hand tools and consumables fill the rest: Torx and hex sets in metric and imperial, JIS drivers that fit Japanese fasteners, thermal compound, Loctite, cable ties, and heat shrink. This keeps a repair clean rather than held together with tape.

## What Stays Back at the Shop

Some parts need bench conditions that don't exist in your facility. Others need test gear we can't bring. Knowing what we leave behind explains why some repairs require shipping.

We do not carry spindle cartridges. A rebuild involves bearing preload measurement, balance to 0.1 gram, and runout checks at multiple taper positions. These need a climate-controlled room with granite plates and calibrated indicators. Field install without this check creates risk. A spindle that tests "fine" during commissioning can fail three weeks later from wrong preload or residual imbalance. Our [CNC Machine Repair Services](/repairs/) page covers when spindle work goes to the bench versus on-site.

Large servo motors stay at the shop for similar reasons. A 30kW spindle motor weighs 180 pounds. It needs lifting gear, precise coupling alignment, and often brake work. Field install risks dropping it, misaligning the shaft, or fouling the encoder. We bring small motors—1kW to 5kW units on tool changers, pallet systems, and chip conveyors. Two techs can handle and align these safely.

Complete CNC controls rarely travel. A Fanuc 0i-TF or Mazak SmoothX runs $15,000 to $40,000. It needs parameter backup, restore, and verification across hundreds of settings. Field control swaps happen, but we schedule them in advance. The replacement gets pre-configured before we load it. We don't carry control units hoping to match whatever machine we find.

Brand-specific tooling gets prioritized by call schedule. If we head to a Doosan shop, the truck gets Doosan drive pulls and connector kits. Generic calls get the generic loadout. This is why we ask about model and serial during dispatch—it shapes what shows up.

## How the Loadout Reflects Real Field Data

Our inventory isn't theory. It comes from tracking every call. We log what part actually failed versus what the first guess was. We note every return trip caused by a missing item.

Over 12 months last year, drive boards accounted for 23% of on-site fixes. Power supplies came in at 14%. Encoders and feedback issues combined for 18%. These three groups alone—all items we carry—covered over half of first-visit repairs.

The other half involved parts we don't carry: spindles, ball screws, way systems, large motors. In those cases, the call's value came from accurate diagnosis and scope of work documentation. Knowing exactly what failed, ordering the right part, and scheduling the return trip turns "machine's acting up" into a planned repair with known downtime.

This explains why we don't guess. A shop that asks us to "bring a spindle and swap it" usually hasn't confirmed the spindle is the problem. We have seen calls where the spindle was fine but the VFD had a failing IGBT. We have seen spindles with good bearings but a collapsed drawbar spring pack. Accurate diagnosis saves the customer from buying parts they don't need.

## Coverage Radius and Truck Response

Your location relative to Waterloo sets how fast a stocked truck arrives. Our [Field Service & Logistics (Midwest)](/insights/field-service-logistics/) hub covers the realities of a seven-state footprint.

Shops within [The 4-Hour Drive Radius: What Iowa Shops Get](/insights/field-service-logistics/iowa-four-hour-radius/) see the fastest dispatch. A call from [Davenport CNC Repair & Service](/service-area/davenport-iowa/) at 7 AM can often have a truck on-site by late morning. That truck carries the full diagnostic kit and drive inventory.

[Rochester CNC Repair & Service](/service-area/rochester-minnesota/) and similar markets in southern Minnesota, northern Illinois, and eastern Nebraska fall in the 4-6 hour band. Response is typically next-day unless the call comes early. The truck stock stays the same—distance changes arrival time, not cargo.

Beyond six hours, field service math shifts. A shop in central Texas or western Missouri may find shipping the assembly to Waterloo beats 12+ hours of road time plus lodging. We run these numbers openly. The right answer depends on the machine, the urgency, and the failure mode.

## Sources & References

- Internal service call records, Midwest CNC Services, 2023-2024 period
- Truck inventory manifest, updated quarterly
- Fanuc αi and βi series documentation
- Siemens SINAMICS S120 service manual
- Mitsubishi MDS-B/C series specs
- Renishaw QC20-W ballbar operating manual

## When to Bring This Work to Us

If your machine is down and you're unsure what it needs, describe what you see. Alarm codes, when the problem started, what changed—this shapes whether we dispatch a truck or recommend shipping the part.

Start at [get a quote](/get-a-quote/). Tell us the machine, the symptom, and your location. We'll explain what the truck can handle on-site versus what needs to come back to Waterloo.