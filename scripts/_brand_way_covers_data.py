"""Way-covers hub-and-spoke content for the 6 priority brands.

Same structural pattern as SPINDLE_HUB_DATA / BRAND_HUB_DATA. Per-spoke
content focuses on what's UNIQUE about way-covers work for each
series / control generation:

  - Cover style selection per series (bellows / telescoping steel / roll-up)
  - Dimensional and clearance considerations per platform
  - OEM-spec availability vs custom fabrication
  - Sealing and chip / coolant intrusion patterns per orientation
  - Pallet-changer / trunnion / multi-axis interface considerations
  - Era + parts availability per control generation (control spokes)

Voice match: measured, no hype, no claim-audit ban-list phrases.
"""

# ============================================================
# Compact builders to keep this file readable
# ============================================================
def _wc_series(brand_slug, slug, title_suffix, subtitle, intro, considerations, sourcing, siblings):
    return {
        "title":   f"{brand_slug.replace('-', ' ').title().replace('Dmg ', 'DMG ').replace('Mori', 'Mori')} {title_suffix} Way Covers",
        "slug":    f"{brand_slug}-way-covers-{slug}",
        "subtitle":subtitle,
        "url":     f"/way-covers/{brand_slug}-cnc-way-covers/{slug}/",
        "intro":   intro,
        # Re-purpose 'failures' field as 'considerations' for the way covers
        # template — generic render_series_spoke uses the failures slot, so
        # we keep the data shape but the content is configuration/sizing
        # considerations rather than failure modes.
        "failures": considerations,
        "controls_paragraph": sourcing,
        "siblings": siblings,
    }


def _wc_control(brand_slug, slug, title_suffix, subtitle, era, intro, machines_paragraph, considerations, sourcing, custom_fab, siblings):
    return {
        "title":   f"Way Covers for {title_suffix} Era Machines",
        "slug":    f"{brand_slug}-way-covers-{slug}",
        "subtitle":subtitle,
        "url":     f"/way-covers/{brand_slug}-cnc-way-covers/{slug}/",
        "era":     era,
        "intro":   intro,
        "machines_paragraph": machines_paragraph,
        "failures": considerations,
        "parts_paragraph": sourcing,
        "recovery_paragraph": custom_fab,
        "siblings": siblings,
    }


# ============================================================
# MAZAK WAY COVERS
# ============================================================
_MAZAK_WC_SERIES_SPOKES = {
    "quick-turn": _wc_series(
        "mazak", "quick-turn", "Quick Turn", "Quick Turn / QTN",
        "Quick Turn lathe way covers protect the slant-bed ways from chip and coolant ingress. The QT and QTN series uses telescoping-steel covers on most models — they handle the heavy chip load that comes off turning operations better than bellows. Cover dimensions scale with bed size: QT-8 through QT-15 use compact configurations; QTN-300 and larger have longer ways and matching covers. We fabricate to spec from your existing cover, the original drawing, or measurements off the machine.",
        [
            "Telescoping steel is the default cover style for Quick Turn — handles turning-chip loads better than bellows.",
            "MS and MSY twin-spindle variants have additional sub-spindle ways requiring matching cover sets.",
            "Long-bed QTN-300 through QTN-450 covers are larger and require accurate measurement of the way travel.",
            "Y-axis variants (QT and QTN with Y) add an additional axis cover.",
            "Bar-feed and parts-catcher mounting can interfere with cover paths — confirm clearances during quoting.",
        ],
        "Older Quick Turn covers are typically OEM-discontinued; current Compact, Smart, and Ultra models still have OEM-spec replacements available through Mazak channels. We can match either path — build to your exact spec or replicate the OEM original. Lead time is 2 to 4 weeks on most orders regardless of the path.",
        [
            ("Mazak Integrex way covers",          "/way-covers/mazak-cnc-way-covers/integrex/"),
            ("Mazak Turning Legacy way covers",    "/way-covers/mazak-cnc-way-covers/turning-legacy/"),
        ],
    ),
    "integrex": _wc_series(
        "mazak", "integrex", "Integrex", "Integrex Mill-Turn",
        "Integrex multitasking machines have more way coverage requirements than straight lathes or vertical mills — turning ways, B-axis mill-spindle traverse, sub-spindle ways on twin-spindle variants. Cover configurations are more complex on Integrex platforms and the clearance constraints around the B-axis and tool magazine are tighter. We fabricate the full set or individual covers as needed.",
        [
            "B-axis milling spindle traverse covers — telescoping or bellows depending on travel and clearance.",
            "Turning spindle ways — telescoping steel is standard on most Integrex configurations.",
            "Sub-spindle ways on i-200ST, i-300ST, i-400ST, and e-series with sub-spindle.",
            "Tool magazine interface clearances — confirm during quoting because OEM dimensions can drift after a crash.",
            "Y-axis cover on Integrex variants with Y-axis (i-200SY, i-300SY, etc.).",
        ],
        "Integrex i-series originals are increasingly OEM-discontinued; current i-H, i-V, and e-V/10 builds still have OEM-spec available. Custom fabrication to your exact spec covers either case. Lead time is 2 to 4 weeks; complex multi-cover sets for full machine coverage can run slightly longer.",
        [
            ("Mazak Variaxis way covers",    "/way-covers/mazak-cnc-way-covers/variaxis/"),
            ("Mazak Quick Turn way covers",  "/way-covers/mazak-cnc-way-covers/quick-turn/"),
        ],
    ),
    "variaxis": _wc_series(
        "mazak", "variaxis", "Variaxis", "Variaxis 5-Axis",
        "Variaxis 5-axis trunnion-table covers are among the more demanding fabrication jobs in the Mazak lineup. The trunnion adds rotational clearance constraints; the X/Y/Z way covers have to clear the rotating workpiece envelope. We typically build telescoping steel for the linear axes and either bellows or roll-up for the trunnion-adjacent areas depending on the specific machine.",
        [
            "X/Y/Z linear-axis covers — telescoping steel handles the chip load from 5-axis cuts.",
            "Trunnion-adjacent covers may use bellows or roll-up depending on clearance to rotating workpiece envelope.",
            "i-300 through i-800 builds have different way-travel dimensions — confirm during quoting.",
            "J-series and C-series compact builds have tighter clearance constraints than the i-series.",
            "Legacy Variaxis 500/630/730 covers are almost always custom fabrication at this point.",
        ],
        "Current Variaxis i-series covers are still OEM-available through Mazak; legacy 500/630/730 are typically OEM-discontinued. We build to your exact spec from the original cover, the OEM drawing, or measurements off the machine. Lead time is 2 to 4 weeks.",
        [
            ("Mazak Integrex way covers",       "/way-covers/mazak-cnc-way-covers/integrex/"),
            ("Mazak VTC + VCN way covers",      "/way-covers/mazak-cnc-way-covers/vertical-machining-centers/"),
        ],
    ),
    "vertical-machining-centers": _wc_series(
        "mazak", "vertical-machining-centers", "VTC + VCN", "VTC + VCN Verticals",
        "VTC and VCN production vertical covers are the highest-volume Mazak way-cover orders we see. Both families use telescoping steel on the X and Y ways as the default; the Z-axis spindle column on some VCN configurations uses bellows for vertical drop coverage. VTC long-bed builds (VTC-800) have longer X-axis covers than the production VCNs.",
        [
            "X/Y telescoping steel covers — production-vertical chip load handles best on telescoping designs.",
            "Z-axis spindle column covers on some VCN configurations — bellows or fabric depending on the build.",
            "Long-bed VTC-800 has substantially longer covers than VCN-410/510/530 — confirm bed size during quoting.",
            "VCN-Compact has tighter clearance constraints than full-size VCN.",
            "Way damage from chip ingress is common on machines without proper sealing — replacement is often the cleanest fix.",
        ],
        "Current VCN-510C, VCN-530C, VCN-700, VCN-Compact, and VTC-800 covers are OEM-available through Mazak; older VTC and VCN builds increasingly require custom fab. Lead time is 2 to 4 weeks regardless of path. The FJV and AJV legacy verticals are custom-only at this point.",
        [
            ("Mazak HCN Horizontal way covers",  "/way-covers/mazak-cnc-way-covers/hcn-horizontal/"),
            ("Mazak Variaxis way covers",        "/way-covers/mazak-cnc-way-covers/variaxis/"),
        ],
    ),
    "hcn-horizontal": _wc_series(
        "mazak", "hcn-horizontal", "HCN Horizontal", "HCN Horizontals",
        "HCN horizontal way covers have to account for the pallet-changer interface on top of the standard X/Y/Z protection. The horizontal orientation works in the covers' favor for chip drainage — fluid and chips don't pool the way they can on verticals — but the pallet-changer sealing area is where most cover wear shows up. We fabricate the linear-axis covers plus pallet-interface seals as a coordinated set.",
        [
            "X/Y/Z linear-axis covers — telescoping steel is standard for the horizontal chip and coolant loads.",
            "Pallet-changer interface sealing — the most common wear point on HCN platforms.",
            "B-axis indexer interface clearances — confirm during quoting.",
            "HCN-8800 and HCN-10800 large-platform covers are substantially larger than HCN-4000 through HCN-6000.",
            "Legacy PFH and H-series covers are almost always custom fabrication at this point.",
        ],
        "Current HCN-4000 through HCN-10800 covers are OEM-available through Mazak; legacy PFH and H-series are custom-only. Lead time is 2 to 4 weeks. We can build complete cover sets including the pallet-interface seals as a coordinated package.",
        [
            ("Mazak VTC + VCN way covers",  "/way-covers/mazak-cnc-way-covers/vertical-machining-centers/"),
            ("Mazak Integrex way covers",   "/way-covers/mazak-cnc-way-covers/integrex/"),
        ],
    ),
    "turning-legacy": _wc_series(
        "mazak", "turning-legacy", "Turning Legacy", "Slant Turn / Multiplex / Megaturn",
        "Mazak's turning legacy platforms — Slant Turn, Multiplex, Megaturn, HQR, Powermaster — are almost always custom-fabrication for way covers in 2026. The OEM has discontinued most original cover part numbers, so we build to spec from your existing cover, the original drawing, or measurements off the machine. The fabrication itself is straightforward; the time-consuming part is getting accurate measurements from a machine that's been in production for 25+ years.",
        [
            "Telescoping steel is the default on Slant Turn and Multiplex platforms.",
            "Megaturn vertical-turning covers use different geometry — confirm style during quoting.",
            "HQR-150 through HQR-250 have similar dimensions to current Quick Turn but with legacy-spec mounting.",
            "Confirm way-travel dimensions carefully on machines that have been re-mounted or moved.",
            "Original mounting hardware is sometimes unavailable — we'll match or provide replacement hardware as part of the build.",
        ],
        "OEM-spec covers for the turning legacy family are almost universally discontinued. Custom fabrication to your existing cover, original drawing, or machine measurements is the standard path. Lead time is 2 to 4 weeks; complex multi-axis legacy machines may run slightly longer if measurements need to be coordinated.",
        [
            ("Mazak Quick Turn way covers",          "/way-covers/mazak-cnc-way-covers/quick-turn/"),
            ("Mazak VTC + VCN way covers",           "/way-covers/mazak-cnc-way-covers/vertical-machining-centers/"),
        ],
    ),
}

