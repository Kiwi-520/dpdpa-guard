"""
Layer 8a — Terminal Reporter
=============================
Takes the fully enriched output from all previous layers
and formats it into clean, readable terminal output.

This is what the developer sees when they run dpdpa-guard.

Input:  Full data dict from Layer 6 (linkage_check output)
Output: Same dict unchanged + prints formatted report to terminal
        Optionally returns formatted string for CLI use

Design principle:
    Every finding must be actionable.
    Every section reference must be traceable.
    A developer should be able to read this in under 2 minutes
    and know exactly what to fix.
"""

import os
from datetime import datetime


# ── Colour codes for terminal output ─────────────────────────────────────────
# Fallback gracefully if terminal does not support colours

class Colour:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    GREEN   = "\033[92m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"

def _c(text: str, colour: str) -> str:
    """Wrap text in colour codes."""
    return f"{colour}{text}{Colour.RESET}"

def _bold(text: str) -> str:
    return f"{Colour.BOLD}{text}{Colour.RESET}"


# ── Risk level colours ────────────────────────────────────────────────────────

RISK_COLOURS = {
    "CRITICAL": Colour.RED,
    "HIGH":     Colour.YELLOW,
    "MEDIUM":   Colour.MAGENTA,
    "LOW":      Colour.GREEN,
    "NONE":     Colour.GREEN,
    "UNKNOWN":  Colour.GREY,
}

def _risk(level: str) -> str:
    colour = RISK_COLOURS.get(level, Colour.GREY)
    return _c(f"[{level}]", colour)


# ── Separator helpers ─────────────────────────────────────────────────────────

WIDTH = 65

def _line(char: str = "─") -> str:
    return char * WIDTH

def _double_line() -> str:
    return "═" * WIDTH

def _section_header(title: str) -> str:
    return f"\n{_bold(title)}\n{_line()}"


# ── Main reporter function ────────────────────────────────────────────────────

