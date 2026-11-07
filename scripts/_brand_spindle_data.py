"""Spindle hub-and-spoke content for the 6 priority brands.

Mirrors the BRAND_HUB_DATA structure in generate_brand_pages.py but for
spindle-specific service work. Each brand has:
  - browse_series:   list[(name, url, desc)]  — spindle series-spoke links
  - browse_control:  list[(name, url, desc)]  — spindle control-spoke links
  - browse_service:  list[(name, url, desc)]  — cross-links to repair / way-covers
  - faq:             list[(q, a)]             — ≥5 spindle-specific Q&As
  - series_spokes:   dict[slug -> {...}]      — per-series spindle spoke content
  - control_spokes:  dict[slug -> {...}]      — per-control spindle spoke content
  - hero_lede / what_brings / how_we_approach / browse_control_intro

Per-spoke content unique to spindle work: spindle types used (cartridge vs.
integrated vs. B-axis), bearing-pack rebuild patterns, taper grinding /
runout verification, balance-class requirements, kinematic verification
on multi-axis platforms. No fabricated specifics — content draws on
standard CNC spindle service practice.
"""

# ============================================================
# MAZAK SPINDLE
# ============================================================
_MAZAK_SPINDLE_SERIES_SPOKES = {
    "quick-turn": {
        "title":   "Mazak Quick Turn Spindle Repair",
        "slug":    "mazak-spindle-quick-turn",
        "subtitle":"Quick Turn / QTN",
        "url":     "/spindle-grinding/mazak-spindle-repair/quick-turn/",
        "intro":   "Quick Turn and Quick Turn Nexus spindles are the most common Mazak spindles we see on the bench. The line uses cartridge-style turning spindles across QT-8 through QTN-450 with different bearing arrangements per size class. Smaller QT lathes use lighter-duty cartridges; QTN-300 and up have higher-RPM bearing packs that show different wear patterns. MS and MSY twin-spindle variants add sub-spindle synchronization considerations after any spindle work.",
        "failures": [
            "Front bearing wear from sustained high-coolant production — the most common single failure on this platform.",
            "Encoder contamination from coolant intrusion at the spindle nose.",
            "Chuck cylinder leaks that affect spindle preload and bearing life downstream.",
            "Draw-tube wear on bar-feed production over years of cycle count.",
            "Sub-spindle alignment drift on MS/MSY twin-spindle variants — requires synchronization verification after any spindle rebuild.",
        ],
        "controls_paragraph": "Older Quick Turn spindles ran on machines with [Mazatrol Legacy controls](/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/) — the spindle drive generation matters because legacy spindle parameters are stored differently than modern. Mid-2000s through 2013 Quick Turn Nexus shipped with [Mazatrol Matrix](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/) — Matrix-generation spindle drives are well documented and well supported. Current Compact, Smart, and Ultra Quick Turns ship on [SmoothG and SmoothAi](/spindle-grinding/mazak-spindle-repair/smooth-control/).",
        "siblings": [
            ("Mazak Integrex spindle work",        "/spindle-grinding/mazak-spindle-repair/integrex/"),
            ("Mazak Turning Legacy spindle work",  "/spindle-grinding/mazak-spindle-repair/turning-legacy/"),
        ],
    },
    "integrex": {
        "title":   "Mazak Integrex Spindle Repair",
        "slug":    "mazak-spindle-integrex",
        "subtitle":"Integrex Mill-Turn",
        "url":     "/spindle-grinding/mazak-spindle-repair/integrex/",
        "intro":   "Integrex multitasking machines have two spindles each — a turning spindle in the headstock and a B-axis milling spindle in the upper-tooling. The milling spindle is the higher-stress component because it sees both axial and lateral cuts under load. Bearing-pack life is shorter than on a straight VMC, and post-rebuild kinematic alignment matters more because mill-turn tolerances are tighter than on either lathe or vertical mill alone.",
        "failures": [
            "B-axis milling spindle bearing-pack wear from sustained heavy cuts — primary failure mode on Integrex platforms.",
            "Turning spindle bearing wear under heavy axial loads on e-series and i-H machines.",
            "Encoder drift on the B-axis spindle after thermal cycling — particularly on Integrex i-200 and 300 originals.",
            "Lower-turret spindle issues on e-series multi-spindle configurations.",
            "Spindle chiller faults that lead to thermal-related bearing damage if not caught early.",
        ],
        "controls_paragraph": "Original Integrex i-series spindle drives paired with [Mazatrol Matrix controls](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/); current i-H, i-V, and e-V/10 ship on [SmoothX](/spindle-grinding/mazak-spindle-repair/smooth-control/). After any B-axis spindle work, we run the kinematic verification rather than handing it back for the shop to chase — that's standard Integrex service practice.",
        "siblings": [
            ("Mazak Variaxis spindle work",     "/spindle-grinding/mazak-spindle-repair/variaxis/"),
            ("Mazak Quick Turn spindle work",   "/spindle-grinding/mazak-spindle-repair/quick-turn/"),
        ],
    },
    "variaxis": {
        "title":   "Mazak Variaxis Spindle Repair",
        "slug":    "mazak-spindle-variaxis",
        "subtitle":"Variaxis 5-Axis",
        "url":     "/spindle-grinding/mazak-spindle-repair/variaxis/",
        "intro":   "Variaxis spindles are 5-axis trunnion-table verticals — i-300 through i-800, J-series and C-series, and the legacy 500/630/730. The spindles see aerospace and mold-die work where bearing pack precision matters more than on production lathes. RTCP and kinematic alignment are part of any spindle service on this platform because 5-axis tool-tip-positioning depends on spindle geometry staying tight to the trunnion centerline.",
        "failures": [
            "Bearing pack wear under sustained high-RPM 5-axis finishing cuts — particularly on i-series machines running aerospace work.",
            "Taper damage from a toolholder failure or crash — common cause of unscheduled spindle work on Variaxis.",
            "Coolant intrusion at the spindle nose from heavy-coolant aluminum production.",
            "Kinematic drift after spindle work — requires full RTCP re-calibration as part of the rebuild.",
            "Spindle chiller thermal issues affecting bearing-pack life.",
        ],
        "controls_paragraph": "Current Variaxis i-series ships on [SmoothX](/spindle-grinding/mazak-spindle-repair/smooth-control/); legacy Variaxis 500/630/730 ran on [Mazatrol Matrix](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/) or earlier. Variaxis kinematic verification after spindle work is brand-specific — we run the calibration sequence as part of every rebuild because tool-tip accuracy on 5-axis depends on it.",
        "siblings": [
            ("Mazak Integrex spindle work",                "/spindle-grinding/mazak-spindle-repair/integrex/"),
            ("Mazak Vertical Machining Center spindles",   "/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/"),
        ],
    },
    "vertical-machining-centers": {
        "title":   "Mazak VTC + VCN Spindle Repair",
        "slug":    "mazak-spindle-vertical-machining-centers",
        "subtitle":"VTC + VCN Verticals",
        "url":     "/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/",
        "intro":   "VTC and VCN spindles are the highest-volume Mazak spindles after Quick Turn. The two families use different spindle types — VTC long-bed machines have heavier-duty production spindles with longer rebuild intervals; VCN high-RPM machines run lighter, faster spindles that wear quicker under sustained production. The VTC-800 in particular sees long-cycle axial production that creates specific wear patterns.",
        "failures": [
            "High-RPM bearing failure on VCN-510C and VCN-530C from sustained high-coolant aluminum work.",
            "Long-bed VTC-800 spindle bearing wear from extended axial production cycles.",
            "Taper damage from toolholder issues or chip ingress during ATC sequences.",
            "Coolant intrusion at the spindle nose — common where coolant pressure is high.",
            "Z-axis spindle drift from ballnut and bearing wear on heavily used long-bed VTCs.",
        ],
        "controls_paragraph": "Older VTC and VCN ran on [Mazatrol Legacy](/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/); mid-life machines on [Matrix](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/); current VCN-510C, VCN-530C, VCN-700, and VCN-Compact ship on [SmoothG](/spindle-grinding/mazak-spindle-repair/smooth-control/). VTC-800 with SmoothX is the long-bed current platform.",
        "siblings": [
            ("Mazak HCN Horizontal spindles",       "/spindle-grinding/mazak-spindle-repair/hcn-horizontal/"),
            ("Mazak Variaxis 5-Axis spindles",      "/spindle-grinding/mazak-spindle-repair/variaxis/"),
        ],
    },
    "hcn-horizontal": {
        "title":   "Mazak HCN Horizontal Spindle Repair",
        "slug":    "mazak-spindle-hcn-horizontal",
        "subtitle":"HCN Horizontals",
        "url":     "/spindle-grinding/mazak-spindle-repair/hcn-horizontal/",
        "intro":   "HCN horizontal spindles sit oriented differently than their VTC and VCN cousins, and that orientation matters for service patterns. Coolant drainage works in the spindle's favor on horizontals — fluid doesn't pool at the spindle nose the way it can on verticals. But pallet-changer thermal cycling and B-axis indexer loads create different stress patterns. The HCN-8800 and HCN-10800 large platforms see the heaviest production cuts.",
        "failures": [
            "Bearing-pack wear from sustained pallet-changer production cycles on HCN-4000 through HCN-6000.",
            "Larger spindle bearing wear on HCN-8800 and HCN-10800 from heavy axial cuts.",
            "Taper damage from toolholder issues during the high-cycle ATC sequence.",
            "Spindle thermal drift on machines running long-cycle finishing work without spindle warm-up.",
            "Encoder issues from thermal cycling at the pallet-changer interface.",
        ],
        "controls_paragraph": "Mid-2000s HCN runs on [Matrix](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/); current HCN-8800 and HCN-10800 ship on [SmoothX](/spindle-grinding/mazak-spindle-repair/smooth-control/). Legacy PFH and H-series machines run [Mazatrol Legacy](/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/) controls and the spindle parts situation reflects late-life status.",
        "siblings": [
            ("Mazak VTC + VCN spindles",            "/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/"),
            ("Mazak Integrex spindles",             "/spindle-grinding/mazak-spindle-repair/integrex/"),
        ],
    },
    "turning-legacy": {
        "title":   "Mazak Turning Legacy Spindle Repair",
        "slug":    "mazak-spindle-turning-legacy",
        "subtitle":"Slant Turn / Multiplex / Megaturn / HQR",
        "url":     "/spindle-grinding/mazak-spindle-repair/turning-legacy/",
        "intro":   "Mazak's turning legacy spindles — Slant Turn 15/18/20 and Nexus, Multiplex 6000 through 6300, Megaturn vertical turning, HQR-150/200/250, Powermaster — are mechanically sound but increasingly parts-challenged. Bearing-pack rebuilds with current-supply parts are the standard service path; matching OEM bearings is sometimes the time-consuming step. We scope each job based on what's currently sourceable before quoting.",
        "failures": [
            "Bearing-pack wear after decades of production cycles — the most common reason these machines come in.",
            "Taper wear from years of toolholder loading without regular regrinding.",
            "Spindle preload loss from worn drawbar or chuck cylinder components.",
            "Encoder issues on the legacy generation — replacement encoders sometimes require adapter work.",
            "Drive-side issues from older servo amplifiers — increasingly aftermarket-only on the oldest builds.",
        ],
        "controls_paragraph": "Slant Turn, Multiplex 6000, Megaturn, and the original HQR generation ran on [Mazatrol Legacy controls](/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/) — M-Plus and Fusion 640 are the most common pairings. Multiplex 6100 and later moved to [Matrix](/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/). For the legacy generation, spindle service often runs in parallel with parameter backup and battery work because the control side is at the same late-life stage.",
        "siblings": [
            ("Mazak Quick Turn spindles",   "/spindle-grinding/mazak-spindle-repair/quick-turn/"),
            ("Mazak VTC + VCN spindles",    "/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/"),
        ],
    },
}

_MAZAK_SPINDLE_CONTROL_SPOKES = {
    "mazatrol-legacy": {
        "title":   "Spindle Service on Mazatrol Legacy (M-Plus / Fusion 640)",
        "slug":    "mazak-spindle-mazatrol-legacy",
        "subtitle":"Mazatrol Legacy",
        "url":     "/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/",
        "era":     "Roughly 1981 through 2005",
        "intro":   "Legacy Mazatrol controls — M-2, M-32, M-Plus, Fusion 640 — paired with the spindle drive generations from the same era. For spindle service in 2026 on these machines, the conversation is about working with the control's parameter set, capturing the existing configuration before any work, and verifying spindle drive parameters survive battery replacement. The control side is at the same late-life stage as the spindle hardware.",
        "machines_paragraph": "Mazatrol Legacy controls shipped on older [Quick Turn](/spindle-grinding/mazak-spindle-repair/quick-turn/) lathes (pre-Nexus), the [Turning Legacy](/spindle-grinding/mazak-spindle-repair/turning-legacy/) platforms (Slant Turn, Multiplex 6000, Megaturn, HQR original generation), early [Vertical Machining Centers](/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/) (VTC legacy and FJV), and the [HCN horizontals'](/spindle-grinding/mazak-spindle-repair/hcn-horizontal/) PFH and H-series predecessors.",
        "failures": [
            "Spindle parameters lost when memory battery dies — capturing the parameter set is the first step before any spindle work on a legacy control.",
            "Spindle drive amplifier obsolescence — older drives heading toward aftermarket-only supply.",
            "Encoder feedback issues that look like spindle problems but are control-side — diagnostic matters here.",
            "Backup media obsolescence — floppy and PCMCIA on legacy Mazatrol; migrating media is often a companion job to spindle service.",
        ],
        "parts_paragraph": "Legacy spindle drives are increasingly aftermarket-only. Some servo amplifiers are still serviceable through remanufacturing specialists; others have moved to retrofit-only territory. We check parts availability before quoting any spindle work that requires drive-side replacement.",
        "recovery_paragraph": "Before any spindle work on a legacy Mazatrol, we capture the parameter set on whatever media the control supports. Spindle parameters — bearing preload settings, drive tuning, encoder offsets — need to survive battery replacement and any board work. Floppy or PCMCIA media migration to current paths is often part of the same conversation.",
        "siblings": [
            ("Mazatrol Matrix spindle service",   "/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/"),
            ("Mazatrol Smooth spindle service",   "/spindle-grinding/mazak-spindle-repair/smooth-control/"),
        ],
    },
    "mazatrol-matrix": {
        "title":   "Spindle Service on Mazatrol Matrix / Matrix 2",
        "slug":    "mazak-spindle-mazatrol-matrix",
        "subtitle":"Mazatrol Matrix",
        "url":     "/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/",
        "era":     "Roughly 2005 through 2013",
        "intro":   "Matrix and Matrix 2 paired with Mazak's mid-2000s through early-2010s spindle drives — well documented, well supported, and a sweet-spot generation for spindle service. The HDD-to-SSD upgrade on Matrix-1 is a high-ROI companion service when a machine is in for spindle work anyway. Spindle parameters back up cleanly over network on Matrix-2.",
        "machines_paragraph": "Matrix controls shipped on [Quick Turn Nexus](/spindle-grinding/mazak-spindle-repair/quick-turn/) (QTN-100 through QTN-450), original [Integrex](/spindle-grinding/mazak-spindle-repair/integrex/) i-series, [VTC and VCN](/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/) production verticals (VTC-200 through VTC-800, VCN-410 through VCN-530), [HCN-4000 through HCN-6000](/spindle-grinding/mazak-spindle-repair/hcn-horizontal/), and the [Multiplex 6100](/spindle-grinding/mazak-spindle-repair/turning-legacy/) generation.",
        "failures": [
            "HDD failure on Matrix-1 — companion SSD upgrade is high-ROI when the machine is already in for spindle work.",
            "Spindle drive faults from the αi-generation drives paired with this control — generally still well supported.",
            "MMC board faults that affect spindle programming and diagnostics.",
            "Touchscreen drift impacting spindle setup workflow.",
        ],
        "parts_paragraph": "Matrix-2 spindle drives and control boards are fully supported through OEM and authorized channels. Matrix-1 is heading toward late-life status but still serviceable. Spindle drive amplifiers from this generation are well documented and parts availability is generally good.",
        "recovery_paragraph": "Matrix supports clean parameter backup over CF card or USB. Before any spindle work, we back up the spindle-related parameters (preload, drive tuning, encoder offsets) along with the full machine parameter set. The SSD upgrade on Matrix-1 is the highest-value preventive service item — combining it with scheduled spindle work eliminates a future return trip.",
        "siblings": [
            ("Mazatrol Legacy spindle service",   "/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/"),
            ("Mazatrol Smooth spindle service",   "/spindle-grinding/mazak-spindle-repair/smooth-control/"),
        ],
    },
    "smooth-control": {
        "title":   "Spindle Service on Mazatrol Smooth (SmoothX / G / Ai)",
        "slug":    "mazak-spindle-smooth-control",
        "subtitle":"Mazatrol Smooth",
        "url":     "/spindle-grinding/mazak-spindle-repair/smooth-control/",
        "era":     "2013 through present",
        "intro":   "Smooth-generation Mazak machines have modern spindle drives — αii-class on most current platforms — and clean parameter backup workflows over network. Spindle service on Smooth-equipped machines is mostly about the spindle hardware itself; the control side adds network-based parameter management, MTConnect integration for spindle monitoring, and the diagnostic visibility the platform provides.",
        "machines_paragraph": "Smooth ships on current [Integrex](/spindle-grinding/mazak-spindle-repair/integrex/) (i-H, i-V, e-V/10), current [Variaxis](/spindle-grinding/mazak-spindle-repair/variaxis/) i-series, [VTC-800 and current VCN](/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/), current [HCN-8800 and HCN-10800](/spindle-grinding/mazak-spindle-repair/hcn-horizontal/), and current [Quick Turn](/spindle-grinding/mazak-spindle-repair/quick-turn/) Compact, Smart, Primos, Ez, and Ultra.",
        "failures": [
            "Spindle parameter backup discipline — Smooth controls store more parameters than legacy generations and a clean backup process matters.",
            "Network configuration drift after a shop network change can affect spindle monitoring integration.",
            "MTConnect setup issues on machines integrated with shop-floor monitoring.",
            "Spindle drive faults rare given the modernity of the platform — most current-generation work is preventive.",
        ],
        "parts_paragraph": "Smooth-generation spindle drives and control parts are fully current through OEM channels. Parts availability is not a constraint on this generation.",
        "recovery_paragraph": "Network-based parameter backup is the standard workflow on Smooth. Before any spindle work we capture the full parameter set over the network, document spindle-specific parameters (preload, drive tuning, encoder offsets, MTConnect integration), and verify the restore at sign-off. The newer the machine, the more parameters there are to manage — backup discipline scales with control generation.",
        "siblings": [
            ("Mazatrol Matrix spindle service",   "/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/"),
            ("Mazatrol Legacy spindle service",   "/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/"),
        ],
    },
}