_MAZAK_WC_CONTROL_SPOKES = {
    "mazatrol-legacy": _wc_control(
        "mazak", "mazatrol-legacy", "Mazatrol Legacy", "Mazatrol Legacy",
        "Roughly 1981 through 2005",
        "Way covers on Mazatrol Legacy era machines — M-2, M-32, M-Plus, Fusion 640 — are almost always custom-fabrication in 2026. The machines are mechanically sound and still in production, but OEM cover part numbers have largely been discontinued. We build to spec from your existing cover, the original Mazak drawing if you still have it, or measurements off the machine.",
        "Mazatrol Legacy machines include older [Quick Turn](/way-covers/mazak-cnc-way-covers/quick-turn/) lathes (pre-Nexus), the [Turning Legacy](/way-covers/mazak-cnc-way-covers/turning-legacy/) platforms (Slant Turn, Multiplex 6000, Megaturn, HQR), legacy [Vertical Machining Centers](/way-covers/mazak-cnc-way-covers/vertical-machining-centers/) (VTC legacy, FJV, AJV), and the [HCN horizontals'](/way-covers/mazak-cnc-way-covers/hcn-horizontal/) PFH and H-series predecessors.",
        [
            "Telescoping steel is the default for legacy Mazatrol turning machines.",
            "Bellows on some legacy vertical-machine Z-axis configurations.",
            "Original mounting hardware is sometimes unavailable — replacement hardware as part of the build.",
            "Measurement coordination from an aging machine requires confirming way travel hasn't drifted from spec.",
        ],
        "OEM-spec way covers for Mazatrol Legacy era machines are mostly discontinued. Custom fabrication is the standard path. We can build to your existing cover, the original OEM drawing, or measurements taken off the machine.",
        "When the original cover is too damaged to measure from, we work from the OEM drawing if available, or measure the ways directly from the machine. Way-travel dimensions should be confirmed in case the machine has been moved or re-shimmed since original installation. Lead time is 2 to 4 weeks once measurements are confirmed.",
        [
            ("Mazatrol Matrix era way covers",  "/way-covers/mazak-cnc-way-covers/mazatrol-matrix/"),
            ("Mazatrol Smooth era way covers",  "/way-covers/mazak-cnc-way-covers/smooth-control/"),
        ],
    ),
    "mazatrol-matrix": _wc_control(
        "mazak", "mazatrol-matrix", "Mazatrol Matrix", "Mazatrol Matrix",
        "Roughly 2005 through 2013",
        "Matrix-era Mazak machines split the way-cover parts situation roughly down the middle in 2026. Some OEM-spec covers are still available through Mazak channels; others have been discontinued and require custom fabrication. We check OEM availability before quoting and route to whichever path makes sense for the specific machine and cover.",
        "Matrix machines include [Quick Turn Nexus](/way-covers/mazak-cnc-way-covers/quick-turn/) (QTN-100 through QTN-450), original [Integrex](/way-covers/mazak-cnc-way-covers/integrex/) i-series, [Vertical Machining Centers](/way-covers/mazak-cnc-way-covers/vertical-machining-centers/) (VTC-200 through VTC-800, VCN-410 through VCN-530), [HCN-4000 through HCN-6000](/way-covers/mazak-cnc-way-covers/hcn-horizontal/), and the [Multiplex 6100](/way-covers/mazak-cnc-way-covers/turning-legacy/) generation.",
        [
            "Telescoping steel covers are the default on most Matrix-era machines.",
            "Bellows on some Z-axis configurations and Variaxis trunnion-adjacent areas.",
            "OEM-original vs custom-fab decision depends on the specific cover and machine — we check availability before quoting.",
            "Dimensions are well documented on Matrix-era machines — measurement coordination is easier than on legacy.",
        ],
        "Some Matrix-era way covers are still OEM-available through Mazak channels; others are discontinued and require custom fabrication. The split has been shifting toward custom-fab over the past several years as inventory thins.",
        "When OEM-spec is available we route to that path; when it's not we build to spec from your existing cover or the OEM drawing. Mounting hardware is typically still available for Matrix-era machines so the build slots into existing hardware without adapter work. Lead time is 2 to 4 weeks.",
        [
            ("Mazatrol Legacy era way covers",  "/way-covers/mazak-cnc-way-covers/mazatrol-legacy/"),
            ("Mazatrol Smooth era way covers",  "/way-covers/mazak-cnc-way-covers/smooth-control/"),
        ],
    ),
    "smooth-control": _wc_control(
        "mazak", "smooth-control", "Mazatrol Smooth", "Mazatrol Smooth",
        "2013 through present",
        "Smooth-era Mazak way covers are fully OEM-supported through Mazak channels. Most replacements run through that path because the dimensions are current-spec and OEM hardware is available. We can build to OEM spec or fabricate custom alternatives where the OEM lead time or pricing makes custom the better choice.",
        "Smooth-era machines include current [Integrex](/way-covers/mazak-cnc-way-covers/integrex/) (i-H, i-V, e-V/10), current [Variaxis](/way-covers/mazak-cnc-way-covers/variaxis/) i-series, [VTC-800 and current VCN](/way-covers/mazak-cnc-way-covers/vertical-machining-centers/), current [HCN-8800 and HCN-10800](/way-covers/mazak-cnc-way-covers/hcn-horizontal/), and current [Quick Turn](/way-covers/mazak-cnc-way-covers/quick-turn/) Compact, Smart, Primos, Ez, and Ultra.",
        [
            "Most Smooth-era machines have OEM-spec covers available through Mazak channels.",
            "Telescoping steel is the default on most platforms; bellows on specific Variaxis and Z-axis configurations.",
            "Dimensions are documented and current — measurement coordination is straightforward.",
            "OEM lead time can sometimes exceed our custom-fab lead time — we'll let you know during quoting.",
        ],
        "Smooth-era way cover parts are fully OEM-supported through Mazak channels. Custom fabrication is an option when OEM lead time or pricing makes that the better path.",
        "For Smooth-era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. We can quote either way and recommend based on the specifics. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("Mazatrol Matrix era way covers",  "/way-covers/mazak-cnc-way-covers/mazatrol-matrix/"),
            ("Mazatrol Legacy era way covers",  "/way-covers/mazak-cnc-way-covers/mazatrol-legacy/"),
        ],
    ),
}


# ============================================================
# HAAS WAY COVERS
# ============================================================
_HAAS_WC_SERIES_SPOKES = {
    "vf-series": _wc_series(
        "haas", "vf-series", "VF Series", "VF Series Vertical Mills",
        "VF series way covers are the highest-volume Haas way-cover orders. The line uses telescoping steel for the X and Y ways across all configurations; the Z-axis is internal on most VF machines so it doesn't typically need separate cover work. Cover dimensions scale with bed size: VF-1 and VF-2 use compact configurations; VF-5 through VF-12 have substantially longer ways. SS (Super Speed) variants use the same cover dimensions as base machines.",
        [
            "X/Y telescoping steel covers — standard across the VF series.",
            "VF-2YT and VF-3YT extended-Y variants have longer Y-axis covers than the base machines.",
            "VFEXT extended-Z variants — Z-axis is internal but still confirm during quoting.",
            "Trunnion table covers on VF machines with rotary trunnion adders.",
            "Way damage from chip ingress is common on machines running heavy aluminum production — replacement is often cleanest.",
        ],
        "Most VF series way covers are OEM-available through Haas. Custom fabrication is an option when timing or specific clearance requirements make that the better path. Lead time is 2 to 4 weeks.",
        [
            ("Haas UMC Series way covers",  "/way-covers/haas-cnc-way-covers/umc-series/"),
            ("Haas ST Series way covers",   "/way-covers/haas-cnc-way-covers/st-series/"),
        ],
    ),
    "st-series": _wc_series(
        "haas", "st-series", "ST Series", "ST Series Lathes",
        "ST series lathe way covers protect the slant-bed ways from chip and coolant. Telescoping steel is the default cover style across the line. Smaller ST-10 and ST-20 chuckers use compact configurations; ST-30 and larger have longer ways. SSY Y-axis variants add an additional Y-axis cover; DS-30 dual-spindle adds sub-spindle ways requiring a matching cover set.",
        [
            "Telescoping steel covers are standard across the ST series.",
            "SSY Y-axis variants add a Y-axis cover not present on base ST configurations.",
            "DS-30 dual-spindle adds sub-spindle ways and a matching cover set.",
            "Bar-feed and parts-catcher mounting can interfere with cover paths — confirm clearances.",
            "Long-bed configurations on ST-40 and ST-50 have substantially longer ways.",
        ],
        "Current ST series way covers are OEM-available through Haas; older ST builds split between OEM availability and custom-fab. We check availability before quoting and route accordingly. Lead time is 2 to 4 weeks.",
        [
            ("Haas VF Series way covers",      "/way-covers/haas-cnc-way-covers/vf-series/"),
            ("Haas Toolroom Lathe way covers", "/way-covers/haas-cnc-way-covers/toolroom-lathes/"),
        ],
    ),
    "umc-series": _wc_series(
        "haas", "umc-series", "UMC Series", "UMC Universal 5-Axis",
        "UMC 5-axis way covers have to account for the trunnion table on top of the standard X/Y/Z protection. The trunnion adds rotational clearance constraints; the linear-axis covers have to clear the rotating workpiece envelope. Telescoping steel is standard for the linear axes; bellows or fabric covers are sometimes used for the trunnion-adjacent areas depending on the specific UMC configuration.",
        [
            "X/Y/Z linear-axis covers — telescoping steel handles the 5-axis chip load.",
            "Trunnion-adjacent cover areas may use bellows or fabric depending on workpiece-envelope clearance.",
            "UMC-350 through UMC-1600 have substantially different way-travel dimensions — confirm during quoting.",
            "SS super-speed variants share the same cover dimensions as base UMC machines.",
            "5-axis chip loads are different from 3-axis — covers see more lateral force during multi-axis cuts.",
        ],
        "UMC way covers are OEM-available through Haas across the line. Custom fabrication is an option when specific trunnion-clearance requirements call for that path. Lead time is 2 to 4 weeks.",
        [
            ("Haas VF Series way covers",  "/way-covers/haas-cnc-way-covers/vf-series/"),
            ("Haas EC Series way covers",  "/way-covers/haas-cnc-way-covers/ec-series/"),
        ],
    ),
    "ec-series": _wc_series(
        "haas", "ec-series", "EC Series", "EC Series Horizontals",
        "EC horizontal way covers protect the X/Y/Z ways plus the pallet-changer interface on PP (pallet-pool) builds. The horizontal orientation works in the covers' favor for chip drainage. Telescoping steel is the default cover style; the pallet interface uses dedicated sealing rather than a conventional cover. We fabricate the linear-axis covers and the pallet-interface seals as a coordinated set when needed.",
        [
            "X/Y/Z linear-axis covers — telescoping steel handles horizontal chip and coolant load.",
            "Pallet-changer interface sealing on PP units — the most common wear point on EC platforms.",
            "B-axis indexer interface clearances on 4AX variants.",
            "EC-1600/2000/3000 large-platform covers are substantially larger than EC-300 through EC-500.",
            "Coolant intrusion at the pallet seal is the most common reason EC covers come in.",
        ],
        "Current EC series way covers are OEM-available through Haas; older EC builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Haas VF Series way covers",   "/way-covers/haas-cnc-way-covers/vf-series/"),
            ("Haas UMC Series way covers",  "/way-covers/haas-cnc-way-covers/umc-series/"),
        ],
    ),
    "mini-mill-toolroom": _wc_series(
        "haas", "mini-mill-toolroom", "Mini Mill / Toolroom / DT / DM / VM", "Compact + Toolroom Family",
        "The compact and toolroom families share cover patterns within sub-families but differ across them. Mini Mill covers are compact telescoping steel. DT drill-tap and DM drill-mill machines have specific cover configurations matched to their high-cycle production use. VM mold-machine covers handle aluminum chip loads. TM Toolroom Mill covers split between OEM and custom-fab depending on age.",
        [
            "Mini Mill and Super Mini Mill use compact telescoping steel covers across the X and Y ways.",
            "DT drill-tap covers see high cycle counts — heavier-duty telescoping or aftermarket-upgrade options available.",
            "DM drill-mill covers handle steeper Z-axis travel than Mini Mill.",
            "VM mold-machine covers handle aluminum chip loads and high coolant flow.",
            "TM Toolroom Mill covers on older builds may require custom fabrication.",
        ],
        "Current compact and toolroom covers are OEM-available through Haas; older TM Toolroom Mill builds may require custom-fab. We check availability before quoting and route accordingly. Lead time is 2 to 4 weeks.",
        [
            ("Haas VF Series way covers",        "/way-covers/haas-cnc-way-covers/vf-series/"),
            ("Haas Toolroom Lathe way covers",   "/way-covers/haas-cnc-way-covers/toolroom-lathes/"),
        ],
    ),
    "toolroom-lathes": _wc_series(
        "haas", "toolroom-lathes", "Toolroom Lathes", "TL and CL Toolroom Lathes",
        "Toolroom lathe way covers — TL-1 through TL-4 and CL-1 — use telescoping steel as the default. The dimensions are smaller than ST series production lathes. The machines see toolroom-style use in many shops but get pushed into production-style cycles in others; cover wear patterns track the actual usage rather than the toolroom intent.",
        [
            "Telescoping steel is standard across the TL and CL lineup.",
            "TL-3 and TL-4 have substantially longer ways than TL-1 and TL-2.",
            "Manual-mode usage doesn't reduce cover wear — the ways still need protection.",
            "Bar-feed mounting on TL machines can interfere with standard cover paths — confirm clearances.",
        ],
        "Current TL and CL way covers are OEM-available through Haas; older TL builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Haas ST Series way covers",          "/way-covers/haas-cnc-way-covers/st-series/"),
            ("Haas Mini Mill / Toolroom covers",   "/way-covers/haas-cnc-way-covers/mini-mill-toolroom/"),
        ],
    ),
}

_HAAS_WC_CONTROL_SPOKES = {
    "haas-classic-control": _wc_control(
        "haas", "haas-classic-control", "Haas Classic Control", "Haas Classic Control",
        "Through roughly 2014",
        "Way covers on Classic Control era Haas machines — the early-2000s through 2014 fleet — split between OEM-available and custom-fab depending on the specific model and cover. The mechanical side of these machines is well documented, so custom fabrication to spec is straightforward when the OEM-original is no longer available. The control side is at late-life status but that's separate from the cover work.",
        "Classic Control era machines include the original [VF Series](/way-covers/haas-cnc-way-covers/vf-series/) (VF-1 through VF-12), [ST Series](/way-covers/haas-cnc-way-covers/st-series/) lathes, [EC Series](/way-covers/haas-cnc-way-covers/ec-series/) horizontals, original [Mini Mill, TM Toolroom, and DT/DM](/way-covers/haas-cnc-way-covers/mini-mill-toolroom/) machines, and [TL Toolroom Lathes](/way-covers/haas-cnc-way-covers/toolroom-lathes/).",
        [
            "Telescoping steel is the default cover style for Classic Control era Haas machines.",
            "OEM-original vs custom-fab decision depends on the specific cover and machine age.",
            "Mounting hardware is typically still available even when the cover itself is discontinued.",
            "Way damage from years of chip ingress is common — cover replacement often goes alongside way scraping or grinding.",
        ],
        "Some Classic-era Haas way covers are still OEM-available through Haas channels; others have been discontinued and require custom fabrication. The split shifts toward custom-fab as the fleet ages.",
        "Custom fabrication to your existing cover, the OEM drawing if you have it, or measurements off the machine is the standard path for discontinued covers. The mechanical specs are well documented on Classic-era Haas so measurement coordination is straightforward. Lead time is 2 to 4 weeks.",
        [
            ("Haas NGC era covers",  "/way-covers/haas-cnc-way-covers/haas-ngc/"),
        ],
    ),
    "haas-ngc": _wc_control(
        "haas", "haas-ngc", "Haas NGC", "Haas NGC",
        "2014 to present",
        "Way covers on NGC era Haas machines are fully OEM-supported through Haas channels. Most replacements run through the OEM path because dimensions are current-spec and mounting hardware is available. Custom fabrication is an option where OEM lead time or pricing makes custom the better choice for a specific job.",
        "NGC era machines include every current Haas machine — [VF Series](/way-covers/haas-cnc-way-covers/vf-series/), [ST Series](/way-covers/haas-cnc-way-covers/st-series/), all [UMC](/way-covers/haas-cnc-way-covers/umc-series/) 5-axis machines, [EC Series](/way-covers/haas-cnc-way-covers/ec-series/) horizontals, current [Mini Mill, DT, DM](/way-covers/haas-cnc-way-covers/mini-mill-toolroom/), and [TL/CL Toolroom Lathes](/way-covers/haas-cnc-way-covers/toolroom-lathes/).",
        [
            "Most NGC era machines have OEM-spec covers available through Haas channels.",
            "Telescoping steel is the default on most platforms; bellows on specific UMC trunnion-adjacent areas.",
            "Dimensions are current-spec and documented — measurement coordination is straightforward.",
            "OEM lead time can sometimes exceed our custom-fab lead time — we'll let you know during quoting.",
        ],
        "NGC era way cover parts are fully OEM-supported through Haas channels.",
        "For NGC era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. We can quote either way and recommend based on the specifics. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("Haas Classic Control era way covers",  "/way-covers/haas-cnc-way-covers/haas-classic-control/"),
        ],
    ),
}