def terminal_report(final_data: dict, return_string: bool = False) -> dict:
    """
    Formats and prints the complete compliance report to terminal.

    Args:
        final_data:     Complete data dict from Layer 6
        return_string:  If True, also returns the formatted string
                        (used by CLI for piping output)

    Returns:
        final_data unchanged (pipeline continues)
    """

    lines = []

    def add(text: str = ""):
        lines.append(text)

    metadata        = final_data["metadata"]
    entities        = final_data["entities"]
    summary         = metadata.get("compliance_summary", {})
    linkage         = metadata.get("linkage_risk", {})
    children        = metadata.get("children_data_entities_requiring_review", {})

    # ── Header ────────────────────────────────────────────────────────────────
    add(_double_line())
    add(_bold(_c("  dpdpa-guard — DPDPA 2023 Compliance Report", Colour.CYAN)))
    add(_double_line())
    add()

    # ── Scan metadata ─────────────────────────────────────────────────────────
    source_tag  = metadata.get("source_tag", "Unknown")
    filename    = os.path.basename(source_tag)
    scanned_at  = metadata.get("scanned_at", "Unknown")
    purpose     = metadata.get("business_purpose", "unknown_purpose")
    source_cat  = metadata.get("source", "UNKNOWN")

    add(f"  {'File:':<22} {filename}")
    add(f"  {'Full path:':<22} {_c(source_tag, Colour.GREY)}")
    add(f"  {'Scanned:':<22} {scanned_at}")
    add(f"  {'Source category:':<22} {source_cat}")
    add(f"  {'Inferred purpose:':<22} {_c(purpose, Colour.CYAN)}")
    add()

    # ── Compliance summary ────────────────────────────────────────────────────
    add(_section_header("COMPLIANCE SUMMARY"))
    add()

    total     = summary.get("total_entities_assessed", 0)
    violations = summary.get("entities_with_violations", 0)
    max_pen   = summary.get("max_penalty_exposure_crore", 0)
    risk      = summary.get("overall_risk_level", "UNKNOWN")
    urgent    = summary.get("requires_immediate_action", False)
    children_flag = summary.get("children_data_detected", False)

    risk_display  = _risk(risk)
    urgent_display = _c("⚠  YES — Act before shipping", Colour.RED) if urgent else _c("No", Colour.GREEN)

    add(f"  {'Entities detected:':<30} {total}")
    add(f"  {'Violations found:':<30} {_c(str(violations), Colour.RED if violations > 0 else Colour.GREEN)}")
    add(f"  {'Overall risk level:':<30} {risk_display}")
    add(f"  {'Max penalty exposure:':<30} ₹{max_pen} crore")
    add(f"  {'Immediate action required:':<30} {urgent_display}")

    if children_flag:
        add(f"  {'Children data detected:':<30} {_c('⚠  YES — Section 9 applies', Colour.RED)}")

    violation_types = summary.get("violation_types_found", set())
    if violation_types:
        add()
        add(f"  {_bold('Violation types found:')}")
        for vt in sorted(violation_types):
            add(f"    • {_c(vt, Colour.YELLOW)}")

    add()

    # ── Children data warning (if detected) ───────────────────────────────────
    if children_flag and children.get("children_data_detected"):
        add(_section_header(_c("⚠  CHILDREN DATA WARNING — SECTION 9 DPDPA", Colour.RED)))
        add()
        add(f"  Signal:   {children.get('children_data_signal', 'Unknown')}")
        keywords = children.get("children_data_keywords_found", [])
        if keywords:
            add(f"  Keywords: {', '.join(keywords)}")
        add()
        add(f"  {_c(children.get('children_data_disclaimer', ''), Colour.YELLOW)}")
        add()
        add("  Section 9 obligations:")
        add("    • Verifiable parental consent required before any processing")
        add("    • Behavioural monitoring of children is prohibited")
        add("    • Targeted advertising directed at children is prohibited")
        add("    • Penalty for breach: up to ₹200 crore — Schedule Item 3")
        add()

    # ── Linkage risk section ──────────────────────────────────────────────────
    if linkage:
        linkage_score = linkage.get("overall_linkage_score", "NONE")
        rules_fired   = linkage.get("rules_fired", 0)

        add(_section_header("LINKAGE RISK — QUASI-IDENTIFIER ANALYSIS"))
        add()
        add(f"  {'Overall linkage score:':<30} {_risk(linkage_score)}")
        add(f"  {'Re-identification risk:':<30} {_c('Yes', Colour.RED) if linkage.get('re_identification_risk') else _c('No', Colour.GREEN)}")
        add(f"  {'Rules checked:':<30} {linkage.get('rules_checked', 0)}")
        add(f"  {'Combinations detected:':<30} {rules_fired}")

        if rules_fired > 0:
            add()
            add(f"  {_bold('Combinations found:')}")
            for combo in linkage.get("combinations_found", []):
                add()
                add(f"    {_risk(combo['risk_level'])} {_bold(combo['name'])}")
                add(f"    Rule:      {combo['rule_id']}")
                add(f"    Types:     {', '.join(combo['combination'])}")
                add(f"    DPDPA ref: {combo['dpdpa_reference']}")
                if combo.get("context_escalated"):
                    add(f"    {_c('⚠ Escalated: ' + combo.get('escalation_reason', ''), Colour.YELLOW)}")
                add(f"    {_c(combo['description'], Colour.GREY)}")

            add()
            add(f"  {_bold('Linkage risk actions:')}")
            for action in linkage.get("recommended_actions", []):
                add(f"    • {action}")

        add()

    # ── Entity findings ───────────────────────────────────────────────────────
    add(_section_header("ENTITY FINDINGS"))

    # Group by risk level — CRITICAL first
    priority_order  = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
    grouped         = {level: [] for level in priority_order}

    for entity in entities:
        da    = entity.get("dpdpa_assessment", {})
        level = da.get("risk_level", "UNKNOWN")
        if level not in grouped:
            level = "UNKNOWN"
        grouped[level].append(entity)

    for level in priority_order:
        group = grouped[level]
        if not group:
            continue

        add()
        add(f"  {_risk(level)} — {len(group)} {'entity' if len(group) == 1 else 'entities'}")
        add(f"  {_line('·')}")

        for entity in group:
            da      = entity.get("dpdpa_assessment", {})
            etype   = entity.get("entity_type", "UNKNOWN")
            evalue  = entity.get("entity", "")
            purpose = entity.get("processing_purpose", "unknown")
            valid   = da.get("purpose_valid", False)
            sections = da.get("governing_sections", [])
            flags   = da.get("voilation_flags", [])
            penalty = da.get("penalty_exposure_crore", 0)
            actions = da.get("recommended_actions", [])
            consent = da.get("consent_required", "unknown")
            sensitivity = da.get("sensitivity", "UNKNOWN")

            # Mask the actual value partially for display
            masked_value = _mask_entity(evalue, etype)

            add()
            add(f"  {_bold(etype)}")
            add(f"    Value (masked):  {_c(masked_value, Colour.GREY)}")
            add(f"    Purpose:         {purpose}")
            add(f"    Sensitivity:     {sensitivity}")
            add(f"    Consent needed:  {consent}")
            add(f"    Purpose valid:   {_c('Yes ✓', Colour.GREEN) if valid else _c('No ✗', Colour.RED)}")
            add(f"    DPDPA sections:  {', '.join(sections) if sections else 'See assessment'}")
            add(f"    Penalty exposure: ₹{penalty} crore")

            if flags:
                add(f"    Violations:")
                for flag in flags:
                    add(f"      • {_c(flag, Colour.YELLOW)}")

            if actions:
                add(f"    Actions required:")
                for action in actions[:3]:       # Show top 3 actions
                    add(f"      → {action}")
                if len(actions) > 3:
                    add(f"      → ...and {len(actions) - 3} more actions (see JSON report)")

    add()

    # ── Footer ────────────────────────────────────────────────────────────────
    add(_double_line())
    add(_bold("  DISCLAIMER"))
    add(_line())
    add("  This report provides automated guidance based on DPDPA 2023.")
    add("  It is not legal advice. Verify findings with qualified privacy")
    add("  counsel before making compliance decisions.")
    add()
    add("  Law reference: Digital Personal Data Protection Act, 2023")
    add("  Gazette No. CG-DL-E-12082023-248045, August 11, 2023")
    add(_double_line())
    add()

    # ── Print to terminal ─────────────────────────────────────────────────────
    output_string = "\n".join(lines)
    print(output_string)

    if return_string:
        return final_data, output_string

    return final_data