# ============================================================
# HAAS SPINDLE
# ============================================================
_HAAS_SPINDLE_SERIES_SPOKES = {
    "vf-series": {
        "title":   "Haas VF Series Spindle Repair",
        "slug":    "haas-spindle-vf-series",
        "subtitle":"VF Series Vertical Mills",
        "url":     "/spindle-grinding/haas-spindle-repair/vf-series/",
        "intro":   "VF series spindles are the most common Haas spindles we see — VF-1 through VF-12 plus the YT extended-Y and SS super-speed builds. Haas uses different spindle types across the VF range: the base VF machines have moderate-RPM cartridge spindles; the SS variants have higher-RPM bearing packs that show different wear patterns under sustained production. After-spindle balance verification is a routine part of every rebuild.",
        "failures": [
            "Bearing-pack wear on SS variants from sustained high-RPM production — primary failure mode on super-speed builds.",
            "Taper damage from a tool change failure or crash — common reason VFs come in.",
            "Front bearing wear on machines running heavy aluminum work without spindle warm-up.",
            "Drawbar pull-force loss over time — affects toolholder retention and downstream spindle health.",
            "Coolant intrusion at the spindle nose on high-coolant production work.",
        ],
        "controls_paragraph": "VF machines from the early 2000s through 2014 run on [Haas Classic Control](/spindle-grinding/haas-spindle-repair/haas-classic-control/); 2014-and-later VF builds ship on [Haas Next Generation Control (NGC)](/spindle-grinding/haas-spindle-repair/haas-ngc/). Spindle drive parameters back up via the Haas standard parameter export — same workflow on Classic and NGC, just different media paths.",
        "siblings": [
            ("Haas UMC Series spindles",  "/spindle-grinding/haas-spindle-repair/umc-series/"),
            ("Haas ST Series spindles",   "/spindle-grinding/haas-spindle-repair/st-series/"),
        ],
    },
    "st-series": {
        "title":   "Haas ST Series Spindle Repair",
        "slug":    "haas-spindle-st-series",
        "subtitle":"ST Series Lathes",
        "url":     "/spindle-grinding/haas-spindle-repair/st-series/",
        "intro":   "ST series lathe spindles span ST-10 through ST-55 with SSY Y-axis variants and the DS-30 dual-spindle. The line uses cartridge-style turning spindles with different bearing arrangements per size class. ST-10 and ST-20 chuckers see high-cycle bar work that wears the front bearings; ST-30 and larger see heavier axial cuts. DS-30 sub-spindles add synchronization verification after any sub-spindle service.",
        "failures": [
            "Front bearing wear on ST-10 and ST-20 from sustained bar-feed production.",
            "Chuck cylinder leaks affecting spindle preload — common cause of downstream bearing failure.",
            "Sub-spindle alignment drift on DS-30 dual-spindle — requires synchronization verification after any spindle work.",
            "Larger spindle bearing wear on ST-40 and ST-50 from heavy axial cuts.",
            "Draw-tube wear on high-cycle bar production over years of cycle count.",
        ],
        "controls_paragraph": "Older ST machines run on [Haas Classic Control](/spindle-grinding/haas-spindle-repair/haas-classic-control/); current ST-10 through ST-55 ship on [NGC](/spindle-grinding/haas-spindle-repair/haas-ngc/). DS-30 builds are typically on NGC by now; older DS-30s on Classic.",
        "siblings": [
            ("Haas VF Series spindles",       "/spindle-grinding/haas-spindle-repair/vf-series/"),
            ("Haas Toolroom Lathe spindles",  "/spindle-grinding/haas-spindle-repair/toolroom-lathes/"),
        ],
    },
    "umc-series": {
        "title":   "Haas UMC Series Spindle Repair",
        "slug":    "haas-spindle-umc-series",
        "subtitle":"UMC Universal 5-Axis",
        "url":     "/spindle-grinding/haas-spindle-repair/umc-series/",
        "intro":   "UMC spindles are 5-axis trunnion-table machines — UMC-350 through UMC-1600 with SS variants on several sizes. The work is 5-axis finishing where tool-tip accuracy depends on spindle geometry staying tight to the trunnion centerline. Post-rebuild RTCP verification is part of every spindle service on this platform — we don't hand back a UMC spindle without confirming kinematic accuracy.",
        "failures": [
            "Bearing-pack wear under sustained high-RPM 5-axis finishing cuts — primary failure mode on UMC.",
            "Taper damage from toolholder failure or crash during multi-axis cuts.",
            "Spindle thermal drift impacting kinematic accuracy on long-cycle 5-axis work.",
            "Coolant intrusion at the spindle nose on heavy-coolant aluminum production.",
            "RTCP and kinematic drift after spindle work — full re-verification required.",
        ],
        "controls_paragraph": "All UMC machines ship on [Haas NGC](/spindle-grinding/haas-spindle-repair/haas-ngc/) — Classic Control never made it to the UMC line. NGC's kinematic compensation framework is what makes the 5-axis RTCP verification straightforward post-rebuild.",
        "siblings": [
            ("Haas VF Series spindles",  "/spindle-grinding/haas-spindle-repair/vf-series/"),
            ("Haas EC Series spindles",  "/spindle-grinding/haas-spindle-repair/ec-series/"),
        ],
    },
    "ec-series": {
        "title":   "Haas EC Series Horizontal Spindle Repair",
        "slug":    "haas-spindle-ec-series",
        "subtitle":"EC Series Horizontals",
        "url":     "/spindle-grinding/haas-spindle-repair/ec-series/",
        "intro":   "EC horizontal spindles — EC-300 through EC-3000 production horizontals plus the PP pallet-pool builds — sit oriented for chip drainage to work in the spindle's favor. The wear patterns are pallet-changer-cycle-driven: machines running heavy pallet rotation see different bearing wear than those running long single-pallet cycles. The EC-1600 and larger see the heaviest axial production cuts.",
        "failures": [
            "Bearing-pack wear from sustained pallet-changer production on EC-300 through EC-500.",
            "Larger spindle bearing wear on EC-1600 and EC-2000 from heavy axial cuts.",
            "Spindle thermal cycling from pallet rotation affecting bearing-pack life.",
            "Taper damage from toolholder issues during high-cycle ATC sequences.",
            "Drawbar wear on high-cycle production over years of use.",
        ],
        "controls_paragraph": "Older EC machines run on [Haas Classic Control](/spindle-grinding/haas-spindle-repair/haas-classic-control/); current EC-500, EC-550, and EC-1600/2000/3000 builds ship on [NGC](/spindle-grinding/haas-spindle-repair/haas-ngc/).",
        "siblings": [
            ("Haas VF Series spindles",     "/spindle-grinding/haas-spindle-repair/vf-series/"),
            ("Haas UMC Series spindles",    "/spindle-grinding/haas-spindle-repair/umc-series/"),
        ],
    },
    "mini-mill-toolroom": {
        "title":   "Haas Mini Mill, Toolroom, DT, DM, VM Spindle Repair",
        "slug":    "haas-spindle-mini-mill-toolroom",
        "subtitle":"Mini Mill / Toolroom / DT / DM / VM",
        "url":     "/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/",
        "intro":   "The compact and toolroom families have different spindles based on intended use. Mini Mill spindles are moderate-RPM general-purpose; DT (drill-tap) spindles see high-cycle tapping with specific wear patterns; DM (drill-mill) and VM (mold-mill) spindles are higher-RPM for finishing work. The wear profile tracks how the machine is actually used in the shop more than how Haas spec'd it.",
        "failures": [
            "High-cycle DT spindle bearing wear from sustained drill-tap production — primary failure mode on this sub-family.",
            "Mini Mill spindle wear from general-purpose production over years.",
            "Higher-RPM DM and VM spindle bearing wear from sustained mold-finishing work.",
            "Draw-bar pull-force loss on high-cycle toolroom work.",
            "Spindle thermal issues on machines running long cycles without warm-up.",
        ],
        "controls_paragraph": "Most of this family ran on [Haas Classic Control](/spindle-grinding/haas-spindle-repair/haas-classic-control/) through 2014; newer DT, DM, and Super Mini Mill 2 builds ship on [NGC](/spindle-grinding/haas-spindle-repair/haas-ngc/). Older TM toolroom mills with Classic panels may need parameter migration as part of spindle service.",
        "siblings": [
            ("Haas VF Series spindles",        "/spindle-grinding/haas-spindle-repair/vf-series/"),
            ("Haas Toolroom Lathe spindles",   "/spindle-grinding/haas-spindle-repair/toolroom-lathes/"),
        ],
    },
    "toolroom-lathes": {
        "title":   "Haas Toolroom Lathe Spindle Repair (TL / CL)",
        "slug":    "haas-spindle-toolroom-lathes",
        "subtitle":"TL and CL Toolroom Lathes",
        "url":     "/spindle-grinding/haas-spindle-repair/toolroom-lathes/",
        "intro":   "Toolroom lathe spindles — TL-1 through TL-4 and CL-1 — bridge manual-style turning and production CNC. The spindles are designed for moderate use but get pushed into production-style cycles in many shops. Wear patterns reflect the actual usage rather than the toolroom intent: machines running production see bearing wear similar to ST chuckers; machines used as actual toolroom lathes see more taper wear from frequent toolholder changes.",
        "failures": [
            "Front bearing wear on TL machines used in production-style cycles.",
            "Taper wear from frequent toolholder changes in toolroom-style use.",
            "Spindle preload loss from chuck or collet hardware wear.",
            "Drive-side issues on heavier production TL-3 and TL-4 machines.",
        ],
        "controls_paragraph": "TL machines ran on [Haas Classic Control](/spindle-grinding/haas-spindle-repair/haas-classic-control/) through 2014; current TL and CL-1 ship on [NGC](/spindle-grinding/haas-spindle-repair/haas-ngc/).",
        "siblings": [
            ("Haas ST Series spindles",        "/spindle-grinding/haas-spindle-repair/st-series/"),
            ("Haas Mini Mill / Toolroom",      "/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/"),
        ],
    },
}