# ============================================================
# DMG MORI WAY COVERS
# ============================================================
_DMG_MORI_WC_SERIES_SPOKES = {
    "nlx-turning": _wc_series(
        "dmg-mori", "nlx-turning", "NLX / ALX", "NLX / ALX Universal Turning",
        "NLX and ALX universal-turning covers use telescoping steel as the default across the lineup — NLX-1500 through NLX-6000 and ALX-1500 through 2500. Bed-length suffixes (/500, /700, /1500) drive cover dimensions; the SY/SMC twin-spindle and Y/MY variants add additional axes requiring matching cover sets. The long-bed configurations have substantially longer covers than the base machines.",
        [
            "Telescoping steel is standard across NLX and ALX configurations.",
            "Bed-length suffix (/500, /700, /1500) drives cover dimensions — confirm during quoting.",
            "SY and SMC twin-spindle add sub-spindle ways and matching cover sets.",
            "Y and MY variants add Y-axis covers not present on base configurations.",
            "Bar-feed and parts-catcher mounting can interfere with cover paths.",
        ],
        "Most NLX and ALX way covers are OEM-available through DMG Mori channels. Custom fabrication is an option when timing or specific requirements make that path better. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori CTX / CLX way covers",  "/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/"),
            ("DMG Mori NTX way covers",         "/way-covers/dmg-mori-cnc-way-covers/ntx/"),
        ],
    ),
    "ctx-clx-turning": _wc_series(
        "dmg-mori", "ctx-clx-turning", "CTX / CLX", "CTX / CLX Turning + TC",
        "CTX and CLX turning covers span entry CLX 350/450/550 production through CTX 850 universal turning, plus the TC turn-mill builds. The TC variants add a B-axis milling-spindle traverse cover on top of the standard turning ways. Telescoping steel is the default for the turning side; the B-axis covers on TC machines depend on travel range and clearance.",
        [
            "Turning ways use telescoping steel — standard across CTX and CLX.",
            "TC variants (CTX Beta 800 TC, Gamma 2000 TC, etc.) add B-axis milling-spindle covers.",
            "Long-bed CTX 650 and CTX 850 have substantially longer covers than base CTX 310/450.",
            "Tailstock mounting on long-bed configurations can interfere with cover paths.",
            "Hydraulic chuck mounting hardware can interact with the cover sealing area.",
        ],
        "CTX and CLX way covers are OEM-available through DMG Mori; the TC B-axis covers are sometimes routed through custom fabrication depending on the specific build. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori NLX / ALX way covers",  "/way-covers/dmg-mori-cnc-way-covers/nlx-turning/"),
            ("DMG Mori NTX way covers",         "/way-covers/dmg-mori-cnc-way-covers/ntx/"),
        ],
    ),
    "ntx": _wc_series(
        "dmg-mori", "ntx", "NTX", "NTX Integrated Mill-Turn",
        "NTX integrated mill-turn covers handle the most complex configuration in the DMG Mori turning lineup. Each machine has turning-side covers plus a B-axis milling-spindle traverse cover plus sub-spindle ways on twin-spindle configurations. NTX 1000 through NTX 4000 cover sets differ substantially in dimension — we coordinate the full set as a package rather than as individual covers.",
        [
            "Turning ways use telescoping steel — standard across NTX configurations.",
            "B-axis milling-spindle traverse cover — telescoping or fabric depending on travel and clearance.",
            "Sub-spindle ways on twin-spindle NTX variants.",
            "Tool changer interface clearances are tighter on NTX than on straight turning.",
            "NTX 3000 and NTX 4000 have substantially larger cover sets than NTX 1000/2000.",
        ],
        "Current NTX covers are OEM-available through DMG Mori. We can coordinate the full cover set as a package or build individual covers as needed. Lead time is 2 to 4 weeks; full-machine cover sets can run slightly longer.",
        [
            ("DMG Mori CTX / CLX way covers",  "/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/"),
            ("DMG Mori DMU / DMC way covers",  "/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/"),
        ],
    ),
    "dmu-dmc": _wc_series(
        "dmg-mori", "dmu-dmc", "DMU / DMC 5-Axis", "DMU / DMC 5-Axis Universal & Cube",
        "DMU and DMC 5-axis covers are among the more demanding fabrications in the DMG Mori lineup. DMU trunnion-table machines (DMU 50 through DMU 340) need linear-axis covers that clear the rotating workpiece envelope. DMU monoBLOCK and duoBLOCK builds have different cover geometries from the trunnion machines. DMC cube and gantry builds have their own configurations.",
        [
            "DMU trunnion-table covers — linear axes use telescoping steel; trunnion-adjacent areas use bellows or fabric.",
            "DMU monoBLOCK swivel-head configurations have different cover requirements than trunnion.",
            "DMU duoBLOCK covers handle larger work envelopes than monoBLOCK.",
            "DMC vertical, cube, and gantry builds have distinct cover geometries.",
            "5-axis chip and coolant loads are different from 3-axis — cover sealing matters more.",
        ],
        "Current DMU and DMC way covers are OEM-available through DMG Mori; some specific configurations route through custom fabrication. Lead time is 2 to 4 weeks. Full multi-axis cover sets coordinate well as a package.",
        [
            ("DMG Mori NHX / NH way covers",  "/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/"),
            ("DMG Mori NVX / NV way covers",  "/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/"),
        ],
    ),
    "nhx-horizontals": _wc_series(
        "dmg-mori", "nhx-horizontals", "NHX / NH", "NHX / NH Horizontals",
        "NHX and the older NH horizontal covers have to account for the pallet-changer interface on top of standard X/Y/Z protection. Telescoping steel is the default cover style; pallet-interface sealing uses dedicated sealing rather than conventional covers. NHX 4000 through 10000 covers differ substantially in dimension; NHX-8000 and 10000 large platforms have heavier-duty cover sets.",
        [
            "Telescoping steel covers — standard across NHX and NH configurations.",
            "Pallet-changer interface sealing on all NHX builds — most common wear point.",
            "B-axis indexer interface clearances on every NHX configuration.",
            "Large-platform NHX-8000 and NHX-10000 have substantially larger covers than NHX-4000/5000.",
            "Coolant intrusion at the pallet seal is the most common reason NHX covers come in.",
        ],
        "Current NHX way covers are OEM-available through DMG Mori; legacy NH covers split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori DMU / DMC way covers",     "/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/"),
            ("DMG Mori NVX / NV way covers",      "/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/"),
        ],
    ),
    "nvx-verticals": _wc_series(
        "dmg-mori", "nvx-verticals", "NVX / NV / NVD", "NVX / NV / NVD Verticals",
        "NVX vertical-machining covers — NVX 4000 through 7000 — use telescoping steel as the default. NV 4000 and NV 5000 older builds use the same general configurations with slightly different mounting. NVD with DCG (Driven at the Center of Gravity) construction has the same external cover geometry as NVX but different internal mounting in some areas.",
        [
            "X/Y/Z covers — telescoping steel is the default across NVX, NV, and NVD.",
            "NVX-5060 and NVX-7000 large-envelope covers are substantially larger than NVX-4000.",
            "DCG construction on NVD affects internal mounting but not external cover dimensions.",
            "Spindle column covers on some configurations — bellows or fabric depending on the build.",
            "Way damage from chip ingress is common on heavily used NVX machines.",
        ],
        "Current NVX way covers are OEM-available through DMG Mori; older NV builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori DMU / DMC way covers",  "/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/"),
            ("DMG Mori NHX / NH way covers",   "/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/"),
        ],
    ),
    "cmx": _wc_series(
        "dmg-mori", "cmx", "CMX / CMX U", "CMX Entry & 5-Sided",
        "CMX way covers — CMX 600V through 1300V verticals and CMX 50U/70U 5-axis universals — use lighter-duty telescoping steel than the higher-end NVX or DMU lines. The platform's cost optimization is reflected in the cover specifications. In heavy-use environments cover wear outpaces the higher-end machines.",
        [
            "Telescoping steel covers — lighter-duty than higher-end DMG Mori lines.",
            "CMX 50U and 70U add trunnion-adjacent cover considerations on 5-axis builds.",
            "Cover wear in heavy-use environments tends to be faster than on NVX or DMU.",
            "Smaller CMX 320V has tighter clearance constraints — confirm during quoting.",
        ],
        "CMX way covers are OEM-available through DMG Mori. Custom fabrication is sometimes the right path for heavy-use environments where heavier-duty covers extend service intervals. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori DMU / DMC way covers",       "/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/"),
            ("DMG Mori DMP / Milltap way covers",   "/way-covers/dmg-mori-cnc-way-covers/dmp-milltap/"),
        ],
    ),
    "dmp-milltap": _wc_series(
        "dmg-mori", "dmp-milltap", "DMP / Milltap", "DMP / Milltap Compact Production",
        "DMP and Milltap compact-production covers handle high-cycle drill-tap and small-part production. The covers are compact telescoping steel matched to the small machine envelopes. High cycle counts wear the cover seals faster than on larger machines; in high-throughput environments cover replacement can be a routine annual or semi-annual item.",
        [
            "Compact telescoping steel covers — standard across DMP and Milltap.",
            "Cover seals see high cycle counts — wear patterns track the throughput.",
            "Dual-spindle DMP 500 has additional sub-spindle covers.",
            "Tight clearance constraints on the smallest DMP 35 — confirm dimensions carefully.",
        ],
        "DMP and Milltap way covers are OEM-available through DMG Mori. Heavy-duty aftermarket options sometimes make sense for high-throughput environments. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori CMX way covers",       "/way-covers/dmg-mori-cnc-way-covers/cmx/"),
            ("DMG Mori NVX / NV way covers",  "/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/"),
        ],
    ),
    "sprint-multisprint": _wc_series(
        "dmg-mori", "sprint-multisprint", "SPRINT / MULTISPRINT", "SPRINT / MULTISPRINT Swiss",
        "SPRINT and MULTISPRINT Swiss-style covers handle the high-precision small-diameter bar work these platforms specialize in. Cover geometry on Swiss-type machines differs from straight turning — guide bushing interfaces and bar-feed paths constrain the cover designs. We work with the specific machine configuration during quoting.",
        [
            "Swiss-style cover geometry differs from straight turning configurations.",
            "Guide bushing interface clearances are tight on Swiss platforms.",
            "Bar-feed integration paths interact with cover designs.",
            "MULTISPRINT 25 and 36 add multi-tool spindle considerations.",
        ],
        "SPRINT and MULTISPRINT way covers are OEM-available through DMG Mori. Custom fabrication is sometimes the right path when bar-feed or guide-bushing configurations differ from OEM-spec. Lead time is 2 to 4 weeks.",
        [
            ("DMG Mori NLX / ALX way covers",   "/way-covers/dmg-mori-cnc-way-covers/nlx-turning/"),
            ("DMG Mori CTX / CLX way covers",   "/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/"),
        ],
    ),
}