# ── Entity masking helper ─────────────────────────────────────────────────────

def _mask_entity(value: str, entity_type: str) -> str:
    """
    Partially masks entity values for display.
    Shows enough to identify the entity without exposing full sensitive data.
    """
    if not value:
        return "—"

    length = len(value)

    # High sensitivity — show only last 4 characters
    high_sensitivity = {"AADHAAR", "PAN", "PASSPORT", "VOTER_ID",
                        "DRIVING_LICENSE", "CREDIT_CARD"}
    if entity_type in high_sensitivity:
        if length <= 4:
            return "*" * length
        return "*" * (length - 4) + value[-4:]

    # Medium sensitivity — show first 3 and last 2
    medium_sensitivity = {"PHONE", "UPI", "IFSC", "VEHICLE_REG", "GSTIN"}
    if entity_type in medium_sensitivity:
        if length <= 5:
            return value[0] + "*" * (length - 1)
        return value[:3] + "*" * (length - 5) + value[-2:]

    # Email — mask local part, show domain
    if entity_type == "EMAIL":
        at_pos = value.find("@")
        if at_pos > 0:
            local  = value[:at_pos]
            domain = value[at_pos:]
            masked_local = local[0] + "*" * (len(local) - 1) if len(local) > 1 else "*"
            return masked_local + domain
        return value[:2] + "*" * (length - 2)

    # Low sensitivity — show as-is (name, location, IP)
    return value


# ── Run standalone ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from ingestion_layer  import file_upload
    from detector_layer   import detector, boundary_checkor, valid_check
    from normalizer_layer import normalizer
    from purpose_layer    import purpose_info
    from engine_layer     import assessment, report
    from linkage_layer    import linkage_check

    filename = "sample_doc.txt"

    file_content     = file_upload(filename)
    detected_data    = detector(file_content)
    boundary_checked = boundary_checkor(file_content, detected_data)
    validated        = valid_check(boundary_checked)
    normalised       = normalizer(validated)
    purpose_data     = purpose_info(normalised)
    assessed         = assessment(purpose_data)
    after_report     = report(assessed)
    after_linkage    = linkage_check(after_report)

    terminal_report(after_linkage)