_HAAS_SPINDLE_CONTROL_SPOKES = {
    "haas-classic-control": {
        "title":   "Spindle Service on Haas Classic Control (Pre-NGC)",
        "slug":    "haas-spindle-haas-classic-control",
        "subtitle":"Haas Classic Control",
        "url":     "/spindle-grinding/haas-spindle-repair/haas-classic-control/",
        "era":     "Through roughly 2014",
        "intro":   "Haas Classic Control paired with the pre-NGC spindle drive generation. For spindle service in 2026 on these machines, the conversation includes capturing parameters before any battery or board work, working with the documented Haas spindle-parameter set, and verifying drive tuning survives any control-side service. The control side is well documented but heading toward late-life status.",
        "machines_paragraph": "Classic Control shipped on the early-2000s through 2014 Haas fleet — original [VF Series](/spindle-grinding/haas-spindle-repair/vf-series/), [ST Series](/spindle-grinding/haas-spindle-repair/st-series/) lathes, [EC Series](/spindle-grinding/haas-spindle-repair/ec-series/) horizontals, original [Mini Mill, TM Toolroom, and DT/DM](/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/) machines, and [TL Toolroom Lathes](/spindle-grinding/haas-spindle-repair/toolroom-lathes/). UMC machines never shipped on Classic.",
        "failures": [
            "Spindle parameters lost when memory battery dies on a powered-down control — capture before any battery work.",
            "MOCON board faults that can present as spindle drive issues — diagnostic matters here.",
            "Drive amplifier faults on heavy production work — generally still serviceable through Haas channels.",
            "Spindle drive parameter access through the older Classic interface — workflow is different from NGC.",
        ],
        "parts_paragraph": "Haas Classic spindle drive parts are still available through Haas channels for most board-level items, though the supply chain is thinning as NGC matures. Aftermarket and remanufactured boards are increasingly the path on the oldest Classic builds.",
        "recovery_paragraph": "Before any spindle work on a Classic Control machine, we capture the parameter set via the standard Haas parameter export. Spindle-specific parameters (drive tuning, encoder offsets, preload settings) go into the documented set. For machines on Haas-authorized Classic-to-NGC upgrade paths, the spindle parameter migration is part of that conversation.",
        "siblings": [
            ("Haas Next Generation Control (NGC) spindle service", "/spindle-grinding/haas-spindle-repair/haas-ngc/"),
        ],
    },
    "haas-ngc": {
        "title":   "Spindle Service on Haas Next Generation Control (NGC)",
        "slug":    "haas-spindle-haas-ngc",
        "subtitle":"Haas NGC",
        "url":     "/spindle-grinding/haas-spindle-repair/haas-ngc/",
        "era":     "2014 to present",
        "intro":   "NGC paired with Haas's current spindle drive generation — fully supported, well documented, and easy to work with for spindle service. Parameter backup is network or USB based, the diagnostic visibility into spindle drive parameters is good, and MyHaas integration for spindle monitoring is straightforward. Most NGC spindle service work is the spindle hardware itself; the control side is rarely the bottleneck.",
        "machines_paragraph": "NGC ships on every current Haas machine — [VF Series](/spindle-grinding/haas-spindle-repair/vf-series/), [ST Series](/spindle-grinding/haas-spindle-repair/st-series/), all [UMC](/spindle-grinding/haas-spindle-repair/umc-series/) 5-axis machines, [EC Series](/spindle-grinding/haas-spindle-repair/ec-series/) horizontals, current [Mini Mill, DT, DM](/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/), and [TL/CL Toolroom Lathes](/spindle-grinding/haas-spindle-repair/toolroom-lathes/).",
        "failures": [
            "Parameter backup discipline — NGC stores more spindle parameters than Classic and a clean backup process matters.",
            "Network configuration affecting MyHaas spindle monitoring after a shop network change.",
            "SSD-related boot issues on early NGC builds that can affect spindle program loading.",
            "Touchscreen calibration drift impacting spindle setup workflow on heavily used machines.",
        ],
        "parts_paragraph": "NGC parts and current Haas spindle drives are fully supported through Haas channels.",
        "recovery_paragraph": "NGC's parameter backup workflow over network and USB is the standard path. Before any spindle work we capture the spindle-specific parameter set (drive tuning, encoder offsets, preload settings, MyHaas integration), document the existing configuration, and verify the restore at sign-off.",
        "siblings": [
            ("Haas Classic Control spindle service", "/spindle-grinding/haas-spindle-repair/haas-classic-control/"),
        ],
    },
}


# ============================================================
# DMG MORI SPINDLE
# ============================================================
def _dmg_spindle_series(slug, title_suffix, subtitle, intro, failures, controls, siblings):
    """Compact builder for DMG Mori series spokes — common boilerplate."""
    return {
        "title":   f"DMG Mori {title_suffix} Spindle Repair",
        "slug":    f"dmg-mori-spindle-{slug}",
        "subtitle":subtitle,
        "url":     f"/spindle-grinding/dmg-mori-spindle-repair/{slug}/",
        "intro":   intro,
        "failures":failures,
        "controls_paragraph": controls,
        "siblings":siblings,
    }


_DMG_MORI_SPINDLE_SERIES_SPOKES = {
    "nlx-turning": _dmg_spindle_series(
        "nlx-turning", "NLX / ALX Universal Turning", "NLX / ALX",
        "NLX and ALX universal-turning spindles span the broadest range in the DMG Mori lineup — entry NLX-1500 chuckers through large NLX-6000 long-bed turning, plus the ALX family. The spindles use cartridge-style designs across the line with bearing arrangements scaled to spindle size. Sub-spindle synchronization verification is part of any spindle work on SY/SMC twin-spindle configurations.",
        [
            "Front bearing wear under sustained bar-feed production on smaller NLX builds.",
            "Larger spindle bearing wear on NLX-6000 long-bed from heavy axial cuts.",
            "Sub-spindle synchronization drift on SY and SMC twin-spindle configurations — requires verification after rebuild.",
            "Live-tool spindle wear on the MY and SY mill-turn variants.",
            "Spindle preload loss from chuck cylinder leaks affecting downstream bearing life.",
        ],
        "NLX and ALX ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under the [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/) HMI. Spindle drive tuning happens at the Siemens 840D layer; CELOS handles the operator workflow around the underlying control.",
        [
            ("DMG Mori CTX / CLX spindles",  "/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/"),
            ("DMG Mori NTX spindles",         "/spindle-grinding/dmg-mori-spindle-repair/ntx/"),
        ],
    ),
    "ctx-clx-turning": _dmg_spindle_series(
        "ctx-clx-turning", "CTX / CLX Turning + TC", "CTX / CLX (incl. TC variants)",
        "CTX and CLX turning spindles cover entry CLX 350/450/550 through CTX 850 universal turning, plus the TC turn-mill builds (CTX Beta 800 TC, Beta 1250 TC, Gamma 2000/3000 TC). The TC variants add a B-axis milling spindle alongside the turning spindle — the B-axis becomes the high-stress component on multitasking work. Mill-turn alignment matters more here than on straight CTX turning.",
        [
            "B-axis milling spindle bearing wear on TC variants — primary failure mode on multitasking CTX configurations.",
            "Turning spindle wear under heavy axial cuts on long-bed CTX 650 and CTX 850.",
            "Lower turret wear on twin-turret configurations affecting spindle-side alignment.",
            "Tailstock alignment drift impacting spindle-side cuts on long-bed builds.",
            "Hydraulic chuck preload issues affecting spindle bearing life.",
        ],
        "CTX and CLX ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/). TC variants with the added B-axis put more spindle parameter configuration on the Siemens 840D layer.",
        [
            ("DMG Mori NLX / ALX spindles",  "/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/"),
            ("DMG Mori NTX spindles",         "/spindle-grinding/dmg-mori-spindle-repair/ntx/"),
        ],
    ),
    "ntx": _dmg_spindle_series(
        "ntx", "NTX Integrated Mill-Turn", "NTX Mill-Turn",
        "NTX integrated mill-turn machines run two high-capability spindles each: a turning spindle in the headstock and a full B-axis milling spindle in the upper-tooling. The milling spindle is the highest-stress component on these platforms because it sees axial, lateral, and angular cuts at varying loads. After-spindle B-axis kinematic verification is mandatory — multitasking tolerances depend on it.",
        [
            "B-axis milling spindle bearing-pack wear from sustained mill-turn production — primary failure mode on NTX.",
            "Turning spindle bearing wear under heavy axial loads on NTX 3000 and NTX 4000.",
            "Sub-spindle synchronization drift on multi-tasking part-transfer work.",
            "Spindle thermal cycling from long-cycle multitasking parts affecting bearing-pack life.",
            "Spindle drive faults from sustained heavy cuts on the larger NTX builds.",
        ],
        "NTX ships on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/). The B-axis spindle kinematics need full re-verification after any milling-spindle service.",
        [
            ("DMG Mori CTX / CLX spindles",  "/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/"),
            ("DMG Mori DMU / DMC spindles",  "/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/"),
        ],
    ),
    "dmu-dmc": _dmg_spindle_series(
        "dmu-dmc", "DMU / DMC 5-Axis", "DMU / DMC 5-Axis",
        "DMU and DMC 5-axis spindles are the high-end of the DMG Mori vertical lineup — DMU 50 through DMU 340 trunnion-table machines, plus monoBLOCK and duoBLOCK builds, the DMU eVo, and DMC universal variants. Most see aerospace and mold-die finishing work where bearing pack precision is critical. RTCP and trunnion kinematic verification after spindle work is mandatory on these platforms.",
        [
            "Bearing pack wear from sustained high-RPM 5-axis finishing — primary failure mode on DMU.",
            "Swivel head spindle bearing wear on monoBLOCK builds.",
            "Taper damage from toolholder failure during 5-axis cuts.",
            "Coolant intrusion at the spindle nose on heavy-coolant aluminum production.",
            "RTCP and kinematic drift after spindle work — full re-calibration required as part of the rebuild.",
        ],
        "DMU machines mostly ship on [Heidenhain TNC](/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/) (iTNC 530 on legacy, TNC 640 on current). DMC builds typically ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/). All run under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/). Spindle parameter sets differ meaningfully between Siemens and Heidenhain — diagnostic and recovery procedures match the underlying control.",
        [
            ("DMG Mori NHX / NH spindles",  "/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/"),
            ("DMG Mori NVX / NV spindles",  "/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/"),
        ],
    ),
    "nhx-horizontals": _dmg_spindle_series(
        "nhx-horizontals", "NHX / NH Horizontal", "NHX / NH Horizontals",
        "NHX and the legacy NH horizontal spindles sit oriented for chip drainage to work in the spindle's favor — NHX 4000 through 10000 plus the older NH 4000/5000/6300. The platform's pallet-changer cycle creates thermal patterns at the spindle that drive specific wear. The larger NHX-8000 and 10000 see heavy axial cuts and bigger spindle bearings to match.",
        [
            "Bearing-pack wear from sustained pallet-changer production cycles.",
            "Larger spindle bearing wear on NHX-8000 and NHX-10000 under heavy axial cuts.",
            "Spindle thermal cycling from pallet rotation affecting bearing-pack life.",
            "Taper damage from toolholder issues during pallet-cycle ATC sequences.",
            "Spindle drive faults on heavier production cuts.",
        ],
        "NHX and NH ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/).",
        [
            ("DMG Mori DMU / DMC spindles",  "/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/"),
            ("DMG Mori NVX / NV spindles",   "/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/"),
        ],
    ),
    "nvx-verticals": _dmg_spindle_series(
        "nvx-verticals", "NVX / NV / NVD Vertical", "NVX / NV / NVD Verticals",
        "NVX is DMG Mori's high-end vertical lineup — NVX 4000 through 7000 production verticals, plus the older NV 4000 and NV 5000, and NVD with DCG (Driven at the Center of Gravity) construction for high-acceleration work. Spindle wear patterns track the build class: NVX-5060 high-RPM machines wear differently than NVX-7000 large-envelope machines.",
        [
            "High-RPM spindle bearing failure on NVX-5060 from sustained aluminum aerospace work.",
            "Larger spindle bearing wear on NVX-7000 from heavy axial cuts.",
            "Spindle thermal drift on long-cycle finishing work.",
            "Taper damage from toolholder issues during high-cycle ATC sequences.",
            "DCG-related spindle bearing patterns on NVD builds.",
        ],
        "NVX, NV, and NVD ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/).",
        [
            ("DMG Mori DMU / DMC spindles",     "/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/"),
            ("DMG Mori NHX / NH spindles",      "/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/"),
        ],
    ),
    "cmx": _dmg_spindle_series(
        "cmx", "CMX / CMX U", "CMX Entry & 5-Sided",
        "CMX spindles are the entry-production end of the DMG Mori lineup — CMX 600V through 1300V verticals, CMX 50U and 70U 5-axis universals, the CMX 320V compact. The platform is built for accessibility and cost; spindle wear patterns in heavy-use environments outpace the higher-end DMU and NVX machines because the bearing-pack design is lighter-duty.",
        [
            "Bearing wear from sustained production cycles in busy shop environments.",
            "Spindle thermal issues on machines pushed to upper RPM limits.",
            "Taper damage from toolholder issues during high-cycle production.",
            "Coolant intrusion at the spindle nose on high-coolant work.",
        ],
        "CMX machines ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/).",
        [
            ("DMG Mori DMU / DMC spindles",       "/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/"),
            ("DMG Mori DMP / Milltap spindles",   "/spindle-grinding/dmg-mori-spindle-repair/dmp-milltap/"),
        ],
    ),
    "dmp-milltap": _dmg_spindle_series(
        "dmp-milltap", "DMP / Milltap Compact Production", "DMP / Milltap",
        "DMP and Milltap compact production spindles run in the highest-cycle environment in the DMG Mori lineup — DMP 35 through 70 small-part drill-tap, dual-spindle DMP 500, Milltap 700. The spindles are built for high cycle counts but the wear pattern tracks the cycle count: short-cycle drill-tap production grinds through bearing-pack life faster than longer-cycle work.",
        [
            "High-cycle bearing-pack wear from sustained drill-tap production.",
            "Spindle bearing failure on high-RPM, short-cycle use.",
            "Tool-changer thermal cycling affecting spindle nose alignment.",
            "Drawbar wear from extremely high cycle counts.",
        ],
        "DMP and Milltap ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/).",
        [
            ("DMG Mori CMX spindles",          "/spindle-grinding/dmg-mori-spindle-repair/cmx/"),
            ("DMG Mori NVX / NV spindles",     "/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/"),
        ],
    ),
    "sprint-multisprint": _dmg_spindle_series(
        "sprint-multisprint", "SPRINT / MULTISPRINT Swiss", "SPRINT / MULTISPRINT",
        "SPRINT and MULTISPRINT spindles are Swiss-type production turning — SPRINT 20/32/50/65 and MULTISPRINT 25/36. Swiss-type spindle service has its own patterns: guide bushing wear interacts with spindle service in ways straight turning doesn't, and the sub-spindle synchronization on twin-spindle Swiss platforms requires careful verification after any spindle work.",
        [
            "Guide bushing wear interacting with spindle service — the two are often companion jobs.",
            "Sub-spindle synchronization drift on twin-spindle Swiss configurations.",
            "Bar feeder synchronization issues affecting spindle-side cuts.",
            "Spindle preload loss from chuck or collet hardware on high-cycle bar work.",
        ],
        "SPRINT and MULTISPRINT ship on [Siemens 840D](/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/) under [CELOS](/spindle-grinding/dmg-mori-spindle-repair/celos/).",
        [
            ("DMG Mori NLX / ALX spindles",   "/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/"),
            ("DMG Mori CTX / CLX spindles",   "/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/"),
        ],
    ),
}