_DMG_MORI_WC_CONTROL_SPOKES = {
    "siemens-840d": _wc_control(
        "dmg-mori", "siemens-840d", "Siemens 840D", "Siemens 840D",
        "Late 1990s through present",
        "Way covers on DMG Mori machines running Siemens 840D span a wide age range — from late-1990s original 840D builds through current solutionline machines. Original 840D era machines (roughly 1998-2010) increasingly require custom fabrication; solutionline era (2010-present) is mostly OEM-available. The control side is separate from the cover work but the era helps frame parts availability.",
        "Siemens 840D ships on most of the DMG Mori lineup — [NLX/ALX](/way-covers/dmg-mori-cnc-way-covers/nlx-turning/), [CTX/CLX](/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/), [NTX](/way-covers/dmg-mori-cnc-way-covers/ntx/), [NHX/NH](/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/), [NVX/NV/NVD](/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/), [CMX](/way-covers/dmg-mori-cnc-way-covers/cmx/), [DMP/Milltap](/way-covers/dmg-mori-cnc-way-covers/dmp-milltap/), [SPRINT/MULTISPRINT](/way-covers/dmg-mori-cnc-way-covers/sprint-multisprint/), and the [DMC](/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/) variants.",
        [
            "Original 840D era machines (pre-2010) increasingly route through custom fabrication.",
            "Solutionline era machines (2010-present) are mostly OEM-available.",
            "Telescoping steel is the default cover style on most Siemens-controlled DMG Mori machines.",
            "Era split is rough — some configurations stayed OEM-available longer than others.",
        ],
        "Original 840D era way covers are increasingly custom-fab; solutionline era machines have OEM availability through DMG Mori. The split shifts year over year as inventory thins on the older builds.",
        "Custom fabrication to your existing cover, the OEM drawing, or measurements off the machine is the standard path for discontinued covers. Mounting hardware on Siemens-controlled DMG Mori machines is typically well documented. Lead time is 2 to 4 weeks.",
        [
            ("Heidenhain TNC era way covers",  "/way-covers/dmg-mori-cnc-way-covers/heidenhain-tnc/"),
            ("CELOS era way covers",           "/way-covers/dmg-mori-cnc-way-covers/celos/"),
        ],
    ),
    "heidenhain-tnc": _wc_control(
        "dmg-mori", "heidenhain-tnc", "Heidenhain TNC", "Heidenhain TNC",
        "iTNC 530 from ~2001, TNC 640 from 2012",
        "Way covers on DMG Mori machines running Heidenhain TNC are mostly the DMU and DMC 5-axis fleet. iTNC 530 era machines (2001-2012) split between OEM and custom-fab depending on configuration; TNC 640 era (2012-present) is mostly OEM-available. The 5-axis cover requirements are more complex than straight verticals — trunnion-adjacent areas often use bellows or fabric.",
        "Heidenhain TNC ships on the [DMU/DMC](/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/) 5-axis family — DMU 50 through DMU 340, monoBLOCK and duoBLOCK builds, DMU eVo, and the DMC universals.",
        [
            "5-axis trunnion-adjacent areas often use bellows or fabric rather than telescoping steel.",
            "iTNC 530 era covers (2001-2012) split between OEM and custom-fab.",
            "TNC 640 era covers (2012-present) are mostly OEM-available through DMG Mori.",
            "DMU monoBLOCK and duoBLOCK have different cover geometries from trunnion machines.",
        ],
        "iTNC 530 era way covers are heading toward late-life on the parts side; some configurations are OEM-available, others require custom fabrication. TNC 640 era covers are mostly OEM-available.",
        "For older DMU machines with iTNC 530, custom fabrication to spec is increasingly the path — we build to your existing cover, the OEM drawing, or measurements off the machine. Lead time is 2 to 4 weeks. 5-axis cover sets can run slightly longer when the trunnion-adjacent areas need coordinated bellows fabrication.",
        [
            ("Siemens 840D era way covers",   "/way-covers/dmg-mori-cnc-way-covers/siemens-840d/"),
            ("CELOS era way covers",          "/way-covers/dmg-mori-cnc-way-covers/celos/"),
        ],
    ),
    "celos": _wc_control(
        "dmg-mori", "celos", "CELOS", "CELOS HMI",
        "CELOS from 2014, CELOS X current",
        "CELOS is the DMG Mori HMI layer — machines with CELOS are current-generation builds (2014 onward) which means way covers are mostly OEM-available. The CELOS era frames parts availability well: if a machine has CELOS, the underlying control is recent enough that OEM cover parts are in current supply through DMG Mori.",
        "CELOS runs on every current DMG Mori machine — every [NLX/ALX](/way-covers/dmg-mori-cnc-way-covers/nlx-turning/), [CTX/CLX](/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/), [NTX](/way-covers/dmg-mori-cnc-way-covers/ntx/), [DMU/DMC](/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/), [NHX/NH](/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/), [NVX/NV/NVD](/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/), [CMX](/way-covers/dmg-mori-cnc-way-covers/cmx/), [DMP/Milltap](/way-covers/dmg-mori-cnc-way-covers/dmp-milltap/), and [SPRINT/MULTISPRINT](/way-covers/dmg-mori-cnc-way-covers/sprint-multisprint/) machines.",
        [
            "CELOS era machines are current production — way covers are OEM-available through DMG Mori.",
            "Underlying control (Siemens 840D or Heidenhain TNC) is recent enough that mounting hardware is current.",
            "Custom fabrication is an option when OEM lead time or pricing favors that path.",
            "Cover dimensions are documented and current — measurement coordination is straightforward.",
        ],
        "CELOS era way cover parts are fully OEM-supported through DMG Mori channels.",
        "For CELOS era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. We can quote either way and recommend based on the specifics. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("Siemens 840D era way covers",     "/way-covers/dmg-mori-cnc-way-covers/siemens-840d/"),
            ("Heidenhain TNC era way covers",   "/way-covers/dmg-mori-cnc-way-covers/heidenhain-tnc/"),
        ],
    ),
}


# ============================================================
# DOOSAN WAY COVERS — controls cross-link to Fanuc
# ============================================================
_DOOSAN_WC_SERIES_SPOKES = {
    "puma": _wc_series(
        "doosan", "puma", "Puma", "Puma Horizontal Turning",
        "Puma horizontal-turning covers use telescoping steel across the lineup — Puma 230 through Puma 800 with M/MS/LM/LY/Y/SY variants, the heavier 4100/5100/700/800 builds, the GT compact lineup, and the TT twin-turret builds. Cover dimensions scale with bed size. The MS/SY twin-spindle variants add sub-spindle ways requiring matching cover sets.",
        [
            "Telescoping steel covers — standard across the Puma lineup.",
            "MS and SY twin-spindle variants add sub-spindle cover sets.",
            "Y-axis variants (LY, Y, SY) add a Y-axis cover.",
            "Long-bed Puma 4100 and 5100 have substantially longer covers than smaller Puma builds.",
            "TT twin-turret has additional turret-side covers.",
        ],
        "Most Puma way covers are OEM-available through DN Solutions (Doosan); older Puma builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Puma MX / SMX way covers",  "/way-covers/doosan-cnc-way-covers/puma-mx-smx/"),
            ("Doosan Lynx way covers",            "/way-covers/doosan-cnc-way-covers/lynx/"),
        ],
    ),
    "puma-mx-smx": _wc_series(
        "doosan", "puma-mx-smx", "Puma MX / SMX", "Puma MX / SMX Multitasking",
        "Puma MX and SMX mill-turn covers add a B-axis milling-spindle traverse cover on top of the standard turning ways. MX 1600 through 3100 and SMX 2100/2600/3100 cover sets are coordinated — we typically quote the full set rather than individual covers because the dimensions interact.",
        [
            "Turning ways use telescoping steel — standard on Puma MX/SMX.",
            "B-axis milling-spindle traverse cover — telescoping or fabric depending on configuration.",
            "Sub-spindle ways on T/ST variants.",
            "ATC interface clearances are tighter on multitasking than on straight turning.",
        ],
        "Puma MX and SMX way covers are OEM-available through DN Solutions; the B-axis cover on specific configurations may route through custom fabrication. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Puma way covers",         "/way-covers/doosan-cnc-way-covers/puma/"),
            ("Doosan DVF 5-Axis way covers",   "/way-covers/doosan-cnc-way-covers/5-axis-verticals/"),
        ],
    ),
    "puma-vertical-turning": _wc_series(
        "doosan", "puma-vertical-turning", "Puma V / VT / VTR", "Puma Vertical Turning",
        "Puma V, VT, and VTR vertical-turning covers protect the ram and table ways from chip and coolant. Vertical-turning configurations have different cover geometry than horizontal turning — the table sees axial chip drop, the ram sees radial chip patterns. Telescoping steel is the default for the ram travel; specific table-area sealing depends on the build.",
        [
            "Ram-travel covers use telescoping steel on V/VT/VTR.",
            "Table-area sealing depends on the specific build — V400 through V9300 differ substantially.",
            "VT 750/900/1100 vertical turning centers have additional milling-spindle considerations.",
            "VTR ram-type machines have unique cover geometries.",
        ],
        "Current Puma V/VT/VTR way covers are OEM-available through DN Solutions; older builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Puma way covers",         "/way-covers/doosan-cnc-way-covers/puma/"),
            ("Doosan DNM Vertical way covers", "/way-covers/doosan-cnc-way-covers/dnm-verticals/"),
        ],
    ),
    "lynx": _wc_series(
        "doosan", "lynx", "Lynx", "Lynx Compact Turning",
        "Lynx compact-turning covers — Lynx 220, 2100, 2600, 300 with M/MS/LM/LSY/LY variants — use compact telescoping steel. Bar-feed integration is common on Lynx and the bar-feed mounting can interfere with standard cover paths. We coordinate cover dimensions with the bar-feed installation when both are factors.",
        [
            "Compact telescoping steel covers — standard on Lynx.",
            "Bar-feed mounting often interacts with cover paths — confirm during quoting.",
            "LSY twin-spindle adds sub-spindle ways.",
            "LMA and MA milling variants add Y-axis covers.",
        ],
        "Lynx way covers are OEM-available through DN Solutions on most builds. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Puma way covers",        "/way-covers/doosan-cnc-way-covers/puma/"),
            ("Doosan Swiss-Type way covers",  "/way-covers/doosan-cnc-way-covers/swiss-turning/"),
        ],
    ),
    "dnm-verticals": _wc_series(
        "doosan", "dnm-verticals", "DNM", "DNM Vertical Machining",
        "DNM vertical-machining covers use telescoping steel for X/Y/Z ways. DNM 200 through 750 cover dimensions scale with bed size; the higher-end DNM 4000/5700/6700 production builds have heavier-duty cover specifications. DNM 200/5AX adds 5-axis trunnion considerations to the standard vertical-mill cover requirements.",
        [
            "X/Y/Z telescoping steel covers — standard across the DNM lineup.",
            "DNM 5700 and 6700 large-platform covers are substantially larger than DNM 200/350.",
            "DNM 200/5AX 5-axis adds trunnion-adjacent cover considerations.",
            "Way cover damage from chip ingress is common on heavily used DNM machines.",
        ],
        "Current DNM way covers are OEM-available through DN Solutions; older builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Horizontals way covers",  "/way-covers/doosan-cnc-way-covers/horizontals/"),
            ("Doosan DVF 5-Axis way covers",   "/way-covers/doosan-cnc-way-covers/5-axis-verticals/"),
        ],
    ),
    "horizontals": _wc_series(
        "doosan", "horizontals", "NHM / NHP / HC", "NHM / NHP / HC Horizontals",
        "Doosan horizontal way covers protect the X/Y/Z ways plus the pallet-changer interface on PP units. Telescoping steel is the default; pallet-interface sealing uses dedicated sealing. NHM 4000 through 8000 cover dimensions scale with bed size; NHM-8000 large-platform has substantially heavier-duty cover requirements.",
        [
            "Telescoping steel covers — standard across NHM, NHP, HC.",
            "Pallet-changer interface sealing on all builds — most common wear point.",
            "B-axis indexer interface clearances on every configuration.",
            "NHM-8000 large-platform covers are substantially larger than NHM-4000.",
        ],
        "Current Doosan horizontal way covers are OEM-available through DN Solutions. Lead time is 2 to 4 weeks.",
        [
            ("Doosan DNM Vertical way covers",  "/way-covers/doosan-cnc-way-covers/dnm-verticals/"),
            ("Doosan Puma way covers",          "/way-covers/doosan-cnc-way-covers/puma/"),
        ],
    ),
    "5-axis-verticals": _wc_series(
        "doosan", "5-axis-verticals", "DVF / FM", "DVF / FM 5-Axis",
        "DVF and FM 5-axis covers handle trunnion-table and linear-motor configurations. DVF 5000/6500/8000 use trunnion tables with standard X/Y/Z linear-axis covers plus trunnion-adjacent sealing. FM 200/5AX Linear-motor build has different cover requirements because of the linear-motor drive design.",
        [
            "DVF trunnion-table covers — linear axes use telescoping steel; trunnion-adjacent areas use bellows or fabric.",
            "DVF 5000 through 8000 have substantially different work envelopes and cover dimensions.",
            "FM 200/5AX Linear-motor build has unique cover considerations.",
            "5-axis chip and coolant loads require careful cover sealing.",
        ],
        "DVF and FM way covers are OEM-available through DN Solutions. Lead time is 2 to 4 weeks; multi-axis cover sets coordinate well as a package.",
        [
            ("Doosan DNM Vertical way covers",      "/way-covers/doosan-cnc-way-covers/dnm-verticals/"),
            ("Doosan Puma MX / SMX way covers",     "/way-covers/doosan-cnc-way-covers/puma-mx-smx/"),
        ],
    ),
    "swiss-turning": _wc_series(
        "doosan", "swiss-turning", "Swiss-Type / DST", "Swiss-Type / DST",
        "Doosan Swiss-type covers handle high-precision small-diameter bar work — SwiftTurn 32 and 38 plus the DST series. Cover geometry on Swiss platforms differs from straight turning — guide bushing interfaces and bar-feed paths constrain the cover designs. We work with the specific configuration during quoting.",
        [
            "Swiss-style cover geometry differs from straight turning.",
            "Guide bushing interface clearances are tight on Swiss platforms.",
            "Bar-feed integration paths interact with cover designs.",
            "DST series multi-tool configurations add live-tool considerations.",
        ],
        "Doosan Swiss way covers are OEM-available through DN Solutions on current builds. Lead time is 2 to 4 weeks.",
        [
            ("Doosan Lynx way covers",  "/way-covers/doosan-cnc-way-covers/lynx/"),
            ("Doosan Puma way covers",  "/way-covers/doosan-cnc-way-covers/puma/"),
        ],
    ),
}