_DMG_MORI_SPINDLE_CONTROL_SPOKES = {
    "siemens-840d": {
        "title":   "Spindle Service on Siemens 840D (DMG Mori)",
        "slug":    "dmg-mori-spindle-siemens-840d",
        "subtitle":"Siemens 840D",
        "url":     "/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/",
        "era":     "Late 1990s through present (solutionline current)",
        "intro":   "Siemens 840D is where DMG Mori spindle parameters live for the majority of the lineup. Spindle drive tuning, encoder configuration, and machine-data parameters are managed at the 840D layer; CELOS handles the operator workflow on top. Before any spindle work we capture the parameter set via the Siemens-standard backup path. Original 840D (non-solutionline) is at late-life status for control hardware; solutionline is fully current.",
        "machines_paragraph": "840D ships on most of the DMG Mori lineup — [NLX/ALX](/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/), [CTX/CLX](/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/), [NTX](/spindle-grinding/dmg-mori-spindle-repair/ntx/), [NHX/NH](/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/), [NVX/NV/NVD](/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/), [CMX](/spindle-grinding/dmg-mori-spindle-repair/cmx/), [DMP/Milltap](/spindle-grinding/dmg-mori-spindle-repair/dmp-milltap/), [SPRINT/MULTISPRINT](/spindle-grinding/dmg-mori-spindle-repair/sprint-multisprint/), and the [DMC](/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/) variants.",
        "failures": [
            "Spindle parameters lost when memory battery dies on a powered-down 840D PCU.",
            "Spindle drive amplifier faults on older builds — original 840D drives heading toward late-life.",
            "MMC failures on original 840D affecting spindle programming and diagnostic visibility.",
            "Encoder feedback issues at the 840D layer that can present as spindle problems.",
        ],
        "parts_paragraph": "Siemens 840D spindle drives are well supported through Siemens and authorized service partners on solutionline. Original 840D (non-sl) drives are heading toward aftermarket and remanufactured-only over the next several years.",
        "recovery_paragraph": "Spindle parameter backup on 840D is documented Siemens procedure — back up via the operator panel before any battery or board work. Spindle-specific parameters (drive tuning, encoder offsets, preload settings) go into the standard backup set.",
        "siblings": [
            ("Heidenhain TNC spindle service",  "/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/"),
            ("CELOS spindle workflow",          "/spindle-grinding/dmg-mori-spindle-repair/celos/"),
        ],
    },
    "heidenhain-tnc": {
        "title":   "Spindle Service on Heidenhain TNC (DMG Mori)",
        "slug":    "dmg-mori-spindle-heidenhain-tnc",
        "subtitle":"Heidenhain TNC",
        "url":     "/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/",
        "era":     "iTNC 530 from ~2001, TNC 640 from 2012",
        "intro":   "Heidenhain TNC is the common control on DMG Mori's DMU and DMC 5-axis lines — iTNC 530 on legacy builds, TNC 640 on current. Spindle parameters and drive tuning on TNC are managed differently from Siemens, and the workflow for kinematic verification after 5-axis spindle work uses Heidenhain's documented procedures. Most DMU spindle service routes through this control.",
        "machines_paragraph": "Heidenhain TNC ships on the [DMU/DMC](/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/) 5-axis family — DMU 50 through DMU 340, monoBLOCK and duoBLOCK builds, DMU eVo, and the DMC universals. Most of the high-end DMG Mori 5-axis spindle work runs on this control.",
        "failures": [
            "Keypad failure affecting spindle setup workflow — most common single failure on iTNC 530.",
            "Encoder drift on rotary-axis encoders for trunnion machines affecting RTCP after spindle work.",
            "MC (Main Computer) board faults on older iTNC 530.",
            "Memory battery loss affecting spindle and machine parameters.",
        ],
        "parts_paragraph": "Heidenhain TNC parts are well supported through Heidenhain and authorized service partners. iTNC 530 is heading toward late-life; TNC 640 is fully current.",
        "recovery_paragraph": "Heidenhain TNC spindle parameter backup is well documented — back up to network or USB before any work. Tool tables and spindle-specific parameters (drive tuning, encoder offsets) go into the standard backup. After spindle work on a DMU 5-axis machine, we run the documented kinematic verification before sign-off.",
        "siblings": [
            ("Siemens 840D spindle service",  "/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/"),
            ("CELOS spindle workflow",        "/spindle-grinding/dmg-mori-spindle-repair/celos/"),
        ],
    },
    "celos": {
        "title":   "CELOS Spindle Workflow on DMG Mori",
        "slug":    "dmg-mori-spindle-celos",
        "subtitle":"CELOS HMI Layer",
        "url":     "/spindle-grinding/dmg-mori-spindle-repair/celos/",
        "era":     "CELOS from 2014, CELOS X current",
        "intro":   "CELOS is the DMG Mori operator-facing layer that sits on top of Siemens 840D or Heidenhain TNC. For spindle service, CELOS is mostly relevant on the workflow side — job preparation, parameter backup automation, integration with shop-floor monitoring of spindle metrics. The actual spindle parameters live in the underlying control; CELOS provides the visibility and the integration points.",
        "machines_paragraph": "CELOS runs on every current DMG Mori machine — every [NLX/ALX](/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/), [CTX/CLX](/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/), [NTX](/spindle-grinding/dmg-mori-spindle-repair/ntx/), [DMU/DMC](/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/), [NHX/NH](/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/), [NVX/NV/NVD](/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/), [CMX](/spindle-grinding/dmg-mori-spindle-repair/cmx/), [DMP/Milltap](/spindle-grinding/dmg-mori-spindle-repair/dmp-milltap/), and [SPRINT/MULTISPRINT](/spindle-grinding/dmg-mori-spindle-repair/sprint-multisprint/) machines.",
        "failures": [
            "IPC reliability on older CELOS hardware — boot drive and fan issues.",
            "Network configuration drift affecting spindle monitoring integration.",
            "MTConnect/OPC UA setup for shop-floor spindle metric integration.",
            "App integration issues with shop-floor monitoring systems.",
        ],
        "parts_paragraph": "CELOS IPC hardware is fully supported through DMG Mori. The control underneath (Siemens or Heidenhain) follows its own parts lifecycle.",
        "recovery_paragraph": "CELOS configuration backup is part of the standard DMG Mori service workflow. Spindle monitoring integration (MTConnect/OPC UA), CELOS apps, and the workflow configuration get documented before any service work.",
        "siblings": [
            ("Siemens 840D spindle service",     "/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/"),
            ("Heidenhain TNC spindle service",   "/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/"),
        ],
    },
}


# ============================================================
# DOOSAN SPINDLE — controls cross-link to Fanuc spindle spokes
# ============================================================
def _doosan_spindle_series(slug, title_suffix, subtitle, intro, failures, controls, siblings):
    return {
        "title":   f"Doosan {title_suffix} Spindle Repair",
        "slug":    f"doosan-spindle-{slug}",
        "subtitle":subtitle,
        "url":     f"/spindle-grinding/doosan-spindle-repair/{slug}/",
        "intro":   intro,
        "failures":failures,
        "controls_paragraph": controls,
        "siblings":siblings,
    }


_DOOSAN_SPINDLE_SERIES_SPOKES = {
    "puma": _doosan_spindle_series(
        "puma", "Puma Horizontal Turning", "Puma Horizontal Turning",
        "Puma horizontal-turning spindles are the most common Doosan spindles we see — Puma 230 through Puma 800 with M/MS/LM/LY/Y/SY/SY II configuration variants, plus the heavier 4100, 5100, 700, and 800 builds, the GT compact lineup, and the TT twin-turret builds. The spindle types scale with size class: smaller Puma 1500/2000 use lighter cartridges; Puma 4100 and 5100 have heavier-duty bearing arrangements.",
        [
            "Front bearing wear under sustained bar-feed production on smaller Puma builds.",
            "Larger spindle bearing wear on Puma 4100/5100 from heavy axial cuts.",
            "Sub-spindle synchronization drift on SY twin-spindle configurations.",
            "Chuck cylinder leaks affecting spindle preload on high-cycle bar work.",
            "Spindle preload loss from draw-tube wear over years of cycle count.",
        ],
        "Most Puma builds ship on Fanuc — entry and mid-range on [Fanuc 0i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-0i/) (typically 0i-D or 0i-F), and higher-end Puma 2600SY, 3100, 4100, 5100, 700, and 800 on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/).",
        [
            ("Doosan Puma MX / SMX spindles",  "/spindle-grinding/doosan-spindle-repair/puma-mx-smx/"),
            ("Doosan Lynx spindles",            "/spindle-grinding/doosan-spindle-repair/lynx/"),
        ],
    ),
    "puma-mx-smx": _doosan_spindle_series(
        "puma-mx-smx", "Puma MX / SMX Multitasking", "Puma MX / SMX",
        "Puma MX and SMX mill-turn spindles add a B-axis milling spindle to the turning chassis — MX 1600 through MX 3100 with T/ST/SY variants, and the newer SMX 2100/2600/3100. The B-axis milling spindle is the high-stress component on these platforms because it sees mill-turn loads at varying angles. Post-rebuild B-axis kinematic verification is mandatory.",
        [
            "B-axis milling spindle bearing-pack wear from sustained mill-turn production — primary failure mode.",
            "Turning spindle bearing wear under heavy axial cuts.",
            "Lower turret spindle issues on twin-turret configurations.",
            "Sub-spindle synchronization drift on multi-axis transfer work.",
            "B-axis kinematic drift after spindle work — full re-verification required.",
        ],
        "Puma MX and SMX ship on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/) — typically 30i-B on current builds. The Fanuc 30i family provides the parameter visibility needed for multi-axis spindle service.",
        [
            ("Doosan Puma spindles",           "/spindle-grinding/doosan-spindle-repair/puma/"),
            ("Doosan DVF 5-Axis spindles",     "/spindle-grinding/doosan-spindle-repair/5-axis-verticals/"),
        ],
    ),
    "puma-vertical-turning": _doosan_spindle_series(
        "puma-vertical-turning", "Puma V / VT / VTR Vertical Turning", "Puma V / VT / VTR",
        "Vertical-turning spindles on Puma V400 through V9300, VT 750/900/1100, and VTR ram-type machines handle large, heavy parts where vertical orientation simplifies workpiece loading. Spindle wear patterns are different from horizontal turning — table bearings see more axial load; the spindle proper sees more cyclic radial load on chucked work.",
        [
            "Table bearing wear from sustained heavy-cut vertical turning.",
            "ATC reliability on V-series with integrated milling affecting spindle nose alignment.",
            "Hydraulic clamp pressure loss affecting spindle bearing life.",
            "Spindle drive faults on heavy-cut production.",
        ],
        "Puma V, VT, and VTR ship on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/) on most current builds. Older Puma V400 may still run [Fanuc 0i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-0i/).",
        [
            ("Doosan Puma spindles",         "/spindle-grinding/doosan-spindle-repair/puma/"),
            ("Doosan DNM Vertical spindles", "/spindle-grinding/doosan-spindle-repair/dnm-verticals/"),
        ],
    ),
    "lynx": _doosan_spindle_series(
        "lynx", "Lynx Compact Turning", "Lynx Compact Turning",
        "Lynx compact-turning spindles — Lynx 220, 2100, 2600, and 300 with a wide range of M, MS, LM, LSY, LY, LMA, MA, II variants — see the highest-cycle environment in the Doosan lineup. Small-shop bar work and bar-fed production grind through bearing-pack life faster than larger-platform production. The compact spindle design balances cost and durability; the wear pattern tracks cycle count more than load.",
        [
            "Front bearing wear from sustained bar-feed production — primary failure mode on compact Lynx.",
            "Bar feeder synchronization issues affecting spindle-side cuts.",
            "Sub-spindle alignment on LSY configurations.",
            "Chuck cylinder leaks from sustained bar-work cycles affecting spindle preload.",
        ],
        "Lynx ships on [Fanuc 0i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-0i/) — typically 0i-D or 0i-F. The compact platform doesn't need the higher-end Fanuc 30i family.",
        [
            ("Doosan Puma spindles",        "/spindle-grinding/doosan-spindle-repair/puma/"),
            ("Doosan Swiss-Type spindles",  "/spindle-grinding/doosan-spindle-repair/swiss-turning/"),
        ],
    ),
    "dnm-verticals": _doosan_spindle_series(
        "dnm-verticals", "DNM Vertical Machining", "DNM Verticals",
        "DNM vertical-machining spindles cover DNM 200 through DNM 750 production verticals, the higher-end DNM 4000/5700/6700 builds, and the DNM 200/5AX 5-axis variant. The line uses different spindle types per size class: smaller DNMs run lighter cartridges; the 4000/5700/6700 production builds have heavier-duty spindles built for sustained cuts.",
        [
            "Spindle bearing failure on high-RPM production work — common on DNM-500 and similar.",
            "Larger spindle bearing wear on DNM 4000/5700/6700 from heavy axial cuts.",
            "Taper damage from toolholder issues during ATC sequences.",
            "Drawbar pull-force loss affecting toolholder retention over high cycle counts.",
        ],
        "DNM ships on [Fanuc 0i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-0i/) for entry and mid-range, and [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/) on DNM 4000/5700/6700/750 production verticals.",
        [
            ("Doosan Horizontals (NHM/NHP/HC) spindles",  "/spindle-grinding/doosan-spindle-repair/horizontals/"),
            ("Doosan DVF 5-Axis spindles",                "/spindle-grinding/doosan-spindle-repair/5-axis-verticals/"),
        ],
    ),
    "horizontals": _doosan_spindle_series(
        "horizontals", "NHM / NHP / HC Horizontal", "NHM / NHP / HC",
        "Horizontal-machining spindles on NHM 4000 through 8000, NHP 4000 through 6300, and HC 400/500 sit oriented for chip drainage. Pallet-changer thermal cycling drives specific wear patterns. The larger NHM-8000 has a heavier-duty spindle to match the heavier axial cuts; smaller NHM-4000 and NHP-4000 see more pallet-cycle bearing wear.",
        [
            "Bearing-pack wear from sustained pallet-changer production.",
            "Larger spindle bearing wear on NHM-8000 from heavy axial cuts.",
            "Spindle thermal cycling from pallet rotation.",
            "Taper damage from high-cycle ATC sequences during pallet changes.",
        ],
        "NHM, NHP, and HC ship on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/) — the multi-axis pallet handling fits the 30i family's parameter set.",
        [
            ("Doosan DNM Vertical spindles",  "/spindle-grinding/doosan-spindle-repair/dnm-verticals/"),
            ("Doosan Puma spindles",          "/spindle-grinding/doosan-spindle-repair/puma/"),
        ],
    ),
    "5-axis-verticals": _doosan_spindle_series(
        "5-axis-verticals", "DVF / FM 5-Axis Vertical", "DVF / FM 5-Axis",
        "DVF and FM 5-axis vertical spindles run high-stress finishing on trunnion-table machines — DVF 5000, 6500, 8000 trunnion 5-axis and the FM 200/5AX Linear-motor build. Spindle work on these platforms requires full RTCP and trunnion kinematic verification post-rebuild because 5-axis tool-tip accuracy depends on spindle geometry staying tight to the trunnion centerline.",
        [
            "Bearing pack wear under sustained 5-axis finishing.",
            "Taper damage from toolholder failure during multi-axis cuts.",
            "RTCP and kinematic drift after spindle work — full re-calibration required.",
            "Linear-motor drive issues on the FM 200/5AX affecting spindle-side work.",
        ],
        "DVF and FM ship on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/) — the 5-axis kinematics need the 30i family's higher feature set for proper RTCP verification.",
        [
            ("Doosan DNM Vertical spindles",     "/spindle-grinding/doosan-spindle-repair/dnm-verticals/"),
            ("Doosan Puma MX / SMX spindles",    "/spindle-grinding/doosan-spindle-repair/puma-mx-smx/"),
        ],
    ),
    "swiss-turning": _doosan_spindle_series(
        "swiss-turning", "Swiss-Type / DST", "Swiss-Type / DST",
        "Doosan Swiss-type spindles — SwiftTurn 32 and 38, the DST series — handle high-precision small-diameter bar work. Swiss-type spindle service interacts with guide bushing wear in ways straight turning doesn't; the two are often companion jobs. Sub-spindle synchronization on twin-spindle Swiss platforms needs careful verification post-rebuild.",
        [
            "Guide bushing wear interacting with spindle service.",
            "Sub-spindle synchronization drift on twin-spindle Swiss configurations.",
            "Bar feeder synchronization issues affecting spindle-side cuts.",
            "Live tool indexing on multi-tool variants affecting spindle-side alignment.",
        ],
        "Doosan Swiss platforms ship on [Fanuc 30i (Doosan)](/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/).",
        [
            ("Doosan Lynx spindles",  "/spindle-grinding/doosan-spindle-repair/lynx/"),
            ("Doosan Puma spindles",  "/spindle-grinding/doosan-spindle-repair/puma/"),
        ],
    ),
}


# ============================================================
# OKUMA SPINDLE
# ============================================================
def _okuma_spindle_series(slug, title_suffix, subtitle, intro, failures, controls, siblings):
    return {
        "title":   f"Okuma {title_suffix} Spindle Repair",
        "slug":    f"okuma-spindle-{slug}",
        "subtitle":subtitle,
        "url":     f"/spindle-grinding/okuma-spindle-repair/{slug}/",
        "intro":   intro,
        "failures":failures,
        "controls_paragraph": controls,
        "siblings":siblings,
    }


_OKUMA_SPINDLE_SERIES_SPOKES = {
    "lb-lu-lathes": _okuma_spindle_series(
        "lb-lu-lathes", "LB / LU Lathe", "LB / LU Horizontal Lathes",
        "Okuma LB and LU horizontal-lathe spindles span entry-production through large-bore turning — LB 200 through LB 5000 EX, LU 300 through LU 8000. Okuma builds spindles in-house under tight tolerances; the platform's reputation for thermal stability matters for service work because the wear patterns are predictable when the machine has been well maintained. Live-tool variants add live-tool drive considerations alongside the main spindle.",
        [
            "Front bearing wear on heavily used LB and LU long-bed machines.",
            "Larger spindle bearing wear on LB 4000 EX and LB 5000 EX from heavy axial cuts.",
            "Tailstock quill wear affecting spindle-side work on long-bed configurations.",
            "Live-tool indexing issues on the live-tool variants.",
            "Spindle preload loss from chuck cylinder issues.",
        ],
        "Older LB and LU run on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/); mid-life on [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/); current LB 3000 EX II and LB 4000/5000 EX on [OSP-P500](/spindle-grinding/okuma-spindle-repair/osp-p500/). Legacy ES-L and ESV may still be on [OSP Legacy](/spindle-grinding/okuma-spindle-repair/osp-legacy/).",
        [
            ("Okuma Genos spindles",   "/spindle-grinding/okuma-spindle-repair/genos/"),
            ("Okuma MULTUS spindles",  "/spindle-grinding/okuma-spindle-repair/multus/"),
        ],
    ),
    "genos": _okuma_spindle_series(
        "genos", "Genos L / Genos M", "Genos",
        "Genos spindles are Okuma's 'Affordable Excellence' line — Genos L lathes (L250, L300, L3000-e, L400, L4000) and Genos M verticals (M460-VE, M560-V, M660-V). The platform's lighter-duty spindle design shows different wear patterns than the higher-end MB/MA or MULTUS lines, particularly under sustained production cycles. Thermal management matters on Genos because the platform's cost optimization doesn't include the same thermal compensation hardware as higher-end machines.",
        [
            "Bearing wear from sustained production cycles.",
            "Spindle thermal drift on machines pushed to upper RPM limits without warm-up.",
            "ATC wear affecting spindle-nose tool retention.",
            "Control panel reliability impacting spindle setup workflow on older Genos.",
        ],
        "Genos ships on [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) — the standard Okuma control for the line through current builds.",
        [
            ("Okuma LB / LU spindles",          "/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/"),
            ("Okuma MB / MA Vertical spindles", "/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/"),
        ],
    ),
    "mb-ma-verticals": _okuma_spindle_series(
        "mb-ma-verticals", "MB / MA Vertical", "MB / MA Verticals",
        "MB and MA vertical-machining spindles — MB-46V through MB-66V production, MB-4000H/5000H horizontal-spindle builds, MA-400 through MA-8000 larger-envelope platforms — are the workhorses on Okuma vertical shop floors. The platform's in-house spindle design and thermal compensation lend predictable wear patterns: machines that have been maintained well wear at expected rates; machines pushed past their thermal compensation limits show different patterns.",
        [
            "ATC drum wear affecting spindle-nose tool retention.",
            "Ballscrew wear from sustained heavy cuts affecting spindle-side accuracy.",
            "Spindle bearing wear on high-RPM MB-66V production.",
            "Larger spindle bearing wear on MA-650 and MA-8000 from heavy axial cuts.",
        ],
        "Older MB and MA run on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/); current MB and MA builds run on [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/). Legacy MV and MX-45 are usually [OSP Legacy](/spindle-grinding/okuma-spindle-repair/osp-legacy/).",
        [
            ("Okuma Genos spindles",          "/spindle-grinding/okuma-spindle-repair/genos/"),
            ("Okuma MULTUS spindles",         "/spindle-grinding/okuma-spindle-repair/multus/"),
        ],
    ),
    "multus": _okuma_spindle_series(
        "multus", "MULTUS B-Axis Multitasking", "MULTUS Multitasking",
        "MULTUS spindles are Okuma's B-axis multitasking platform — MULTUS B200 through B750 (with II variants), MULTUS U3000 through U5000 large-envelope builds, plus the historic MacTurn predecessors. The B-axis milling spindle is the highest-stress component on MULTUS just as on Mazak Integrex. Okuma's thermal compensation framework makes B-axis spindle service more predictable than on platforms without the same hardware.",
        [
            "B-axis milling spindle bearing wear from sustained mill-turn production.",
            "Lower turret spindle wear on twin-turret MULTUS configurations.",
            "ATC chain reliability affecting spindle-nose tool retention.",
            "Sub-spindle alignment on dual-spindle MULTUS variants.",
        ],
        "MULTUS runs on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/) on older builds and [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) on current. The flagship MULTUS U5000 and current B-II builds ship on [OSP-P500](/spindle-grinding/okuma-spindle-repair/osp-p500/).",
        [
            ("Okuma Twin-Spindle / Twin-Turret",  "/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/"),
            ("Okuma LB / LU spindles",            "/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/"),
        ],
    ),
    "twin-spindle-twin-turret": _okuma_spindle_series(
        "twin-spindle-twin-turret", "Twin-Spindle / Twin-Turret", "Twin-Spindle / Twin-Turret",
        "Okuma's twin-spindle and twin-turret platforms — 2SP-2500H, 2SP-V40, LT 200-MY through LT 300-MY, LT 2000 EX — add sub-spindle synchronization complexity to spindle service. Both spindles need to be in tolerance for the part-transfer sequences to work; rebuilding one without verifying the other isn't standard practice. Twin-turret platforms add lower-turret considerations alongside the main spindle work.",
        [
            "Sub-spindle synchronization drift after main-spindle rebuild — both need verification.",
            "Lower turret indexing and spindle-side alignment.",
            "Hydraulic system pressure loss on twin-spindle affecting bearing preload.",
            "Part-transfer reliability on parts catcher systems.",
        ],
        "Twin-spindle and twin-turret platforms run on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/) on older builds, [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) on LT 300-MY and LT 2000 EX. Legacy LT-15 and LT-25 are typically [OSP Legacy](/spindle-grinding/okuma-spindle-repair/osp-legacy/).",
        [
            ("Okuma MULTUS spindles",           "/spindle-grinding/okuma-spindle-repair/multus/"),
            ("Okuma LB / LU spindles",          "/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/"),
        ],
    ),
    "vtm": _okuma_spindle_series(
        "vtm", "VTM Vertical Turning", "VTM",
        "Okuma VTM vertical-turning spindles — VTM-65, VTM-100, VTM-120, VTM-180 — handle large, heavy chucked parts where vertical orientation simplifies workpiece loading. Table bearings see sustained axial load from heavy roughing cuts; the spindle proper sees cyclic radial load. The platform's thermal stability helps with long-cycle finishing work.",
        [
            "Table bearing wear from sustained heavy-cut vertical turning.",
            "ATC reliability on milling-capable VTM builds.",
            "Swarf evacuation issues around the table affecting spindle-nose work.",
            "Hydraulic clamp pressure loss affecting bearing preload.",
        ],
        "VTM runs on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/) on older builds and [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) on current.",
        [
            ("Okuma MU 5-Axis / MCR Bridge",       "/spindle-grinding/okuma-spindle-repair/v-bridge-mills/"),
            ("Okuma LAW / LFS Heavy Lathes",       "/spindle-grinding/okuma-spindle-repair/heavy-lathes/"),
        ],
    ),
    "v-bridge-mills": _okuma_spindle_series(
        "v-bridge-mills", "MU 5-Axis / MCR Bridge", "MU 5-Axis / MCR Bridge",
        "MU 5-axis and MCR bridge-mill spindles handle the most precise work in the Okuma lineup. MU-400V through MU-8000V are trunnion-table 5-axis machines where RTCP verification post-rebuild is mandatory. MCR-A5C and MCR-BIII bridge mills handle very large parts where bridge geometry interacts with spindle-side accuracy in ways trunnion machines don't.",
        [
            "Trunnion calibration drift on MU builds after spindle work — A and C-axis zero-point work.",
            "Bridge geometry calibration on MCR — large-span alignment after spindle service.",
            "Spindle bearing wear on MU 5-axis builds from high-stress cuts.",
            "Linear scale issues on bridge machines affecting spindle-side accuracy.",
        ],
        "MU and MCR ship on [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) — the standard control for these platforms across the current generation.",
        [
            ("Okuma MB / MA Vertical spindles",  "/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/"),
            ("Okuma VTM spindles",               "/spindle-grinding/okuma-spindle-repair/vtm/"),
        ],
    ),
    "heavy-lathes": _okuma_spindle_series(
        "heavy-lathes", "Heavy Lathes (LAW / LFS)", "LAW / LFS Heavy",
        "Okuma LAW and LFS heavy-lathe spindles — LAW 1000 through 3000 heavy lathes and LFS-590 flat-bed turning — handle very large workpieces under very heavy cuts. The spindles are scaled to match: larger bore, larger bearings, heavier-duty drives. Wear patterns track the loads more than the cycle count — these machines see fewer cycles but each one matters more.",
        [
            "Large-bore spindle wear on sustained heavy roughing cuts.",
            "Way wear from extended heavy-cut production affecting spindle-side alignment.",
            "Hydraulic chuck pressure loss on large workpieces affecting bearing preload.",
            "Drive amplifier faults from heavy-cut loads.",
        ],
        "LAW and LFS run on [OSP-P200](/spindle-grinding/okuma-spindle-repair/osp-p200/) on older builds and [OSP-P300](/spindle-grinding/okuma-spindle-repair/osp-p300/) on current.",
        [
            ("Okuma LB / LU spindles",   "/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/"),
            ("Okuma VTM spindles",       "/spindle-grinding/okuma-spindle-repair/vtm/"),
        ],
    ),
}

_OKUMA_SPINDLE_CONTROL_SPOKES = {
    "osp-p200": {
        "title":   "Spindle Service on Okuma OSP-P200",
        "slug":    "okuma-spindle-osp-p200",
        "subtitle":"OSP-P200",
        "url":     "/spindle-grinding/okuma-spindle-repair/osp-p200/",
        "era":     "Roughly 2003 through 2012",
        "intro":   "OSP-P200 paired with the spindle drive generation of the early-2000s through 2012 Okuma fleet. For spindle service in 2026, the control side is at late-life status — HDD work, MMC board faults, keypad wear — but most spindle drive parts are still serviceable through Okuma channels. Capture the parameter set before any control-side work that could affect spindle configuration.",
        "machines_paragraph": "OSP-P200 shipped across the older Okuma lineup — [LB and LU lathes](/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/), [MB and MA verticals](/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/), older [MULTUS](/spindle-grinding/okuma-spindle-repair/multus/) builds, [VTM](/spindle-grinding/okuma-spindle-repair/vtm/), [twin-spindle and twin-turret](/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/), and [LAW heavy lathes](/spindle-grinding/okuma-spindle-repair/heavy-lathes/).",
        "failures": [
            "Spindle parameters at risk during HDD failure or MMC board work — capture before any service.",
            "Spindle drive amplifier faults on heavy production — still serviceable through Okuma channels.",
            "Keypad failures affecting spindle setup workflow.",
            "Thermal damage from fan failures — affects both control and spindle-side components.",
        ],
        "parts_paragraph": "P200 spindle drive parts are still supported through Okuma channels for most board items. Some components are heading toward aftermarket-only. We check parts availability before quoting board-level spindle drive work.",
        "recovery_paragraph": "Spindle parameter backup on P200 is straightforward through the control's built-in path. Before any spindle work or HDD/board service, we capture the spindle-specific parameters (drive tuning, encoder offsets, preload settings) along with the full machine parameter set.",
        "siblings": [
            ("OSP-P300 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p300/"),
            ("OSP Legacy spindle service", "/spindle-grinding/okuma-spindle-repair/osp-legacy/"),
        ],
    },
    "osp-p300": {
        "title":   "Spindle Service on Okuma OSP-P300",
        "slug":    "okuma-spindle-osp-p300",
        "subtitle":"OSP-P300",
        "url":     "/spindle-grinding/okuma-spindle-repair/osp-p300/",
        "era":     "Roughly 2012 through 2020",
        "intro":   "OSP-P300 paired with the mid-life Okuma spindle drives — well documented, well supported, easy to work with for spindle service. The SSD upgrade on early P300 builds is a high-value companion service when a machine is in for spindle work. P300's diagnostic visibility into spindle parameters is good and the touchscreen workflow makes spindle setup verification fast.",
        "machines_paragraph": "OSP-P300 ships across the modern Okuma lineup — current [LB and LU lathes](/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/), [Genos](/spindle-grinding/okuma-spindle-repair/genos/), current [MB and MA verticals](/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/), [MULTUS](/spindle-grinding/okuma-spindle-repair/multus/) (except current U5000), [VTM](/spindle-grinding/okuma-spindle-repair/vtm/), [MU and MCR](/spindle-grinding/okuma-spindle-repair/v-bridge-mills/), [twin-spindle / twin-turret](/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/), and [LAW](/spindle-grinding/okuma-spindle-repair/heavy-lathes/) builds.",
        "failures": [
            "SSD upgrade availability — high-value preventive service on early P300 builds when machine is in for spindle work.",
            "Touchscreen drift affecting spindle setup workflow on heavily used machines.",
            "Ethernet and USB issues affecting spindle parameter backup paths.",
            "More parameters than P200 to manage — backup discipline matters.",
        ],
        "parts_paragraph": "OSP-P300 spindle drive parts and control parts are fully supported through Okuma channels.",
        "recovery_paragraph": "P300 supports clean parameter backup via network or USB. Before any spindle work we capture the spindle-specific parameter set (drive tuning, encoder offsets, preload settings) along with the full parameter set. SSD upgrades on early P300 builds combine well with scheduled spindle work.",
        "siblings": [
            ("OSP-P200 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p200/"),
            ("OSP-P500 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p500/"),
        ],
    },
    "osp-p500": {
        "title":   "Spindle Service on Okuma OSP-P500",
        "slug":    "okuma-spindle-osp-p500",
        "subtitle":"OSP-P500",
        "url":     "/spindle-grinding/okuma-spindle-repair/osp-p500/",
        "era":     "2020 to present",
        "intro":   "OSP-P500 is Okuma's current control generation, paired with current Okuma spindle drives. Spindle service on P500-equipped machines is mostly the spindle hardware itself; the control side adds network-based parameter management, MTConnect spindle metric integration, and the diagnostic visibility the platform provides. Parameter backup is fully network-capable.",
        "machines_paragraph": "OSP-P500 ships on Okuma's current flagship platforms — latest [LB 3000 EX II and LB 4000/5000 EX](/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/), current [MULTUS U5000 and B-II](/spindle-grinding/okuma-spindle-repair/multus/), and other current-generation builds.",
        "failures": [
            "Network configuration drift affecting spindle monitoring integration.",
            "MTConnect setup for shop-floor spindle metric integration.",
            "App integration on the OSP-P500 platform.",
            "More parameters than P300 to manage — backup discipline scales.",
        ],
        "parts_paragraph": "P500 spindle drives and control parts are fully current through Okuma channels.",
        "recovery_paragraph": "P500 has the most modern backup workflow in the Okuma family — network-based parameter and program backup. Before any spindle work we capture the spindle parameter set over the network, including MTConnect integration settings.",
        "siblings": [
            ("OSP-P300 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p300/"),
            ("OSP-P200 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p200/"),
        ],
    },
    "osp-legacy": {
        "title":   "Spindle Service on OSP Legacy (5000 / 7000 / U10 / U100)",
        "slug":    "okuma-spindle-osp-legacy",
        "subtitle":"OSP Legacy",
        "url":     "/spindle-grinding/okuma-spindle-repair/osp-legacy/",
        "era":     "Pre-2003",
        "intro":   "OSP Legacy paired with pre-2003 Okuma spindle drives — OSP 5000, OSP 7000, U10, U100. For spindle service on these machines, the conversation becomes a parts-availability conversation more than anything. Some bearing packs are still sourceable; some drive amplifiers have moved to remanufactured-only or retrofit-territory. We scope each spindle job based on what's currently sourceable before quoting.",
        "machines_paragraph": "OSP Legacy controls shipped on older Okuma platforms — legacy MV-series verticals, MX-45, ES-L and ESV [LB/LU](/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/) builds, older [LT-15 and LT-25 twin-turret](/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/), and legacy MacTurn predecessors to current MULTUS.",
        "failures": [
            "Bubble memory loss on the oldest OSP 5000 builds — affects spindle parameter storage.",
            "Spindle drive amplifier obsolescence — heading toward aftermarket-only on the oldest builds.",
            "Encoder feedback issues at the control side that can present as spindle problems.",
            "Floppy and PCMCIA media reliability for spindle parameter backup paths.",
        ],
        "parts_paragraph": "OSP Legacy spindle drives are heavily obsolescent. Most board-level repair runs through remanufacturing specialists. For some machines, the conversation moves to retrofit — replacing the OSP Legacy control with a current OSP-P300 or P500. Spindle drive replacement is part of that conversation when the original drive is no longer sourceable.",
        "recovery_paragraph": "Spindle parameter backup on OSP Legacy is generation-specific. The process starts with documenting the existing parameter set on whatever media the control supports, then planning the work. For machines being retrofitted to current OSP, the spindle parameter migration is part of that conversation.",
        "siblings": [
            ("OSP-P200 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p200/"),
            ("OSP-P300 spindle service",   "/spindle-grinding/okuma-spindle-repair/osp-p300/"),
        ],
    },
}