# ============================================================
# OKUMA WAY COVERS
# ============================================================
_OKUMA_WC_SERIES_SPOKES = {
    "lb-lu-lathes": _wc_series(
        "okuma", "lb-lu-lathes", "LB / LU Lathes", "LB / LU Horizontal Lathes",
        "LB and LU horizontal-lathe covers use telescoping steel as the default. Okuma's reputation for thermal stability extends to the way-cover sealing — covers tend to stay in spec longer than on lower-end platforms when the machine has been well maintained. LB 200 through LB 5000 EX cover dimensions scale with bed size; live-tool variants add additional axes.",
        [
            "Telescoping steel covers — standard across LB and LU.",
            "Long-bed LB 4000 EX and LB 5000 EX have substantially longer covers than LB 200/250.",
            "Live-tool variants add live-tool turret cover considerations.",
            "LU 7000 and 8000 large-bore platforms have heavier-duty cover specifications.",
        ],
        "Current LB and LU way covers are OEM-available through Okuma; older builds split between OEM and custom-fab. Legacy ES-L and ESV are typically custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Okuma Genos way covers",   "/way-covers/okuma-cnc-way-covers/genos/"),
            ("Okuma MULTUS way covers",  "/way-covers/okuma-cnc-way-covers/multus/"),
        ],
    ),
    "genos": _wc_series(
        "okuma", "genos", "Genos", "Genos 'Affordable Excellence'",
        "Genos covers handle the 'Affordable Excellence' line — Genos L lathes and Genos M verticals. Lighter-duty than the higher-end MB/MA or MULTUS lines, but Okuma still uses quality cover specifications relative to platform class. In heavy-use environments cover wear outpaces the higher-end machines.",
        [
            "Telescoping steel covers — lighter-duty than higher-end Okuma lines.",
            "Genos L lathes use compact configurations matched to the production class.",
            "Genos M verticals use standard X/Y/Z cover patterns.",
            "Heavy-use cover wear can be faster than on MB/MA or MULTUS lines.",
        ],
        "Genos way covers are OEM-available through Okuma. Custom fabrication is an option for heavy-use environments. Lead time is 2 to 4 weeks.",
        [
            ("Okuma LB / LU way covers",          "/way-covers/okuma-cnc-way-covers/lb-lu-lathes/"),
            ("Okuma MB / MA Vertical way covers", "/way-covers/okuma-cnc-way-covers/mb-ma-verticals/"),
        ],
    ),
    "mb-ma-verticals": _wc_series(
        "okuma", "mb-ma-verticals", "MB / MA", "MB / MA Vertical Machining",
        "MB and MA vertical-machining covers are the Okuma vertical workhorses. MB-46V through MB-66V production verticals, MB-4000H/5000H horizontal-spindle builds, and MA-400 through MA-8000 larger-envelope platforms. Telescoping steel is the default; Okuma's thermal compensation framework helps cover dimensions stay stable over time when the machine is well maintained.",
        [
            "X/Y/Z telescoping steel covers — standard across MB and MA.",
            "MB-4000H and MB-5000H horizontal-spindle builds have different cover geometry.",
            "MA-650 and MA-8000 large-envelope covers are substantially larger than MA-400/500.",
            "Thermal compensation framework affects cover dimensional stability over time.",
        ],
        "Current MB and MA way covers are OEM-available through Okuma; older builds split between OEM and custom-fab. Legacy MV and MX-45 are typically custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Okuma Genos way covers",     "/way-covers/okuma-cnc-way-covers/genos/"),
            ("Okuma MULTUS way covers",    "/way-covers/okuma-cnc-way-covers/multus/"),
        ],
    ),
    "multus": _wc_series(
        "okuma", "multus", "MULTUS", "MULTUS B-Axis Multitasking",
        "MULTUS multitasking covers add a B-axis milling-spindle traverse cover on top of the standard turning ways. MULTUS B200 through B750 and U3000 through U5000 cover sets coordinate as a package — we typically quote the full set because dimensions interact across turning ways, B-axis traverse, and sub-spindle ways on dual-spindle variants.",
        [
            "Turning ways use telescoping steel — standard on MULTUS configurations.",
            "B-axis milling-spindle traverse cover — telescoping or fabric depending on configuration.",
            "Lower turret cover on twin-turret MULTUS configurations.",
            "Sub-spindle ways on dual-spindle MULTUS variants.",
            "Historic MacTurn predecessors are typically custom-fab.",
        ],
        "MULTUS way covers are OEM-available through Okuma on current builds; older builds split between OEM and custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Okuma Twin-Spindle / Twin-Turret",  "/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/"),
            ("Okuma LB / LU way covers",           "/way-covers/okuma-cnc-way-covers/lb-lu-lathes/"),
        ],
    ),
    "twin-spindle-twin-turret": _wc_series(
        "okuma", "twin-spindle-twin-turret", "Twin-Spindle / Twin-Turret", "Twin-Spindle / Twin-Turret",
        "Okuma's twin-spindle and twin-turret covers — 2SP-2500H, 2SP-V40, LT 200-MY through LT 2000 EX — coordinate as multi-cover sets. Twin-spindle adds sub-spindle ways; twin-turret adds lower-turret cover considerations. We quote the full set as a package because the dimensions interact.",
        [
            "Telescoping steel for main turning ways — standard across twin-spindle/twin-turret.",
            "Sub-spindle ways add a matching cover set.",
            "Lower-turret cover on twin-turret configurations.",
            "Legacy LT-15 and LT-25 are almost always custom-fab.",
        ],
        "Current twin-spindle/twin-turret way covers are OEM-available through Okuma; legacy LT-15/25 are custom-fab. Lead time is 2 to 4 weeks.",
        [
            ("Okuma MULTUS way covers",     "/way-covers/okuma-cnc-way-covers/multus/"),
            ("Okuma LB / LU way covers",    "/way-covers/okuma-cnc-way-covers/lb-lu-lathes/"),
        ],
    ),
    "vtm": _wc_series(
        "okuma", "vtm", "VTM", "VTM Vertical Turning",
        "Okuma VTM vertical-turning covers protect the ram and table areas. VTM-65 through VTM-180 cover dimensions scale with the table size. Table-area sealing depends on the build; the ram travel uses telescoping steel as the default. The large work envelopes on VTM-180 require correspondingly larger cover sets.",
        [
            "Ram-travel covers use telescoping steel.",
            "Table-area sealing depends on the specific VTM configuration.",
            "VTM-180 large-platform covers are substantially larger than VTM-65/100.",
            "Swarf evacuation around the table interacts with cover sealing.",
        ],
        "Current VTM way covers are OEM-available through Okuma. Lead time is 2 to 4 weeks.",
        [
            ("Okuma MU 5-Axis / MCR Bridge",       "/way-covers/okuma-cnc-way-covers/v-bridge-mills/"),
            ("Okuma LAW / LFS Heavy Lathes",       "/way-covers/okuma-cnc-way-covers/heavy-lathes/"),
        ],
    ),
    "v-bridge-mills": _wc_series(
        "okuma", "v-bridge-mills", "MU 5-Axis / MCR Bridge", "MU 5-Axis / MCR Bridge",
        "MU 5-axis and MCR bridge-mill covers are the most complex fabrications in the Okuma lineup. MU-400V through MU-8000V trunnion-table 5-axis machines need linear-axis covers that clear the rotating workpiece envelope. MCR-A5C and MCR-BIII bridge mills have bridge-geometry cover requirements that differ from trunnion machines.",
        [
            "MU trunnion-table covers — linear axes use telescoping steel; trunnion-adjacent areas use bellows or fabric.",
            "MU-8000V large-platform has substantially larger cover sets than MU-400V/500V.",
            "MCR-A5C and MCR-BIII bridge mill covers have distinct geometry from trunnion machines.",
            "Bridge-geometry covers handle large-span work envelopes.",
        ],
        "MU and MCR way covers are OEM-available through Okuma on current builds. Lead time is 2 to 4 weeks; full multi-axis cover sets coordinate as a package.",
        [
            ("Okuma MB / MA Vertical way covers",  "/way-covers/okuma-cnc-way-covers/mb-ma-verticals/"),
            ("Okuma VTM way covers",                "/way-covers/okuma-cnc-way-covers/vtm/"),
        ],
    ),
    "heavy-lathes": _wc_series(
        "okuma", "heavy-lathes", "LAW / LFS Heavy", "LAW / LFS Heavy Lathes",
        "Okuma LAW and LFS heavy-lathe covers handle very large workpieces and very heavy cuts. LAW 1000 through 3000 use heavier-duty cover specifications matched to the machine class. LFS-590 flat-bed turning has different cover geometry from the LAW configurations.",
        [
            "Heavy-duty telescoping steel covers — scaled for the workpiece class.",
            "LAW 3000 covers are substantially heavier-duty than LAW 1000.",
            "LFS-590 flat-bed has distinct cover geometry from LAW.",
            "Heavy chip and coolant loads require careful cover sealing.",
        ],
        "Current LAW and LFS way covers are OEM-available through Okuma. Custom fabrication is sometimes appropriate for heavy-cut environments where heavier-than-OEM specifications make sense. Lead time is 2 to 4 weeks.",
        [
            ("Okuma LB / LU way covers",  "/way-covers/okuma-cnc-way-covers/lb-lu-lathes/"),
            ("Okuma VTM way covers",      "/way-covers/okuma-cnc-way-covers/vtm/"),
        ],
    ),
}

_OKUMA_WC_CONTROL_SPOKES = {
    "osp-p200": _wc_control(
        "okuma", "osp-p200", "OSP-P200", "OSP-P200",
        "Roughly 2003 through 2012",
        "Way covers on OSP-P200 era Okuma machines — the early-2000s through 2012 fleet — split between OEM-available and custom-fab. Most are still OEM-available through Okuma channels but the supply is thinning on the older configurations. We check availability before quoting.",
        "OSP-P200 era machines include older [LB and LU lathes](/way-covers/okuma-cnc-way-covers/lb-lu-lathes/), [MB and MA verticals](/way-covers/okuma-cnc-way-covers/mb-ma-verticals/), older [MULTUS](/way-covers/okuma-cnc-way-covers/multus/) builds, [VTM](/way-covers/okuma-cnc-way-covers/vtm/), [twin-spindle and twin-turret](/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/), and [LAW heavy lathes](/way-covers/okuma-cnc-way-covers/heavy-lathes/).",
        [
            "Telescoping steel is the default cover style on OSP-P200 era machines.",
            "OEM availability is thinning on older configurations — check before quoting.",
            "Mounting hardware is typically still available even when covers are heading toward late-life.",
            "Custom-fab is an option when OEM lead time or pricing pushes that direction.",
        ],
        "OSP-P200 era way covers split between OEM-available and increasingly custom-fab. The shift toward custom is gradual as Okuma's OEM supply on older builds thins year over year.",
        "Custom fabrication to your existing cover, the OEM drawing, or measurements off the machine is the standard path when OEM is no longer available. Lead time is 2 to 4 weeks.",
        [
            ("OSP-P300 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p300/"),
            ("OSP Legacy era way covers", "/way-covers/okuma-cnc-way-covers/osp-legacy/"),
        ],
    ),
    "osp-p300": _wc_control(
        "okuma", "osp-p300", "OSP-P300", "OSP-P300",
        "Roughly 2012 through 2020",
        "Way covers on OSP-P300 era Okuma machines are mostly OEM-available through Okuma channels. The era is current enough that mounting hardware and dimensions are well documented and parts are in current supply. Custom fabrication is an option when timing or specific requirements push that direction.",
        "OSP-P300 era machines include current [LB and LU lathes](/way-covers/okuma-cnc-way-covers/lb-lu-lathes/), [Genos](/way-covers/okuma-cnc-way-covers/genos/), current [MB and MA verticals](/way-covers/okuma-cnc-way-covers/mb-ma-verticals/), [MULTUS](/way-covers/okuma-cnc-way-covers/multus/) (except current U5000), [VTM](/way-covers/okuma-cnc-way-covers/vtm/), [MU and MCR](/way-covers/okuma-cnc-way-covers/v-bridge-mills/), [twin-spindle / twin-turret](/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/), and [LAW](/way-covers/okuma-cnc-way-covers/heavy-lathes/) builds.",
        [
            "Most P300 era way covers are OEM-available through Okuma.",
            "Telescoping steel is the default; bellows on specific 5-axis trunnion configurations.",
            "Dimensions are documented and current — measurement coordination is straightforward.",
            "Custom-fab is an option for non-standard configurations or heavy-use environments.",
        ],
        "OSP-P300 era way covers are mostly OEM-available through Okuma channels.",
        "For OSP-P300 era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("OSP-P200 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p200/"),
            ("OSP-P500 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p500/"),
        ],
    ),
    "osp-p500": _wc_control(
        "okuma", "osp-p500", "OSP-P500", "OSP-P500",
        "2020 to present",
        "Way covers on OSP-P500 era Okuma machines are fully OEM-supported through Okuma channels. Current production builds with current dimensions and current mounting hardware. Most replacements run through OEM unless lead time or pricing pushes toward custom.",
        "OSP-P500 era machines include Okuma's current flagship platforms — the latest [LB 3000 EX II and LB 4000/5000 EX](/way-covers/okuma-cnc-way-covers/lb-lu-lathes/), current [MULTUS U5000 and B-II](/way-covers/okuma-cnc-way-covers/multus/), and other current-generation builds.",
        [
            "P500 era machines are current production — way covers are OEM-available through Okuma.",
            "Dimensions and mounting hardware are current-spec.",
            "Custom-fab is an option when OEM lead time or pricing favors that path.",
        ],
        "OSP-P500 era way cover parts are fully OEM-supported through Okuma channels.",
        "Custom fabrication is straightforward for P500 era machines because dimensions are current-spec and measurements coordinate easily. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("OSP-P300 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p300/"),
            ("OSP-P200 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p200/"),
        ],
    ),
    "osp-legacy": _wc_control(
        "okuma", "osp-legacy", "OSP Legacy", "OSP Legacy",
        "Pre-2003",
        "Way covers on OSP Legacy era Okuma machines (pre-2003) are almost always custom-fabrication. OEM cover part numbers for OSP 5000, OSP 7000, U10, and U100 era machines have largely been discontinued. We build to spec from your existing cover, the original Okuma drawing if you have it, or measurements off the machine.",
        "OSP Legacy controls shipped on older Okuma platforms — legacy MV-series verticals, MX-45, ES-L and ESV [LB/LU](/way-covers/okuma-cnc-way-covers/lb-lu-lathes/) builds, older [LT-15 and LT-25 twin-turret](/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/), and legacy MacTurn predecessors to current MULTUS.",
        [
            "Telescoping steel is the default for legacy Okuma turning machines.",
            "Custom-fab is the standard path — OEM-spec is mostly discontinued.",
            "Original mounting hardware is sometimes unavailable — replacement hardware as part of the build.",
            "Measurements off the machine require careful coordination since these are 20+-year-old platforms.",
        ],
        "OSP Legacy era way covers are mostly OEM-discontinued. Custom fabrication is the standard path.",
        "Custom fabrication to your existing cover, the original OEM drawing if you have it, or measurements taken off the machine. We can build complete cover sets for legacy machines including replacement mounting hardware. Lead time is 2 to 4 weeks once measurements are confirmed.",
        [
            ("OSP-P200 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p200/"),
            ("OSP-P300 era way covers",   "/way-covers/okuma-cnc-way-covers/osp-p300/"),
        ],
    ),
}