# ============================================================
# FANUC SPINDLE — control-only, flipped hub structure
# ============================================================
def _fanuc_spindle_control(slug, title_suffix, subtitle, era, intro, machines_paragraph, failures, parts, recovery, siblings):
    return {
        "title":   f"Spindle Service on Fanuc {title_suffix}",
        "slug":    f"fanuc-spindle-{slug}",
        "subtitle":subtitle,
        "url":     f"/spindle-grinding/fanuc-spindle-repair/{slug}/",
        "era":     era,
        "intro":   intro,
        "machines_paragraph": machines_paragraph,
        "failures":failures,
        "parts_paragraph": parts,
        "recovery_paragraph": recovery,
        "siblings":siblings,
    }


_FANUC_SPINDLE_CONTROL_SPOKES = {
    "series-0-legacy": _fanuc_spindle_control(
        "series-0-legacy", "Series 0 / 0M / 0T (Pre-i Legacy)", "Series 0 Legacy", "1980s through 1990s",
        "Fanuc Series 0, 0M, and 0T paired with the early Fanuc spindle drive generations of the 1980s and 1990s. For spindle service in 2026, the conversation is parts-availability-first — many spindle drive amplifiers from this era are aftermarket-only, and bubble memory recovery is fragile. Capture every parameter you can before touching the control side.",
        "Series 0 shipped on a huge range of late-1980s through 1990s machines across multiple OEMs. Older [Doosan Puma](/spindle-grinding/doosan-spindle-repair/puma/) and other Asian-OEM lathes from this era are common platforms running Series 0 with their original spindle drive amplifiers.",
        [
            "Bubble memory loss taking spindle parameters with it — the single most fragile failure mode on Series 0.",
            "Spindle drive amplifier obsolescence — original drives from this era are heavily aftermarket.",
            "Encoder feedback issues at the control side that can present as spindle problems.",
            "Spindle parameter set differences across machine OEMs — Series 0 implementations vary by integrator.",
        ],
        "Series 0 spindle drive parts are heavily aftermarket-only at this point. Remanufactured boards through specialists are the standard path on board-level spindle drive work. For some machines, the conversation moves to retrofit — replacing the Series 0 with a Fanuc 0i and a corresponding spindle drive upgrade.",
        "Spindle parameter recovery on Series 0 is the most fragile recovery procedure in the Fanuc family. Capture the parameter set on whatever media the control supports before any battery or board work. Document the spindle drive tuning, encoder offsets, and any OEM-specific spindle parameters before service.",
        [
            ("Fanuc Series 6-15 spindle service",          "/spindle-grinding/fanuc-spindle-repair/series-6-15-legacy/"),
            ("Fanuc Series 16i/18i/21i spindle service",   "/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/"),
        ],
    ),
    "series-6-15-legacy": _fanuc_spindle_control(
        "series-6-15-legacy", "Series 6 / 10 / 11 / 12 / 15", "Series 6 through 15", "1980s through 2000s",
        "Fanuc Series 6, 10, 11, 12, and 15 paired with the corresponding higher-end Fanuc spindle drives of their era. Series 15 in particular still sees active service on larger machines from the late 1990s and early 2000s. Spindle service patterns overlap with Series 0 but parts availability is sometimes better, particularly on Series 15.",
        "Series 6 through 12 shipped on higher-end machines from various OEMs through the 1990s. Series 15 was common on larger and more sophisticated machines into the 2000s — including some larger [Doosan](/spindle-grinding/doosan-spindle-repair/puma/) and other Asian-OEM platforms running Fanuc-paired spindle drives.",
        [
            "Memory battery loss affecting spindle parameters and tool tables.",
            "Spindle drive amplifier obsolescence — generally still serviceable through remanufacturing specialists.",
            "Encoder feedback issues at the control side.",
            "Older PCB-level faults on spindle drive boards requiring remanufacturing.",
        ],
        "Series 6 through 12 spindle drive parts are deep-legacy with most aftermarket-only. Series 15 still has better parts availability through Fanuc and remanufacturing specialists.",
        "Battery and spindle parameter recovery follows the standard Fanuc workflow — capture parameters before any battery work, replace battery on powered control, restore parameters as needed. Series 15 has somewhat better recovery tooling than the earlier siblings.",
        [
            ("Fanuc Series 0 / 0M / 0T spindle service",   "/spindle-grinding/fanuc-spindle-repair/series-0-legacy/"),
            ("Fanuc Series 16i / 18i / 21i spindle service","/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/"),
        ],
    ),
    "series-16i-18i-21i": _fanuc_spindle_control(
        "series-16i-18i-21i", "Series 16i / 18i / 21i", "Series 16i / 18i / 21i", "Roughly 1995 through 2010",
        "Fanuc 16i, 18i, and 21i (Model A and B) paired with the Fanuc αi spindle drive generation — the most common spindle drive setup on mid-life machines in 2026. Spindle service on this family is well documented; αi drive parts are still well supported through Fanuc; the workflow is mature. PCMCIA media obsolescence is the most common companion issue when these machines come in for spindle work.",
        "Series 16i / 18i / 21i shipped on a wide cross-section of late-1990s through 2000s machines. Many [Doosan Puma](/spindle-grinding/doosan-spindle-repair/puma/) builds from this era ran 16i/18i/21i with Fanuc αi spindle drives.",
        [
            "PCMCIA media obsolescence affecting spindle parameter backup paths.",
            "FROM and SRAM battery loss affecting spindle parameters.",
            "αi spindle drive amplifier faults from sustained heavy production — generally still serviceable.",
            "Monitor failure affecting spindle setup workflow.",
        ],
        "Series 16i / 18i / 21i spindle drive parts (αi family) are still well supported through Fanuc channels. Remanufactured boards through specialists are an option for the oldest builds. PCMCIA-to-CF or PCMCIA-to-USB media migration is a frequent companion job to spindle service.",
        "Spindle parameter backup on 16i / 18i / 21i is the standard Fanuc workflow — capture parameters before any battery or board work, replace battery on powered control, restore as needed. PCMCIA media migration is part of the same conversation we scope upfront when a machine comes in for spindle service.",
        [
            ("Fanuc Series 0i spindle service",            "/spindle-grinding/fanuc-spindle-repair/series-0i/"),
            ("Fanuc Series 30i / 31i / 32i spindle service","/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/"),
        ],
    ),
    "series-0i": _fanuc_spindle_control(
        "series-0i", "Series 0i (A / B / C / D / F)", "Series 0i", "2003 through present",
        "Fanuc Series 0i paired with the αi-class spindle drive generation — the most common Fanuc spindle drive setup we see on shop floors. From 0i-A through current 0i-F, the spindle drive parts are well supported, the parameter backup workflow is well documented, and the troubleshooting tools are mature. Most spindle service on 0i is the spindle hardware itself; the control side rarely complicates the work.",
        "Series 0i shipped on the broadest cross-section of any Fanuc control — most entry and mid-range [Doosan Puma](/spindle-grinding/doosan-spindle-repair/puma/) and all [Doosan Lynx](/spindle-grinding/doosan-spindle-repair/lynx/), older [Haas](/spindle-grinding/haas-spindle-repair/vf-series/) imports, and a huge fleet of imported Asian-OEM machines. 0i-F is the current generation; 0i-D dominates the 2010-2018 fleet.",
        [
            "HDD or CF card failure affecting spindle parameter access — replacement and SSD-style migration are routine.",
            "Battery loss affecting spindle and machine parameters.",
            "αi spindle drive amplifier faults from sustained heavy production.",
            "Operator-panel button failure on high-cycle keys affecting spindle setup.",
        ],
        "Series 0i spindle drive parts are fully current and supported through Fanuc. 0i-A and B are heading toward late-life status; 0i-D and 0i-F are fully current.",
        "Spindle parameter backup on 0i is well documented. Before any spindle work or battery replacement, capture the spindle-specific parameters (drive tuning, encoder offsets, preload settings) and PMC ladder logic along with the full parameter set.",
        [
            ("Fanuc Series 16i/18i/21i spindle service",   "/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/"),
            ("Fanuc Series 30i / 31i / 32i spindle service","/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/"),
        ],
    ),
    "series-30i-31i-32i": _fanuc_spindle_control(
        "series-30i-31i-32i", "Series 30i / 31i / 32i / 35i", "Series 30i / 31i / 32i", "2008 through present",
        "Fanuc 30i, 31i, 32i, and 35i (Model A and B) paired with the current αii-class spindle drive generation. The platform is used on higher-end multi-axis machines where spindle parameter visibility and FOCAS integration matter. Most spindle service work on 30i family machines is the spindle hardware itself; the control side adds network-based parameter management and shop-floor monitoring integration.",
        "30i family ships on higher-end machines — most current [Doosan Puma](/spindle-grinding/doosan-spindle-repair/puma/) (2600SY, 3100, 4100, 5100, 700, 800), all [Puma MX and SMX](/spindle-grinding/doosan-spindle-repair/puma-mx-smx/), [DVF 5-axis](/spindle-grinding/doosan-spindle-repair/5-axis-verticals/), [NHM/NHP/HC horizontals](/spindle-grinding/doosan-spindle-repair/horizontals/), and the higher-end [DNM verticals](/spindle-grinding/doosan-spindle-repair/dnm-verticals/).",
        [
            "Less hardware failure than earlier generations given relative age.",
            "Network configuration drift affecting spindle monitoring integration.",
            "MTConnect and FOCAS setup for spindle metric integration.",
            "SSD upgrades on early 30i-A builds with original HDD — companion service to spindle work.",
        ],
        "30i family spindle drive parts (αii-class) are fully current and supported through Fanuc.",
        "Spindle parameter backup on 30i is modern — network and USB-based parameter and PMC backup. Before any spindle work we capture the parameter set including FOCAS integration settings and verify the restore at sign-off.",
        [
            ("Fanuc Series 0i spindle service",               "/spindle-grinding/fanuc-spindle-repair/series-0i/"),
            ("Fanuc Series 16i / 18i / 21i spindle service",   "/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/"),
        ],
    ),
    "power-mate-i": _fanuc_spindle_control(
        "power-mate-i", "Power Mate i", "Power Mate i", "2000 through present",
        "Fanuc Power Mate i is the dedicated-axis or servo-positioner control. For spindle service, Power Mate i is most relevant on dedicated rotary indexers, sub-spindles on multi-axis configurations, and similar auxiliary spindle drives. Service work focuses on the spindle drive amplifier, encoder feedback, and parameter recovery.",
        "Power Mate i shows up as a dedicated-axis or sub-spindle control on rotary tables, indexers, sub-spindles, and similar auxiliary equipment alongside primary CNC platforms. It often runs as a subordinate control under a primary Fanuc 0i, 30i, or similar host.",
        [
            "Drive amplifier faults — most common single issue.",
            "Encoder feedback issues — contamination or signal loss.",
            "Parameter loss from battery failure.",
            "Communication faults with the host CNC affecting spindle-side coordination.",
        ],
        "Power Mate i spindle drive parts are supported through Fanuc on current generations. Older Power Mate i builds may have parts heading toward aftermarket.",
        "Parameter backup on Power Mate i follows the standard Fanuc workflow. The single-axis nature makes the parameter set smaller, but the discipline is the same — backup before any battery or board work, verify the restore.",
        [
            ("Fanuc Series 0i spindle service",                 "/spindle-grinding/fanuc-spindle-repair/series-0i/"),
            ("Fanuc Series 30i / 31i / 32i spindle service",    "/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/"),
        ],
    ),
}


# ============================================================
# Aggregated SPINDLE_HUB_DATA — consumed by generate_brand_pages.py
# ============================================================
SPINDLE_HUB_DATA = {
    "mazak": {
        "browse_series": [
            ("Quick Turn / QTN",                       "/spindle-grinding/mazak-spindle-repair/quick-turn/",
             "Lathe spindles. Cartridge-style turning spindles across QT-8 through QTN-450, MS/MSY twin-spindle variants, current Compact/Smart/Primos/Ez/Ultra."),
            ("Integrex",                               "/spindle-grinding/mazak-spindle-repair/integrex/",
             "Mill-turn multitasking spindles. Turning + B-axis milling spindle on every Integrex platform — i-series originals, e-series, j, i-V, i-H."),
            ("Variaxis",                               "/spindle-grinding/mazak-spindle-repair/variaxis/",
             "5-axis trunnion vertical spindles. RTCP and kinematic verification post-rebuild — i-300 through i-800 and legacy 500/630/730."),
            ("Vertical Machining Centers (VTC + VCN)", "/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/",
             "Production vertical spindles. VTC long-bed and VCN high-RPM — VTC-16 through VTC-800, VCN-410 through VCN-700, FJV and AJV."),
            ("HCN Horizontals",                        "/spindle-grinding/mazak-spindle-repair/hcn-horizontal/",
             "Horizontal-orientation spindles. Pallet-cycle wear patterns — HCN-4000 through HCN-10800 and legacy PFH and H-series."),
            ("Turning Legacy",                         "/spindle-grinding/mazak-spindle-repair/turning-legacy/",
             "Older Mazak turning spindles. Bearing-pack rebuilds with current-supply parts — Slant Turn, Multiplex, Megaturn, HQR, Powermaster."),
        ],
        "browse_control": [
            ("Mazatrol Legacy",   "/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/",
             "M-2, M-32, M-Plus, Fusion 640. Parameter capture before service; drive amplifier parts late-life."),
            ("Mazatrol Matrix",   "/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/",
             "Matrix and Matrix 2. αi-class spindle drives; SSD upgrade companion service on Matrix-1."),
            ("Mazatrol Smooth",   "/spindle-grinding/mazak-spindle-repair/smooth-control/",
             "SmoothX, SmoothG, SmoothAi. Network parameter backup; MTConnect spindle monitoring integration."),
        ],
        "browse_service": [
            ("Mazak machine repair",                   "/repairs/mazak-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-spindle Mazak service work."),
            ("Mazak way covers",                       "/way-covers/mazak-cnc-way-covers/",
             "Replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work",         "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What spindle work do you do on Mazak machines?",
             "Bearing-pack replacement, taper grinding to restore tolerance, dynamic balancing, encoder service, drawbar service. We rebuild on the bench and verify balance and runout before shipping back. For Integrex and Variaxis, we also run the platform-specific kinematic verification — that's not a separate quote, it's part of the spindle service."),
            ("How long does a Mazak spindle rebuild take?",
             "3 to 5 weeks on most jobs depending on cartridge damage, bearing availability, and whether grinding is needed. We scope each job individually — diagnostic is fast, but the parts side varies by Mazak generation. Matrix-era machines tend to run shorter; legacy Mazatrol machines can run longer if parts need to be sourced."),
            ("Do you grind Mazak spindle tapers back to factory tolerance?",
             "Yes — precision spindle grinding to restore runout is standard practice on every rebuild where the taper shows wear. Photo verification at sign-off is part of the process."),
            ("What about Integrex B-axis milling spindles?",
             "B-axis milling spindle rebuilds are routine work. Integrex platforms require careful B-axis kinematic verification after spindle work because multitasking tolerances are tighter than on straight verticals. We run the verification before shipping."),
            ("Can you upgrade a Matrix-1 to SSD while a Mazak is in for spindle work?",
             "Yes — the SSD upgrade on Matrix-1 is a high-ROI companion service when the machine is already with us for spindle work. It eliminates the single most common Matrix-generation control failure point and shortens future service intervals."),
            ("Do you service older Mazak machines with M-Plus or Fusion 640 controls?",
             "Yes. Legacy Mazatrol spindle service is routine — bearing-pack rebuilds with current-supply parts where the original bearings are no longer sourceable. The control-side conversation runs in parallel because legacy parameter management matters during any spindle work."),
        ],
        "series_spokes":  _MAZAK_SPINDLE_SERIES_SPOKES,
        "control_spokes": _MAZAK_SPINDLE_CONTROL_SPOKES,
        "hero_lede": "Mazak spindle work is our highest-value service line. We rebuild, regrind, and rebalance across every Mazak platform — Quick Turn lathes, Integrex multitasking, Variaxis 5-axis, VTC and VCN verticals, HCN horizontals, and the turning legacy lineup. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Mazak spindle calls fall into a few patterns: front bearing wear on Quick Turn high-coolant production, B-axis milling spindle wear on Integrex multitasking, high-RPM spindle bearing failure on VCN aluminum aerospace work, and pallet-cycle bearing wear on HCN horizontals. Control-side, spindle parameter management differs by Mazatrol generation — Legacy needs the parameter set captured before any work; Matrix-era is well documented and well supported; Smooth has network-based backup. We diagnose each spindle before quoting.",
        "how_we_approach": "Mazak spindle service starts with the platform — Integrex and Variaxis kinematic considerations differ from a Quick Turn rebuild — and then the control generation, because parameter recovery paths differ across Mazatrol Legacy, Matrix, and Smooth. On the bench: tear down, inspect bearings, evaluate the taper for grinding, source parts, rebuild, balance, verify runout. For multitasking and 5-axis platforms we run the platform-specific kinematic verification before sign-off.",
        "browse_control_intro": "Mazak spindles pair with three Mazatrol control generations. Pick yours for parameter-management considerations during spindle service.",
    },

    "haas": {
        "browse_series": [
            ("VF Series",                          "/spindle-grinding/haas-spindle-repair/vf-series/",
             "Vertical mill spindles. VF-1 through VF-12, YT extended-Y and SS super-speed variants."),
            ("ST Series",                          "/spindle-grinding/haas-spindle-repair/st-series/",
             "Lathe spindles. ST-10 through ST-55, SSY Y-axis, DS-30 dual-spindle."),
            ("UMC Series",                         "/spindle-grinding/haas-spindle-repair/umc-series/",
             "5-axis universal spindles. UMC-350 through UMC-1600 with SS variants. RTCP verification post-rebuild."),
            ("EC Series",                          "/spindle-grinding/haas-spindle-repair/ec-series/",
             "Horizontal spindles. EC-300 through EC-3000, pallet-pool and 4-axis variants."),
            ("Mini Mill / Toolroom / DT / DM / VM","/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/",
             "Compact and toolroom spindles. DT high-cycle, DM/VM mold work, Mini Mill general-purpose."),
            ("Toolroom Lathes (TL / CL)",          "/spindle-grinding/haas-spindle-repair/toolroom-lathes/",
             "TL-1 through TL-4 and CL-1 — bridging toolroom and production turning."),
        ],
        "browse_control": [
            ("Haas Classic Control",  "/spindle-grinding/haas-spindle-repair/haas-classic-control/",
             "Pre-NGC, through 2014. Parameter capture before service; MOCON board can present as spindle issue."),
            ("Haas Next Generation Control (NGC)", "/spindle-grinding/haas-spindle-repair/haas-ngc/",
             "2014 to present. Network parameter backup; MyHaas spindle monitoring integration."),
        ],
        "browse_service": [
            ("Haas machine repair",            "/repairs/haas-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-spindle Haas service work."),
            ("Haas way covers",                "/way-covers/haas-cnc-way-covers/",
             "Replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work", "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What spindle work do you do on Haas machines?",
             "Bearing-pack replacement, taper grinding to restore tolerance, dynamic balancing, drawbar service, and encoder service. For UMC 5-axis machines we also run kinematic verification post-rebuild because tool-tip accuracy depends on spindle geometry. Runout and balance verification at sign-off is part of every rebuild."),
            ("How long does a Haas spindle rebuild take?",
             "3 to 5 weeks on most rebuilds. SS super-speed variants typically run a bit longer because higher-RPM bearings need more careful balancing. DT high-cycle drill-tap spindles can be faster because the bearing arrangement is simpler."),
            ("Do you service Haas SS spindles differently?",
             "Yes — SS super-speed variants have higher-RPM bearing packs that need tighter balance class verification post-rebuild. The teardown and rebuild process is similar; the verification standard is higher."),
            ("Can you grind Haas spindle tapers back to factory tolerance?",
             "Yes. Precision spindle grinding to restore runout is part of every rebuild where the taper shows wear. Common on machines that have seen toolholder issues or crashes."),
            ("Do you service Haas Classic Control machines from the early 2000s?",
             "Yes. Classic Control spindle service is routine — bearing-pack rebuilds, taper grinding, balancing. The control side adds parameter management considerations: capture the parameter set before any battery or board work, restore at sign-off. Drive amplifier parts are still available through Haas channels for most Classic-vintage spindles."),
            ("What about UMC 5-axis spindles?",
             "UMC spindle rebuilds include full RTCP and kinematic verification post-bench-work because 5-axis tool-tip accuracy depends on spindle geometry staying tight to the trunnion centerline. We don't hand back a UMC spindle without that verification."),
        ],
        "series_spokes":  _HAAS_SPINDLE_SERIES_SPOKES,
        "control_spokes": _HAAS_SPINDLE_CONTROL_SPOKES,
        "hero_lede": "Haas spindle service across the Midwest — VF and ST production spindles, UMC 5-axis spindles with kinematic verification, EC horizontal spindles, and the compact Mini Mill / DT / DM / VM family. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Haas spindle calls fall into a few patterns: bearing-pack wear on SS super-speed variants from sustained high-RPM production, front bearing wear on ST chuckers from bar-feed cycles, high-cycle wear on DT drill-tap spindles, and pallet-cycle bearing wear on EC horizontals. UMC 5-axis adds RTCP and trunnion kinematic considerations. Control-side, NGC parameter management is straightforward; Classic Control adds MOCON board diagnostic considerations.",
        "how_we_approach": "Haas spindle service starts with confirming the platform (VF / ST / UMC / EC / compact) and the control generation. For UMC 5-axis work, RTCP verification post-rebuild is mandatory. On the bench: teardown, bearing inspection, taper evaluation, parts sourcing, rebuild, balance, runout verification with photo at sign-off.",
        "browse_control_intro": "Haas spindles pair with two control generations. Pick yours for parameter-management considerations during spindle service.",
    },

    "dmg-mori": {
        "browse_series": [
            ("NLX / ALX",                "/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/",
             "Universal turning spindles. NLX 1500 through 6000, ALX 1500 through 2500."),
            ("CTX / CLX",                "/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/",
             "Turning + TC turn-mill spindles. CLX 350/450/550, CTX 310 through 850, plus TC B-axis variants."),
            ("NTX",                      "/spindle-grinding/dmg-mori-spindle-repair/ntx/",
             "Integrated mill-turn spindles. Turning + B-axis milling — NTX 1000 through 4000."),
            ("DMU / DMC",                "/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/",
             "5-axis universal spindles. DMU 50 through 340, monoBLOCK/duoBLOCK, DMC variants. RTCP verification."),
            ("NHX / NH",                 "/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/",
             "Horizontal spindles. NHX 4000 through 10000 plus legacy NH."),
            ("NVX / NV / NVD",           "/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/",
             "Vertical-machining spindles. NVX 4000 through 7000, NV 4000/5000, NVD DCG."),
            ("CMX / CMX U",              "/spindle-grinding/dmg-mori-spindle-repair/cmx/",
             "Entry production spindles. CMX 600V through 1300V, CMX 50U and 70U 5-axis."),
            ("DMP / Milltap",            "/spindle-grinding/dmg-mori-spindle-repair/dmp-milltap/",
             "Compact production spindles. High-cycle drill-tap and small-part — DMP 35 through 70, Milltap 700."),
            ("SPRINT / MULTISPRINT",     "/spindle-grinding/dmg-mori-spindle-repair/sprint-multisprint/",
             "Swiss-style and production turning spindles. SPRINT 20/32/50/65, MULTISPRINT 25/36."),
        ],
        "browse_control": [
            ("Siemens 840D",   "/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/",
             "Most DMG Mori platforms. Spindle parameters live at the 840D layer; documented backup workflow."),
            ("Heidenhain TNC", "/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/",
             "Common on DMU/DMC 5-axis. Heidenhain spindle parameter workflow differs from Siemens."),
            ("CELOS",          "/spindle-grinding/dmg-mori-spindle-repair/celos/",
             "DMG Mori HMI on top of Siemens or Heidenhain. Spindle monitoring integration via MTConnect."),
        ],
        "browse_service": [
            ("DMG Mori machine repair",        "/repairs/dmg-mori-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-spindle DMG Mori service work."),
            ("DMG Mori way covers",            "/way-covers/dmg-mori-cnc-way-covers/",
             "Replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work", "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What spindle work do you do on DMG Mori machines?",
             "Bearing-pack replacement, taper grinding, dynamic balancing, encoder service. For DMU 5-axis and NTX multitasking, RTCP and B-axis kinematic verification are part of every rebuild. Runout and balance verification at sign-off is part of every rebuild."),
            ("How long does a DMG Mori spindle rebuild take?",
             "3 to 5 weeks on most jobs. NTX B-axis milling spindle rebuilds run longer because of the multitasking kinematic verification overhead. DMU 5-axis trunnion-machine rebuilds also run a bit longer for the same reason."),
            ("Do you service spindles on machines with original Siemens 840D versus solutionline?",
             "Yes to both. Spindle drive parts on solutionline are fully current; original 840D drives are heading toward late-life but still serviceable. The control-side conversation differs slightly — solutionline parameter backup is network-based; original 840D may need CF-card-based workflow."),
            ("What about Heidenhain TNC on DMU and DMC machines?",
             "Heidenhain spindle parameter workflow is different from Siemens. Tool tables and spindle-specific parameters back up to network or USB before any work. After spindle work on a DMU 5-axis we run the documented Heidenhain kinematic verification before sign-off."),
            ("Can you grind DMG Mori spindle tapers back to factory tolerance?",
             "Yes. Precision spindle grinding to restore runout is part of every rebuild where the taper shows wear. Common on DMU machines that have seen toolholder issues during 5-axis cuts."),
            ("Do NTX B-axis milling spindles need special attention?",
             "Yes. NTX multitasking tolerances are tighter than on straight verticals because mill-turn work requires angular alignment. After-spindle B-axis kinematic verification is mandatory — that's part of the rebuild, not a separate quote."),
        ],
        "series_spokes":  _DMG_MORI_SPINDLE_SERIES_SPOKES,
        "control_spokes": _DMG_MORI_SPINDLE_CONTROL_SPOKES,
        "hero_lede": "DMG Mori spindle service across the Midwest — NLX and CTX turning spindles, NTX mill-turn with B-axis verification, DMU and DMC 5-axis with RTCP verification, NHX horizontals, NVX verticals, and the CMX/DMP/SPRINT production lines. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most DMG Mori spindle calls fall into a few patterns: bearing-pack wear on NLX and CTX turning, B-axis milling spindle wear on NTX multitasking, RTCP-related work on DMU 5-axis post-crash, pallet-cycle bearing wear on NHX horizontals, and high-RPM bearing failure on NVX aluminum work. Control-side, spindle parameters live at the Siemens 840D layer for most machines or Heidenhain TNC on DMU lines; CELOS adds the monitoring integration on top.",
        "how_we_approach": "DMG Mori spindle service starts with confirming the platform and the underlying control. For DMU 5-axis and NTX multitasking, post-rebuild kinematic verification is mandatory — we don't hand back without it. On the bench: teardown, bearing inspection, taper evaluation, parts sourcing, rebuild, balance, runout verification with photo at sign-off.",
        "browse_control_intro": "DMG Mori spindles pair with Siemens 840D, Heidenhain TNC, or both, all wrapped in CELOS. Pick the control for spindle parameter-management considerations.",
    },

    "doosan": {
        "browse_series": [
            ("Puma",                       "/spindle-grinding/doosan-spindle-repair/puma/",
             "Horizontal-turning spindles. Puma 230 through 800 with M/MS/LM/Y/SY variants and TT/GT/TW builds."),
            ("Puma MX / SMX",              "/spindle-grinding/doosan-spindle-repair/puma-mx-smx/",
             "Mill-turn multitasking spindles. Turning + B-axis milling — MX 1600 through 3100, SMX 2100/2600/3100."),
            ("Puma V / VT / VTR",          "/spindle-grinding/doosan-spindle-repair/puma-vertical-turning/",
             "Vertical-turning spindles. Puma V400 through V9300 chuckers and VT/VTR ram-type."),
            ("Lynx",                       "/spindle-grinding/doosan-spindle-repair/lynx/",
             "Compact turning spindles. Lynx 220 through 300, high-cycle bar work."),
            ("DNM",                        "/spindle-grinding/doosan-spindle-repair/dnm-verticals/",
             "Vertical-machining spindles. DNM 200 through 750 plus DNM 200/5AX 5-axis."),
            ("Horizontals (NHM / NHP / HC)","/spindle-grinding/doosan-spindle-repair/horizontals/",
             "Horizontal spindles. NHM 4000 through 8000, NHP 4000 through 6300, HC 400/500."),
            ("DVF / FM 5-Axis Verticals",  "/spindle-grinding/doosan-spindle-repair/5-axis-verticals/",
             "5-axis trunnion vertical spindles. DVF 5000/6500/8000 and FM 200/5AX. RTCP verification."),
            ("Swiss-Type / DST",           "/spindle-grinding/doosan-spindle-repair/swiss-turning/",
             "Swiss-style precision turning. SwiftTurn 32/38 and DST series."),
        ],
        "browse_control": [
            ("Fanuc 0i (Doosan)",  "/spindle-grinding/fanuc-spindle-repair/series-0i/",
             "Entry and mid-range Doosan. Most Lynx and entry Puma builds. αi-class spindle drives, well supported."),
            ("Fanuc 30i (Doosan)", "/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/",
             "Higher-end Puma, MX/SMX, DVF, NHM. αii-class spindle drives, fully current."),
        ],
        "browse_service": [
            ("Doosan machine repair",         "/repairs/doosan-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-spindle Doosan service work."),
            ("Doosan way covers",             "/way-covers/doosan-cnc-way-covers/",
             "Replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work","#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What spindle work do you do on Doosan machines?",
             "Bearing-pack replacement, taper grinding, dynamic balancing, drawbar service, encoder service. For Puma MX/SMX multitasking we also run B-axis kinematic verification; for DVF 5-axis we run RTCP verification. Runout and balance verification at sign-off is part of every rebuild."),
            ("How long does a Doosan spindle rebuild take?",
             "3 to 5 weeks on most jobs. Puma MX/SMX B-axis milling spindle rebuilds run longer because of the multitasking kinematic verification. DVF 5-axis trunnion-machine rebuilds also run a bit longer for the RTCP work."),
            ("Doosan ships on Fanuc — what does that mean for spindle service?",
             "It means spindle parameters live in the Fanuc parameter set, and the workflow follows the standard Fanuc backup procedures. For Lynx and entry Puma we work with Fanuc 0i; for higher-end Puma MX/SMX/DVF we work with Fanuc 30i. The αi and αii spindle drive families are well documented."),
            ("Do you service older Doosan machines with Fanuc 16i/18i/21i controls?",
             "Yes. Those machines run the αi spindle drive generation which is still well supported through Fanuc. PCMCIA media migration to current paths is often a companion job to spindle service."),
            ("What about Puma MX/SMX B-axis milling spindles?",
             "B-axis milling spindle rebuilds are routine work. Multitasking tolerances require careful B-axis kinematic verification after spindle work — we run the verification before sign-off."),
            ("Can you grind Doosan spindle tapers back to factory tolerance?",
             "Yes. Precision spindle grinding to restore runout is part of every rebuild where the taper shows wear."),
        ],
        "series_spokes":  _DOOSAN_SPINDLE_SERIES_SPOKES,
        "control_spokes": {},  # Doosan controls cross-link to canonical Fanuc spindle spokes
        "hero_lede": "Doosan and DN Solutions spindle service across the Midwest — Puma horizontal turning spindles, Lynx compact lathe spindles, DNM vertical spindles, NHM horizontal spindles, DVF 5-axis with RTCP verification, and the multitasking Puma MX/SMX B-axis milling spindles. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Doosan spindle calls fall into a few patterns: front bearing wear on Puma and Lynx chuckers from bar-feed production, B-axis milling spindle wear on Puma MX/SMX multitasking, high-RPM bearing failure on DNM finishing work, pallet-cycle bearing wear on NHM horizontals, and RTCP work on DVF 5-axis. Control-side, Doosan ships almost exclusively on Fanuc — most service runs against Fanuc 0i for entry builds and Fanuc 30i for higher-end multitasking and 5-axis.",
        "how_we_approach": "Doosan spindle service starts with the platform and the paired Fanuc control. Lynx and entry Puma run Fanuc 0i; higher-end Puma, MX/SMX, DVF, NHM run Fanuc 30i. Spindle parameters back up via standard Fanuc procedures. For multitasking and 5-axis platforms, post-rebuild kinematic verification is part of the service.",
        "browse_control_intro": "Doosan ships almost exclusively on Fanuc. Pick the Fanuc generation your Doosan machine runs for spindle parameter-management considerations.",
    },

    "okuma": {
        "browse_series": [
            ("LB / LU Lathes",                "/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/",
             "Horizontal lathe spindles. LB 200 through 5000 EX, LU 300 through 8000, live-tool variants."),
            ("Genos",                         "/spindle-grinding/okuma-spindle-repair/genos/",
             "'Affordable Excellence' spindles. Genos L250 through L4000 lathes, M460/M560/M660 verticals."),
            ("MB / MA Verticals",             "/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/",
             "Vertical-machining workhorse spindles. MB-46V through MB-66V, MA-400 through MA-8000."),
            ("MULTUS",                        "/spindle-grinding/okuma-spindle-repair/multus/",
             "B-axis multitasking spindles. MULTUS B200 through B750, U3000 through U5000."),
            ("Twin-Spindle / Twin-Turret",    "/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/",
             "2SP-2500H, 2SP-V40, LT 200-MY through LT 2000 EX, historic LT-15/25."),
            ("VTM Vertical Turning",          "/spindle-grinding/okuma-spindle-repair/vtm/",
             "Large vertical-turning spindles. VTM-65, VTM-100, VTM-120, VTM-180."),
            ("MU 5-Axis / MCR Bridge",        "/spindle-grinding/okuma-spindle-repair/v-bridge-mills/",
             "5-axis trunnion (MU-400V through MU-8000V) and bridge mills (MCR-A5C, MCR-BIII)."),
            ("LAW / LFS Heavy Lathes",        "/spindle-grinding/okuma-spindle-repair/heavy-lathes/",
             "Heavy-duty turning spindles. LAW 1000 through 3000 and LFS-590 flat-bed turning."),
        ],
        "browse_control": [
            ("OSP-P200",   "/spindle-grinding/okuma-spindle-repair/osp-p200/",
             "Late-life Okuma. Spindle drive parts still serviceable; HDD/MMC companion work common."),
            ("OSP-P300",   "/spindle-grinding/okuma-spindle-repair/osp-p300/",
             "Mid-life Okuma. SSD upgrade companion service; touchscreen workflow for spindle setup."),
            ("OSP-P500",   "/spindle-grinding/okuma-spindle-repair/osp-p500/",
             "Current Okuma. Network parameter backup, MTConnect spindle monitoring integration."),
            ("OSP Legacy", "/spindle-grinding/okuma-spindle-repair/osp-legacy/",
             "Pre-2003. Heavy parts-availability conversation; retrofit territory on some builds."),
        ],
        "browse_service": [
            ("Okuma machine repair",          "/repairs/okuma-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-spindle Okuma service work."),
            ("Okuma way covers",              "/way-covers/okuma-cnc-way-covers/",
             "Replacement bellows, telescoping steel, and roll-up covers, built to spec."),
            ("ATC, drive, and alignment work","#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What spindle work do you do on Okuma machines?",
             "Bearing-pack replacement, taper grinding, dynamic balancing, drawbar service, encoder service. For MULTUS multitasking we run B-axis kinematic verification; for MU 5-axis we run RTCP verification; for MCR bridge mills we run bridge geometry verification. Runout and balance verification at sign-off is part of every rebuild."),
            ("How long does an Okuma spindle rebuild take?",
             "3 to 5 weeks on most jobs. MULTUS B-axis milling spindle rebuilds and MU 5-axis trunnion rebuilds run a bit longer because of the post-rebuild kinematic verification."),
            ("Okuma builds spindles in-house — does that matter for service?",
             "It matters in that Okuma's thermal compensation and bearing-pack designs are documented and well understood, which makes the diagnostic side faster. The actual bench work is similar to any quality spindle — teardown, inspect, source parts, rebuild, balance, verify."),
            ("Do you service older Okuma machines with OSP Legacy or OSP-P200 controls?",
             "Yes to both. OSP Legacy spindle service becomes a parts-availability conversation — some bearings and drive amplifiers are aftermarket-only. P200 is late-life but still well serviced; spindle drive parts are still mostly available through Okuma channels."),
            ("Can you grind Okuma spindle tapers back to factory tolerance?",
             "Yes. Precision spindle grinding to restore runout is part of every rebuild where the taper shows wear."),
            ("What about MULTUS B-axis milling spindles?",
             "B-axis milling spindle rebuilds are routine work on MULTUS. Multitasking tolerances require careful B-axis kinematic verification — that's part of the service, not a separate quote."),
        ],
        "series_spokes":  _OKUMA_SPINDLE_SERIES_SPOKES,
        "control_spokes": _OKUMA_SPINDLE_CONTROL_SPOKES,
        "hero_lede": "Okuma spindle service across the Midwest — LB and LU horizontal lathe spindles, MB and MA vertical spindles, MULTUS multitasking B-axis spindles, MU 5-axis with RTCP verification, MCR bridge-mill spindles, and the heavy LAW lathe spindles. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Okuma spindle calls fall into a few patterns: bearing-pack wear on LB and LU lathes from sustained production, ATC and spindle wear on MB and MA verticals, B-axis milling spindle wear on MULTUS multitasking, RTCP-related work on MU 5-axis post-crash, large-bore spindle work on LAW heavy lathes. Control-side, spindle parameter management is straightforward on P200 and P300; P500 adds network-based backup; OSP Legacy is the harder conversation because of parts.",
        "how_we_approach": "Okuma spindle service starts with the platform and the OSP generation. For MULTUS and MU multitasking/5-axis, post-rebuild kinematic verification is mandatory. On the bench: Okuma's documented bearing-pack designs help diagnostic speed; teardown, inspect, source parts, rebuild, balance, verify runout with photo at sign-off.",
        "browse_control_intro": "Okuma spindles pair with four OSP control generations. Pick yours for spindle parameter-management considerations.",
    },

    "fanuc": {
        "browse_series": [
            ("Doosan / DN Solutions", "/spindle-grinding/doosan-spindle-repair/",
             "Most Doosan lathes and verticals ship on Fanuc 0i or 30i with αi-class spindle drives."),
            ("Haas (older)",          "/spindle-grinding/haas-spindle-repair/",
             "Some older Haas imports shipped with Fanuc controls before NGC."),
        ],
        "browse_series_header": "Brands that ship Fanuc controls",
        "browse_series_intro": "Fanuc is primarily a controls vendor — your spindle is in a machine built by one of these OEMs and uses a Fanuc-paired spindle drive. Pick the brand for series-specific spindle notes, or pick a Fanuc generation below for control-side considerations.",
        "browse_control": [
            ("Series 0 / 0M / 0T (Pre-i Legacy)", "/spindle-grinding/fanuc-spindle-repair/series-0-legacy/",
             "1980s-1990s. Bubble memory affects spindle parameters; drive amplifiers heavily aftermarket."),
            ("Series 6 / 10 / 11 / 12 / 15",      "/spindle-grinding/fanuc-spindle-repair/series-6-15-legacy/",
             "1980s-2000s. Similar to Series 0; Series 15 still active on larger machines."),
            ("Series 16i / 18i / 21i",            "/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/",
             "1995-2010. αi spindle drives — most common on mid-life machines. Well documented."),
            ("Series 0i (A/B/C/D/F)",             "/spindle-grinding/fanuc-spindle-repair/series-0i/",
             "2003-present. Ubiquitous. αi-class drives, well supported across the entire fleet."),
            ("Series 30i / 31i / 32i / 35i",      "/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/",
             "2008-present. αii-class drives. Network parameter backup, FOCAS integration."),
            ("Power Mate i",                      "/spindle-grinding/fanuc-spindle-repair/power-mate-i/",
             "Dedicated-axis / sub-spindle / rotary indexer. Drive amplifier and encoder work."),
        ],
        "browse_service": [
            ("Spindle drive amplifier repair", "#faq",
             "Board-level Fanuc spindle drive work — αi, αii, and legacy generations. Covered in the FAQ."),
            ("Spindle parameter backup",       "#faq",
             "Parameter recovery procedures and backup discipline — covered in the FAQ."),
            ("PCMCIA media migration",         "#faq",
             "Migrating 16i/18i/21i spindle-related media to current paths — covered in the FAQ."),
        ],
        "faq": [
            ("Why is the Fanuc spindle page structured differently?",
             "Fanuc is primarily a controls vendor — the spindle in your machine sits in a chassis built by Doosan, Haas, or another OEM, but the spindle drive is part of the Fanuc-paired system. Our Fanuc spindle hub is organized by control + drive generation rather than machine series because that's the right diagnostic lens for Fanuc spindle service."),
            ("Which Fanuc generation do you see most often?",
             "Series 0i (specifically 0i-D and 0i-F) is by far the most common Fanuc spindle setup on Midwest shop floors. Series 16i/18i/21i is the second-most-common — many late-1990s through 2000s machines still in production with αi spindle drives. Series 30i is growing as those builds age into routine service."),
            ("Do you do board-level Fanuc spindle drive repair?",
             "Yes. Fanuc spindle service is often board-level — αi and αii drive amplifiers, encoder feedback boards, spindle control modules. We work through remanufacturing specialists on boards that have gone out of OEM supply, and through Fanuc channels for current-generation parts."),
            ("Can you migrate a 16i/18i/21i machine from PCMCIA media during spindle service?",
             "Yes. PCMCIA-to-CF or PCMCIA-to-USB media migration is a routine companion job when a machine comes in for spindle service. Documenting the spindle-related programs and parameters is part of the migration."),
            ("How does spindle service work on a Doosan or Haas machine with Fanuc controls?",
             "We handle the spindle hardware the same way — teardown, bearing inspection, taper evaluation, rebuild, balance, runout verification. The Fanuc-specific work is on the control side: parameter capture before any work, drive amplifier diagnostic, encoder verification, parameter restore at sign-off."),
            ("Do you service Fanuc-controlled machines outside Iowa?",
             "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. For board-level Fanuc spindle drive work, ship-in to our Waterloo facility is usually the right path."),
        ],
        "series_spokes":  {},  # Fanuc flips structure — no series spokes
        "control_spokes": _FANUC_SPINDLE_CONTROL_SPOKES,
        "hero_lede": "Fanuc is primarily a controls vendor — your spindle is in a machine built by Doosan, Haas, or another OEM and uses a Fanuc-paired spindle drive (αi-class on mid-life machines, αii-class on current). We service the full Fanuc spindle drive family from deep-legacy Series 0 through current 0i-F and 30i-B. Find your control below, or browse by service type.",
        "what_brings": "Most Fanuc spindle service splits between three patterns. Deep-legacy Series 0, 6-15 — board-level work through remanufacturing specialists on older spindle drive amplifiers. Mid-life Series 16i/18i/21i — αi drive amplifier service, PCMCIA media migration, battery and parameter recovery. Current Series 0i and 30i — αi/αii drive service, network-based parameter backup, FOCAS integration for spindle monitoring. The diagnostic lens is the control + drive generation, not the machine.",
        "how_we_approach": "Fanuc spindle service starts with confirming the generation. From there it's a fork: legacy generations (Series 0 through Series 15) go through board-level repair or remanufacturing for the spindle drive amplifier; mid-life 16i/18i/21i is αi drive service and parts availability; current 0i and 30i is mostly software, networking, and αi/αii drive verification.",
        "browse_control_intro": "Fanuc spans six control generations from the early 1980s through current production. Pick yours for spindle drive parts availability and parameter-management considerations.",
    },
}