# ============================================================
# FANUC WAY COVERS — controls-only, flipped hub structure
# ============================================================
_FANUC_WC_CONTROL_SPOKES = {
    "series-0-legacy": _wc_control(
        "fanuc", "series-0-legacy", "Series 0 Legacy", "Series 0 Legacy", "1980s through 1990s",
        "Way covers on Fanuc Series 0 / 0M / 0T era machines are almost universally custom-fabrication. These are deep-legacy machines from the 1980s and 1990s; OEM cover part numbers for the original integrators (Doosan, other Asian OEMs) are largely discontinued. We build to spec from existing covers, original drawings, or measurements off the machine.",
        "Series 0 era machines were built by many OEMs — older [Doosan Puma](/way-covers/doosan-cnc-way-covers/puma/) and other Asian-OEM lathes from this era. Each OEM had its own way-cover specifications, so we coordinate by machine model rather than by control generation alone.",
        [
            "Telescoping steel is the default for legacy Series 0 era machines.",
            "Original mounting hardware is often unavailable — replacement as part of the build.",
            "Measurements off the machine require coordination since these are 25-35+ year-old platforms.",
            "OEM specifications vary by machine integrator — confirm dimensions during quoting.",
        ],
        "Series 0 era way covers are almost universally custom-fabrication. OEM-spec parts are heavily aftermarket-only or fully discontinued.",
        "Custom fabrication to your existing cover, original drawings, or measurements off the machine. We can build replacement mounting hardware as part of the build when original hardware is unavailable. Lead time is 2 to 4 weeks once measurements are confirmed.",
        [
            ("Fanuc Series 6-15 era way covers",          "/way-covers/fanuc-cnc-way-covers/series-6-15-legacy/"),
            ("Fanuc Series 16i/18i/21i era way covers",   "/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/"),
        ],
    ),
    "series-6-15-legacy": _wc_control(
        "fanuc", "series-6-15-legacy", "Series 6 / 10 / 11 / 12 / 15", "Series 6 through 15", "1980s through 2000s",
        "Way covers on Fanuc Series 6, 10, 11, 12, and 15 era machines split between custom-fab and OEM-available depending on the underlying OEM and machine vintage. Series 15 machines from the late 1990s and 2000s sometimes still have OEM-spec available through the original integrator. The older Series 6-12 builds are typically custom-fab.",
        "Series 6 through 12 shipped on higher-end machines from various OEMs through the 1990s. Series 15 was common on larger and more sophisticated machines into the 2000s — including some larger [Doosan](/way-covers/doosan-cnc-way-covers/puma/) and other Asian-OEM platforms.",
        [
            "Telescoping steel is the default for Series 6-15 era machines.",
            "Series 15 builds sometimes still have OEM-spec available through the original integrator.",
            "Series 6, 10, 11, 12 are typically custom-fab.",
            "OEM specifications vary by machine integrator — confirm dimensions during quoting.",
        ],
        "Series 6-12 era way covers are mostly custom-fab; Series 15 has somewhat better OEM availability through original integrators.",
        "Custom fabrication is the standard path for the older Series 6-12 builds. For Series 15 we check OEM availability before quoting. Lead time is 2 to 4 weeks.",
        [
            ("Fanuc Series 0 era way covers",              "/way-covers/fanuc-cnc-way-covers/series-0-legacy/"),
            ("Fanuc Series 16i/18i/21i era way covers",    "/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/"),
        ],
    ),
    "series-16i-18i-21i": _wc_control(
        "fanuc", "series-16i-18i-21i", "Series 16i / 18i / 21i", "Series 16i / 18i / 21i", "Roughly 1995 through 2010",
        "Way covers on Fanuc 16i / 18i / 21i era machines split between OEM-available and custom-fab. Many of the machines are still in production and the original integrators (Doosan, Haas, others) still have some OEM cover supply for the most common configurations. Less common configurations and older 16i builds are typically custom-fab.",
        "Series 16i / 18i / 21i shipped on a wide cross-section of late-1990s through 2000s machines. Many [Doosan Puma](/way-covers/doosan-cnc-way-covers/puma/) builds from this era ran 16i/18i/21i; some older [Haas](/way-covers/haas-cnc-way-covers/vf-series/) imports as well.",
        [
            "Telescoping steel is the default cover style on 16i/18i/21i era machines.",
            "OEM availability varies by the original integrator — Doosan and Haas have different parts situations.",
            "Common configurations (popular VF/ST/Puma sizes) tend to have better OEM supply.",
            "Less-common configurations may require custom-fab.",
        ],
        "16i/18i/21i era way cover parts depend on the original integrator. Doosan and Haas have separate parts channels; both still have some current supply on common configurations.",
        "Custom fabrication is the right path when OEM is no longer available or when timing makes custom better. We can build to existing covers, OEM drawings, or measurements off the machine. Lead time is 2 to 4 weeks.",
        [
            ("Fanuc Series 0i era way covers",                "/way-covers/fanuc-cnc-way-covers/series-0i/"),
            ("Fanuc Series 30i / 31i / 32i era way covers",   "/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/"),
        ],
    ),
    "series-0i": _wc_control(
        "fanuc", "series-0i", "Series 0i (A/B/C/D/F)", "Series 0i", "2003 through present",
        "Way covers on Fanuc Series 0i era machines are mostly OEM-available through the original integrators. The 0i family ships on a huge cross-section of current machines — most entry and mid-range Doosan Puma, all Doosan Lynx, older Haas imports, and many other platforms. Each integrator's OEM cover supply varies, but most current 0i-D and 0i-F builds have full OEM availability.",
        "Series 0i ships on the broadest cross-section of any Fanuc control — most entry and mid-range [Doosan Puma](/way-covers/doosan-cnc-way-covers/puma/) and all [Doosan Lynx](/way-covers/doosan-cnc-way-covers/lynx/), older [Haas](/way-covers/haas-cnc-way-covers/vf-series/) builds, and a huge fleet of imported Asian-OEM machines.",
        [
            "0i era machines are current production for most integrators — OEM way covers are widely available.",
            "0i-A and 0i-B builds (older end of the family) may have thinning OEM supply.",
            "0i-D and 0i-F are fully current with full OEM availability through Doosan, Haas, etc.",
            "Custom-fab is an option when OEM lead time or pricing pushes that direction.",
        ],
        "0i era way covers are mostly OEM-available through the original integrators. 0i-A and B may have thinning supply on the oldest builds.",
        "For 0i era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. Lead time is 2 to 4 weeks on most custom builds.",
        [
            ("Fanuc Series 16i/18i/21i era way covers",        "/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/"),
            ("Fanuc Series 30i / 31i / 32i era way covers",    "/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/"),
        ],
    ),
    "series-30i-31i-32i": _wc_control(
        "fanuc", "series-30i-31i-32i", "Series 30i / 31i / 32i / 35i", "Series 30i / 31i / 32i", "2008 through present",
        "Way covers on Fanuc 30i family machines are fully OEM-available through the original integrators. The 30i family ships on higher-end multi-axis machines — current Doosan Puma higher-end builds, all Puma MX/SMX multitasking, DVF 5-axis, NHM horizontals, larger DNM verticals. These are current production with full OEM cover supply.",
        "30i family ships on higher-end machines — most current [Doosan Puma](/way-covers/doosan-cnc-way-covers/puma/) (2600SY, 3100, 4100, 5100, 700, 800), all [Puma MX and SMX](/way-covers/doosan-cnc-way-covers/puma-mx-smx/), [DVF 5-axis](/way-covers/doosan-cnc-way-covers/5-axis-verticals/), [NHM/NHP/HC horizontals](/way-covers/doosan-cnc-way-covers/horizontals/), and the higher-end [DNM verticals](/way-covers/doosan-cnc-way-covers/dnm-verticals/).",
        [
            "30i family machines are current production — way covers are fully OEM-available.",
            "Higher-end multi-axis platforms have more complex cover sets — we coordinate as packages.",
            "Custom-fab is an option when OEM timing or pricing favors that path.",
        ],
        "30i family era way cover parts are fully OEM-available through the original integrators.",
        "For 30i era machines the conversation is mostly about whether OEM-spec or custom-fab is the right path for your specific timeline and cost. Lead time is 2 to 4 weeks on most custom builds; multi-axis cover sets sometimes run slightly longer when coordination is needed.",
        [
            ("Fanuc Series 0i era way covers",                  "/way-covers/fanuc-cnc-way-covers/series-0i/"),
            ("Fanuc Series 16i / 18i / 21i era way covers",      "/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/"),
        ],
    ),
    "power-mate-i": _wc_control(
        "fanuc", "power-mate-i", "Power Mate i", "Power Mate i", "2000 through present",
        "Power Mate i is the Fanuc dedicated-axis control — it shows up on rotary tables, indexers, sub-spindles, and bar feeders integrated alongside primary CNC platforms. Way covers for Power Mate i-controlled axes are typically smaller and more specialized than primary-axis covers. We coordinate with the primary machine's cover requirements when both are factors.",
        "Power Mate i shows up as a dedicated-axis or sub-spindle control on rotary tables, indexers, bar feeders, and similar auxiliary equipment alongside primary CNC platforms.",
        [
            "Power Mate i covers are typically smaller and more specialized than primary-axis covers.",
            "Bar feeder mounting interacts with primary-machine covers — coordinate during quoting.",
            "Rotary indexer covers often use bellows or compact telescoping steel.",
        ],
        "Power Mate i covers depend on the integrator — most current builds have OEM availability through the primary machine OEM.",
        "Custom fabrication is straightforward for Power Mate i covers because the axis travel is shorter and the mounting is well documented. Lead time is 2 to 4 weeks.",
        [
            ("Fanuc Series 0i era way covers",                  "/way-covers/fanuc-cnc-way-covers/series-0i/"),
            ("Fanuc Series 30i / 31i / 32i era way covers",      "/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/"),
        ],
    ),
}


# ============================================================
# Aggregated WAY_COVERS_HUB_DATA
# ============================================================
WAY_COVERS_HUB_DATA = {
    "mazak": {
        "browse_series": [
            ("Quick Turn / QTN",                       "/way-covers/mazak-cnc-way-covers/quick-turn/",
             "Lathe way covers. Telescoping steel for slant-bed turning — QT-8 through QTN-450, MS/MSY variants."),
            ("Integrex",                               "/way-covers/mazak-cnc-way-covers/integrex/",
             "Mill-turn multitasking covers. Turning + B-axis traverse + sub-spindle coordination."),
            ("Variaxis",                               "/way-covers/mazak-cnc-way-covers/variaxis/",
             "5-axis trunnion covers. Linear + trunnion-adjacent — i-300 through i-800 and legacy 500/630/730."),
            ("Vertical Machining Centers (VTC + VCN)", "/way-covers/mazak-cnc-way-covers/vertical-machining-centers/",
             "Production vertical covers. Highest-volume Mazak orders — VTC-16 through VTC-800, VCN family."),
            ("HCN Horizontals",                        "/way-covers/mazak-cnc-way-covers/hcn-horizontal/",
             "Horizontal covers + pallet-interface sealing. HCN-4000 through HCN-10800."),
            ("Turning Legacy",                         "/way-covers/mazak-cnc-way-covers/turning-legacy/",
             "Older Mazak turning. Custom-fab almost always — Slant Turn, Multiplex, Megaturn, HQR, Powermaster."),
        ],
        "browse_control": [
            ("Mazatrol Legacy era",   "/way-covers/mazak-cnc-way-covers/mazatrol-legacy/",
             "Pre-2005 machines. Custom-fab the standard path; OEM mostly discontinued."),
            ("Mazatrol Matrix era",   "/way-covers/mazak-cnc-way-covers/mazatrol-matrix/",
             "2005-2013 machines. Split between OEM-available and custom-fab depending on specific cover."),
            ("Mazatrol Smooth era",   "/way-covers/mazak-cnc-way-covers/smooth-control/",
             "2013-present. Fully OEM-supported through Mazak; custom-fab when timing or pricing favors."),
        ],
        "browse_service": [
            ("Mazak machine repair",                   "/repairs/mazak-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-way-cover Mazak service work."),
            ("Mazak spindle repair",                   "/spindle-grinding/mazak-spindle-repair/",
             "Bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Cover style, dimensions, and shipping",  "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What way cover styles do you build for Mazak machines?",
             "Telescoping steel for most turning and production-vertical applications, bellows for trunnion-adjacent areas on Variaxis and some Integrex configurations, roll-up for specific retrofit and clearance situations. We match what's on the machine or build the right style for the operating conditions."),
            ("How long does a Mazak way cover order take?",
             "2 to 4 weeks on most orders. Complex multi-axis cover sets (full Integrex, Variaxis, or HCN cover packages) can run slightly longer when coordination is needed. Rush options are available — call to discuss."),
            ("Can you build covers for legacy Mazatrol machines (Slant Turn, Multiplex, etc.)?",
             "Yes. Mazatrol Legacy era covers are almost always custom-fabrication in 2026 because OEM parts are mostly discontinued. We build to spec from your existing cover, the original Mazak drawing, or measurements off the machine."),
            ("Do I need OEM-original covers or can custom-fab match Mazak quality?",
             "Custom-fab to OEM-spec or to your specific operating-condition requirements gives equivalent or better service in most cases. We match dimensions, mounting, and material to OEM standards. The decision usually comes down to whether OEM is even available for your machine."),
            ("Can you handle the trunnion-adjacent covers on Variaxis 5-axis machines?",
             "Yes. Variaxis trunnion-adjacent covers are a specialty — bellows or fabric sized to clear the rotating workpiece envelope. We coordinate with the linear-axis covers as a full set."),
            ("Do you ship Mazak way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US. Field installation is most economical in Iowa and adjacent states; longer-haul installations are by arrangement."),
        ],
        "series_spokes":  _MAZAK_WC_SERIES_SPOKES,
        "control_spokes": _MAZAK_WC_CONTROL_SPOKES,
        "hero_lede": "Mazak way covers manufactured to spec across the Midwest — telescoping steel, bellows, and roll-up styles for every Mazak platform. Quick Turn lathes, Integrex multitasking, Variaxis 5-axis, VTC and VCN verticals, HCN horizontals, and the turning legacy lineup. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Mazak way cover orders fall into a few patterns: chip ingress damage on heavily used VTC and VCN production verticals, pallet-changer interface wear on HCN horizontals, trunnion-adjacent cover damage on Variaxis 5-axis, complex multi-axis cover sets on Integrex multitasking, and custom-fab requests on legacy Slant Turn / Multiplex / Megaturn machines where OEM parts have been discontinued. We match the original or build to spec for the operating conditions.",
        "how_we_approach": "Mazak way cover orders start with confirming the platform, the cover style (telescoping / bellows / roll-up), and the dimensions. For OEM-current machines (Smooth-era and some Matrix-era) we route to OEM-spec or custom-fab depending on timing and cost. For Legacy and older Matrix builds, custom fabrication is the standard path. The fabrication itself is straightforward; the time-consuming part is measurement coordination on older machines.",
        "browse_control_intro": "Mazak way cover sourcing patterns differ by machine era. Pick yours for parts-availability and fabrication notes.",
    },

    "haas": {
        "browse_series": [
            ("VF Series",                          "/way-covers/haas-cnc-way-covers/vf-series/",
             "Vertical mill covers. Highest-volume Haas orders — VF-1 through VF-12, YT and SS variants."),
            ("ST Series",                          "/way-covers/haas-cnc-way-covers/st-series/",
             "Lathe covers. Telescoping steel for slant-bed — ST-10 through ST-55, DS-30 dual-spindle."),
            ("UMC Series",                         "/way-covers/haas-cnc-way-covers/umc-series/",
             "5-axis trunnion covers. Linear + trunnion-adjacent — UMC-350 through UMC-1600."),
            ("EC Series",                          "/way-covers/haas-cnc-way-covers/ec-series/",
             "Horizontal covers + pallet-interface sealing. EC-300 through EC-3000."),
            ("Mini Mill / Toolroom / DT / DM / VM","/way-covers/haas-cnc-way-covers/mini-mill-toolroom/",
             "Compact and toolroom covers. Mini Mill, TM Toolroom, DT drill-tap, DM, VM mold machines."),
            ("Toolroom Lathes (TL / CL)",          "/way-covers/haas-cnc-way-covers/toolroom-lathes/",
             "TL-1 through TL-4 and CL-1 — bridging toolroom and production turning."),
        ],
        "browse_control": [
            ("Haas Classic Control era",  "/way-covers/haas-cnc-way-covers/haas-classic-control/",
             "Pre-NGC through 2014. Split between OEM and custom-fab; supply thinning."),
            ("Haas NGC era", "/way-covers/haas-cnc-way-covers/haas-ngc/",
             "2014-present. Fully OEM-supported through Haas; custom-fab when timing favors."),
        ],
        "browse_service": [
            ("Haas machine repair",            "/repairs/haas-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-way-cover Haas service work."),
            ("Haas spindle repair",            "/spindle-grinding/haas-spindle-repair/",
             "Bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Cover style, dimensions, and shipping", "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What way cover styles do you build for Haas machines?",
             "Telescoping steel for most VF and ST applications, bellows for some UMC trunnion-adjacent areas, roll-up for specific retrofit situations. We match what's on the machine or build the right style for the operating conditions."),
            ("How long does a Haas way cover order take?",
             "2 to 4 weeks on most orders. UMC 5-axis cover sets can run slightly longer because the trunnion-adjacent coordination requires more time. Rush options are available."),
            ("Can you build covers for older Haas Classic Control machines?",
             "Yes. Classic Control era Haas covers split between OEM-available and custom-fab depending on the specific model and cover. We check availability first; when OEM is no longer available we build to spec from your existing cover or the original drawing."),
            ("Do you handle UMC trunnion-adjacent covers?",
             "Yes. UMC trunnion-adjacent covers are a specialty — bellows or fabric sized to clear the rotating workpiece envelope. We coordinate with the linear-axis covers as a full set."),
            ("Are aftermarket way covers as good as Haas OEM?",
             "Custom-fab to OEM-spec or to your specific operating-condition requirements gives equivalent or better service in most cases. We match dimensions, mounting, and material. Heavy-use environments sometimes benefit from heavier-than-OEM specifications."),
            ("Do you ship Haas way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US."),
        ],
        "series_spokes":  _HAAS_WC_SERIES_SPOKES,
        "control_spokes": _HAAS_WC_CONTROL_SPOKES,
        "hero_lede": "Haas way covers manufactured to spec across the Midwest — telescoping steel, bellows, and roll-up styles for every Haas platform. VF and ST production machines, UMC 5-axis with trunnion coordination, EC horizontals with pallet-interface sealing, and the compact Mini Mill / DT / DM / VM family. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Haas way cover orders fall into a few patterns: chip ingress damage on heavily used VF and ST machines, pallet-changer interface wear on EC horizontals, trunnion-adjacent damage on UMC 5-axis, high-cycle wear on DT drill-tap and compact-family covers. For Classic-era machines (pre-2014), custom-fab is increasingly the path because OEM supply is thinning. For NGC-era machines (2014-present), OEM is fully available and we route to whichever path makes sense.",
        "how_we_approach": "Haas way cover orders start with confirming the platform and the control era. NGC-era machines route to OEM-spec or custom-fab depending on timing and cost. Classic-era machines increasingly route to custom fabrication as OEM supply thins. The fabrication itself is straightforward; we coordinate cover style, dimensions, and mounting hardware to match either the OEM original or your specific operating-condition requirements.",
        "browse_control_intro": "Haas way cover sourcing patterns differ by machine era. Pick yours for parts-availability and fabrication notes.",
    },

    "dmg-mori": {
        "browse_series": [
            ("NLX / ALX",                "/way-covers/dmg-mori-cnc-way-covers/nlx-turning/",
             "Universal-turning covers. NLX 1500 through 6000, ALX 1500 through 2500."),
            ("CTX / CLX",                "/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/",
             "Turning + TC turn-mill covers. CLX 350/450/550, CTX 310 through 850."),
            ("NTX",                      "/way-covers/dmg-mori-cnc-way-covers/ntx/",
             "Mill-turn multitasking covers. Coordinated turning + B-axis + sub-spindle sets."),
            ("DMU / DMC",                "/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/",
             "5-axis universal covers. DMU trunnion + monoBLOCK/duoBLOCK + DMC variants."),
            ("NHX / NH",                 "/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/",
             "Horizontal covers + pallet-interface sealing. NHX 4000 through 10000."),
            ("NVX / NV / NVD",           "/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/",
             "Production vertical covers. NVX 4000 through 7000, NV 4000/5000, NVD DCG."),
            ("CMX / CMX U",              "/way-covers/dmg-mori-cnc-way-covers/cmx/",
             "Entry production covers. CMX 600V through 1300V, CMX 50U/70U 5-axis."),
            ("DMP / Milltap",            "/way-covers/dmg-mori-cnc-way-covers/dmp-milltap/",
             "Compact production covers. High-cycle drill-tap — DMP 35 through 70, Milltap 700."),
            ("SPRINT / MULTISPRINT",     "/way-covers/dmg-mori-cnc-way-covers/sprint-multisprint/",
             "Swiss-style and production turning covers. SPRINT 20/32/50/65, MULTISPRINT 25/36."),
        ],
        "browse_control": [
            ("Siemens 840D era",   "/way-covers/dmg-mori-cnc-way-covers/siemens-840d/",
             "Original 840D (pre-2010) splits between OEM and custom-fab; solutionline mostly OEM."),
            ("Heidenhain TNC era", "/way-covers/dmg-mori-cnc-way-covers/heidenhain-tnc/",
             "iTNC 530 era splits; TNC 640 era mostly OEM-available through DMG Mori."),
            ("CELOS era",          "/way-covers/dmg-mori-cnc-way-covers/celos/",
             "2014-present. Fully OEM-supported through DMG Mori; custom-fab when timing favors."),
        ],
        "browse_service": [
            ("DMG Mori machine repair",        "/repairs/dmg-mori-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-way-cover DMG Mori service."),
            ("DMG Mori spindle repair",        "/spindle-grinding/dmg-mori-spindle-repair/",
             "Bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Cover style, dimensions, and shipping", "#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What way cover styles do you build for DMG Mori machines?",
             "Telescoping steel for most turning and production-vertical applications, bellows for DMU 5-axis trunnion-adjacent areas, roll-up for specific retrofit situations. We match what's on the machine or build the right style for the operating conditions."),
            ("How long does a DMG Mori way cover order take?",
             "2 to 4 weeks on most orders. DMU 5-axis full cover sets and NTX multitasking full sets can run slightly longer when coordination across multiple axes is needed. Rush options are available."),
            ("Can you build covers for older DMG Mori machines with original Siemens 840D?",
             "Yes. Original 840D era (pre-2010) DMG Mori covers split between OEM-available and custom-fab. We check availability and route accordingly. Custom-fab to your existing cover or OEM drawing is the path when OEM is no longer in supply."),
            ("Do you handle DMU trunnion-adjacent covers?",
             "Yes. DMU trunnion-adjacent covers are a specialty — bellows or fabric sized to clear the rotating workpiece envelope. We coordinate with the X/Y/Z linear-axis covers as a full set."),
            ("Are aftermarket way covers as good as DMG Mori OEM?",
             "Custom-fab to OEM-spec or to your specific operating-condition requirements gives equivalent or better service in most cases."),
            ("Do you ship DMG Mori way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US."),
        ],
        "series_spokes":  _DMG_MORI_WC_SERIES_SPOKES,
        "control_spokes": _DMG_MORI_WC_CONTROL_SPOKES,
        "hero_lede": "DMG Mori way covers manufactured to spec across the Midwest — telescoping steel, bellows, and roll-up styles for every DMG Mori platform. NLX and CTX turning, NTX mill-turn, DMU and DMC 5-axis with trunnion coordination, NHX horizontals, NVX verticals, and the CMX/DMP/SPRINT production lines. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most DMG Mori way cover orders fall into a few patterns: chip ingress damage on heavily used NVX production verticals, pallet-changer interface wear on NHX horizontals, trunnion-adjacent damage on DMU 5-axis, complex multi-axis cover sets on NTX multitasking. For older 840D-era machines, custom-fab is increasingly the path. For CELOS-era machines, OEM is fully available and we route to whichever path makes sense.",
        "how_we_approach": "DMG Mori way cover orders start with confirming the platform and the control era. CELOS-era machines route to OEM-spec or custom-fab depending on timing. Older Siemens 840D-era machines increasingly route to custom fabrication. Multi-axis cover sets (NTX, DMU 5-axis) coordinate as full packages because the dimensions interact.",
        "browse_control_intro": "DMG Mori way cover sourcing patterns differ by machine era and underlying control. Pick yours for parts-availability and fabrication notes.",
    },

    "doosan": {
        "browse_series": [
            ("Puma",                       "/way-covers/doosan-cnc-way-covers/puma/",
             "Horizontal-turning covers. Puma 230 through 800 with M/MS/LM/Y/SY variants and TT/GT/TW builds."),
            ("Puma MX / SMX",              "/way-covers/doosan-cnc-way-covers/puma-mx-smx/",
             "Mill-turn multitasking covers. Coordinated turning + B-axis traverse sets."),
            ("Puma V / VT / VTR",          "/way-covers/doosan-cnc-way-covers/puma-vertical-turning/",
             "Vertical-turning covers. Puma V400 through V9300 chuckers and VT/VTR ram-type."),
            ("Lynx",                       "/way-covers/doosan-cnc-way-covers/lynx/",
             "Compact-turning covers. Lynx 220 through 300, bar-feed coordination."),
            ("DNM",                        "/way-covers/doosan-cnc-way-covers/dnm-verticals/",
             "Vertical-machining covers. DNM 200 through 750 plus DNM 200/5AX 5-axis."),
            ("Horizontals (NHM / NHP / HC)","/way-covers/doosan-cnc-way-covers/horizontals/",
             "Horizontal covers + pallet-interface sealing. NHM 4000 through 8000, NHP, HC."),
            ("DVF / FM 5-Axis Verticals",  "/way-covers/doosan-cnc-way-covers/5-axis-verticals/",
             "5-axis trunnion vertical covers. DVF 5000/6500/8000 and FM 200/5AX."),
            ("Swiss-Type / DST",           "/way-covers/doosan-cnc-way-covers/swiss-turning/",
             "Swiss-style precision turning covers. SwiftTurn 32/38 and DST series."),
        ],
        "browse_control": [
            ("Fanuc 0i (Doosan)",  "/way-covers/fanuc-cnc-way-covers/series-0i/",
             "Entry and mid-range Doosan. Most Lynx and entry Puma builds; mostly OEM-available."),
            ("Fanuc 30i (Doosan)", "/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/",
             "Higher-end Puma, MX/SMX, DVF, NHM. Fully OEM-available through DN Solutions."),
        ],
        "browse_service": [
            ("Doosan machine repair",         "/repairs/doosan-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-way-cover Doosan service."),
            ("Doosan spindle repair",         "/spindle-grinding/doosan-spindle-repair/",
             "Bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Cover style, dimensions, and shipping","#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What way cover styles do you build for Doosan / DN Solutions machines?",
             "Telescoping steel for most Puma and Lynx applications, bellows for DVF 5-axis trunnion-adjacent areas and some Puma MX/SMX configurations, roll-up for specific retrofit situations. We match what's on the machine or build the right style for the operating conditions."),
            ("How long does a Doosan way cover order take?",
             "2 to 4 weeks on most orders. Puma MX/SMX multitasking sets and DVF 5-axis sets can run slightly longer when coordination is needed. Rush options are available."),
            ("Doosan rebranded to DN Solutions — does that affect way covers?",
             "No. The hardware and dimensions are the same. We work from machine model rather than corporate name."),
            ("Can you build covers for Doosan machines with older Fanuc 16i/18i/21i controls?",
             "Yes. We check OEM availability through DN Solutions; for configurations where OEM is no longer available we build to spec from your existing cover or measurements off the machine."),
            ("Do you handle DVF trunnion-adjacent covers?",
             "Yes. DVF 5-axis trunnion-adjacent covers are a specialty — bellows or fabric sized to clear the rotating workpiece envelope."),
            ("Do you ship Doosan way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US."),
        ],
        "series_spokes":  _DOOSAN_WC_SERIES_SPOKES,
        "control_spokes": {},  # Doosan controls cross-link to Fanuc canonical way-covers spokes
        "hero_lede": "Doosan and DN Solutions way covers manufactured to spec across the Midwest — telescoping steel, bellows, and roll-up styles for every Doosan platform. Puma horizontal turning, Lynx compact lathes, DNM verticals, NHM horizontals, DVF 5-axis with trunnion coordination, and the multitasking Puma MX/SMX. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Doosan way cover orders fall into a few patterns: chip ingress on Puma and Lynx production lathes, pallet-changer interface wear on NHM horizontals, trunnion-adjacent damage on DVF 5-axis, complex multi-axis cover sets on Puma MX/SMX. For most current Doosan builds (Fanuc 0i and 30i era), OEM cover supply through DN Solutions is good and we route to OEM-spec or custom-fab depending on timing.",
        "how_we_approach": "Doosan way cover orders start with confirming the platform and the Fanuc control generation. Current 0i-D, 0i-F, and 30i machines have full OEM availability through DN Solutions. Older 0i-A/B and 16i/18i/21i builds increasingly route to custom-fab when OEM is no longer in supply. Multi-axis cover sets (Puma MX/SMX, DVF) coordinate as packages.",
        "browse_control_intro": "Doosan ships almost exclusively on Fanuc. Pick the Fanuc generation your Doosan machine runs for way cover sourcing and fabrication notes.",
    },

    "okuma": {
        "browse_series": [
            ("LB / LU Lathes",                "/way-covers/okuma-cnc-way-covers/lb-lu-lathes/",
             "Horizontal-lathe covers. LB 200 through 5000 EX, LU 300 through 8000, live-tool variants."),
            ("Genos",                         "/way-covers/okuma-cnc-way-covers/genos/",
             "'Affordable Excellence' covers. Genos L250 through L4000 lathes, M460/M560/M660 verticals."),
            ("MB / MA Verticals",             "/way-covers/okuma-cnc-way-covers/mb-ma-verticals/",
             "Vertical-machining workhorse covers. MB-46V through MB-66V, MA-400 through MA-8000."),
            ("MULTUS",                        "/way-covers/okuma-cnc-way-covers/multus/",
             "B-axis multitasking covers. MULTUS B200 through B750, U3000 through U5000."),
            ("Twin-Spindle / Twin-Turret",    "/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/",
             "2SP-2500H, 2SP-V40, LT 200-MY through LT 2000 EX, historic LT-15/25."),
            ("VTM Vertical Turning",          "/way-covers/okuma-cnc-way-covers/vtm/",
             "Large vertical-turning covers. VTM-65, VTM-100, VTM-120, VTM-180."),
            ("MU 5-Axis / MCR Bridge",        "/way-covers/okuma-cnc-way-covers/v-bridge-mills/",
             "5-axis trunnion (MU-400V through MU-8000V) and bridge mills (MCR-A5C, MCR-BIII)."),
            ("LAW / LFS Heavy Lathes",        "/way-covers/okuma-cnc-way-covers/heavy-lathes/",
             "Heavy-duty turning covers. LAW 1000 through 3000 and LFS-590 flat-bed turning."),
        ],
        "browse_control": [
            ("OSP-P200 era",   "/way-covers/okuma-cnc-way-covers/osp-p200/",
             "Late-life Okuma. OEM availability thinning; custom-fab increasingly the path."),
            ("OSP-P300 era",   "/way-covers/okuma-cnc-way-covers/osp-p300/",
             "Mid-life Okuma. Mostly OEM-available through Okuma channels."),
            ("OSP-P500 era",   "/way-covers/okuma-cnc-way-covers/osp-p500/",
             "Current Okuma. Fully OEM-supported; custom-fab when timing favors."),
            ("OSP Legacy era", "/way-covers/okuma-cnc-way-covers/osp-legacy/",
             "Pre-2003. Custom-fab almost universally; OEM mostly discontinued."),
        ],
        "browse_service": [
            ("Okuma machine repair",          "/repairs/okuma-cnc-machine-repair/",
             "ATC, drive, control, way alignment — non-way-cover Okuma service."),
            ("Okuma spindle repair",          "/spindle-grinding/okuma-spindle-repair/",
             "Bearing-pack rebuilds, taper grinding, balancing, runout verification."),
            ("Cover style, dimensions, and shipping","#faq",
             "Covered in the FAQ below."),
        ],
        "faq": [
            ("What way cover styles do you build for Okuma machines?",
             "Telescoping steel for most LB/LU and MB/MA applications, bellows for MU 5-axis trunnion-adjacent areas and some MULTUS configurations, roll-up for specific retrofit situations. We match what's on the machine or build the right style for the operating conditions."),
            ("How long does an Okuma way cover order take?",
             "2 to 4 weeks on most orders. MULTUS multitasking sets and MU 5-axis sets can run slightly longer when coordination is needed."),
            ("Can you build covers for Okuma OSP Legacy machines (pre-2003)?",
             "Yes. OSP Legacy era covers are almost universally custom-fabrication because OEM parts are mostly discontinued. We build to spec from your existing cover, the original Okuma drawing, or measurements off the machine."),
            ("Okuma is known for thermal stability — does that affect cover service?",
             "It affects how long covers stay in spec on a well-maintained machine. The wear patterns are predictable. Cover replacement timing is more about chip-ingress damage and seal wear than thermal drift."),
            ("Do you handle MU trunnion-adjacent covers?",
             "Yes. MU 5-axis trunnion-adjacent covers are a specialty — bellows or fabric sized to clear the rotating workpiece envelope."),
            ("Do you ship Okuma way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US."),
        ],
        "series_spokes":  _OKUMA_WC_SERIES_SPOKES,
        "control_spokes": _OKUMA_WC_CONTROL_SPOKES,
        "hero_lede": "Okuma way covers manufactured to spec across the Midwest — telescoping steel, bellows, and roll-up styles for every Okuma platform. LB and LU horizontal lathes, MB and MA verticals, MULTUS multitasking, MU 5-axis with trunnion coordination, MCR bridge mills, and the heavy LAW lathe line. Find your model below, or browse by series, control generation, or service type.",
        "what_brings": "Most Okuma way cover orders fall into a few patterns: chip ingress on heavily used LB/LU lathes and MB/MA verticals, trunnion-adjacent damage on MU 5-axis, multi-cover coordination on MULTUS multitasking, heavy-duty cover specifications on LAW heavy lathes. For OSP-P300 and P500 era machines, OEM cover supply is good. For P200 era, OEM is thinning. For OSP Legacy era, custom-fab is the standard path.",
        "how_we_approach": "Okuma way cover orders start with confirming the platform and the OSP generation. P500 era is current production with full OEM availability. P300 era is mostly OEM-available. P200 era is split between OEM and custom-fab. OSP Legacy era is custom-fab almost universally. The fabrication itself is straightforward; the time-consuming part is measurement coordination on older machines.",
        "browse_control_intro": "Okuma way cover sourcing patterns differ by OSP control era. Pick yours for parts-availability and fabrication notes.",
    },

    "fanuc": {
        "browse_series": [
            ("Doosan / DN Solutions", "/way-covers/doosan-cnc-way-covers/",
             "Most Doosan lathes and verticals ship on Fanuc 0i or 30i."),
            ("Haas (older)",          "/way-covers/haas-cnc-way-covers/",
             "Some older Haas imports shipped with Fanuc controls before NGC."),
        ],
        "browse_series_header": "Brands that ship Fanuc controls",
        "browse_series_intro": "Fanuc is primarily a controls vendor — your machine is built by one of these OEMs and uses a Fanuc control. Way cover sourcing comes through the original integrator (Doosan, Haas, etc.). Pick the brand for series-specific cover notes, or pick a Fanuc generation below for era-based parts-availability framing.",
        "browse_control": [
            ("Series 0 Legacy", "/way-covers/fanuc-cnc-way-covers/series-0-legacy/",
             "1980s-1990s. Custom-fab almost universally; original integrators discontinued."),
            ("Series 6 / 10 / 11 / 12 / 15",      "/way-covers/fanuc-cnc-way-covers/series-6-15-legacy/",
             "1980s-2000s. Mostly custom-fab; Series 15 sometimes has OEM through original integrator."),
            ("Series 16i / 18i / 21i",            "/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/",
             "1995-2010. Split between OEM-available and custom-fab; depends on integrator."),
            ("Series 0i (A/B/C/D/F)",             "/way-covers/fanuc-cnc-way-covers/series-0i/",
             "2003-present. Mostly OEM-available through original integrators."),
            ("Series 30i / 31i / 32i / 35i",      "/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/",
             "2008-present. Fully OEM-available through original integrators."),
            ("Power Mate i",                      "/way-covers/fanuc-cnc-way-covers/power-mate-i/",
             "Dedicated-axis covers — rotary indexers, sub-spindles, bar feeders."),
        ],
        "browse_service": [
            ("Cover style and fabrication paths",  "#faq",
             "Telescoping / bellows / roll-up style selection — covered in the FAQ."),
            ("Custom fabrication for legacy machines", "#faq",
             "Building covers from existing parts or drawings — covered in the FAQ."),
            ("Cross-brand cover coordination",      "#faq",
             "Coordinating covers across Doosan + Haas + other Fanuc-controlled OEMs — covered in the FAQ."),
        ],
        "faq": [
            ("Why is the Fanuc way-covers page structured differently?",
             "Fanuc is primarily a controls vendor — your machine is built by Doosan, Haas, or another OEM. Way cover sourcing comes through the original integrator, not Fanuc directly. Our Fanuc way-covers hub is organized by control generation because that's the right lens for parts availability — Fanuc generation correlates with machine era which correlates with OEM cover supply."),
            ("Which Fanuc generation do you see most often for way covers?",
             "Series 0i (specifically 0i-D and 0i-F) is by far the most common Fanuc generation on machines we build covers for. Series 16i/18i/21i is second-most-common — many late-1990s through 2000s machines still in production. Series 30i is growing as those builds age."),
            ("Can you build covers for Doosan or Haas machines with older Fanuc controls?",
             "Yes. We work from the machine model rather than the control alone. For older Doosan Puma with Fanuc 16i/18i/21i, we check OEM availability through DN Solutions; if OEM is no longer available, custom-fab to spec from your existing cover. Same workflow for older Haas with Classic Control."),
            ("Do Fanuc-controlled machines use different cover styles than non-Fanuc machines?",
             "No. Cover style (telescoping steel / bellows / roll-up) is determined by the machine's mechanical design, not the control. Most Fanuc-controlled production lathes use telescoping steel; verticals and 5-axis machines mix telescoping with bellows for trunnion-adjacent areas."),
            ("How does cross-brand coordination work for shops with mixed fleets?",
             "Many shops run Fanuc-controlled machines from multiple OEMs. We can build covers for multiple machines in a single coordinated order across Doosan, Haas, and other Fanuc-controlled platforms. Coordination on shipping and installation is part of the package."),
            ("Do you ship Fanuc-controlled machine way covers outside Iowa?",
             "Yes. We ship anywhere in the continental US."),
        ],
        "series_spokes":  {},  # Fanuc flips structure
        "control_spokes": _FANUC_WC_CONTROL_SPOKES,
        "hero_lede": "Fanuc is primarily a controls vendor — your machine is built by Doosan, Haas, or another OEM and runs a Fanuc control. Way covers come through the original integrator's parts supply, framed by the Fanuc control generation (which correlates with machine era). We build covers to spec for the full Fanuc-controlled fleet from deep-legacy Series 0 through current 30i-B. Find your control below, or browse by service type.",
        "what_brings": "Most Fanuc-controlled-machine way cover orders split between three patterns. Deep-legacy Series 0 and 6-15 — custom-fab almost universally because original integrator OEM supply is gone. Mid-life Series 16i/18i/21i — split between OEM-available and custom-fab depending on the integrator. Current Series 0i and 30i — mostly OEM-available through Doosan, Haas, etc., with custom-fab as an option when timing favors. The era frames the parts-availability conversation.",
        "how_we_approach": "Fanuc way cover work starts with confirming the machine OEM (Doosan, Haas, or other) and the control generation. From there it's a fork: current 0i/30i machines route through OEM-spec with custom-fab as an option; mid-life 16i/18i/21i splits between paths; legacy generations route through custom fabrication.",
        "browse_control_intro": "Fanuc-controlled machine way cover sourcing patterns differ by control generation. Pick yours for era-based parts-availability framing.",
    },
}
