"""
Visual lineup card that looks like a hockey rink
"""

def format_lineup_card(lineup_data: dict) -> str:
    """
    Formats a lineup into a visual hockey rink layout.
    Args:
        lineup_data: Dictionary with goalie, line_1, line_2, etc.
    """
    goalie = lineup_data.get("goalie", "No goalie")
    line_1 = lineup_data.get("line_1", {})
    line_2 = lineup_data.get("line_2", {})

    # Get player names
    l1_forwards = line_1.get("forwards", [])
    l1_defense = line_1.get("defense", [])
    l2_forwards = line_2.get("forwards", [])
    l2_defense = line_2.get("defense", [])

    # Helper to format full names
    def format_name(name):
        return name if name else "---"

    # Build the visual rink
    card = f"""
```
═══════════════════════════════════════════════════════════
                      🏒 LINEUP CARD 🏒
═══════════════════════════════════════════════════════════

                         LINE 1

                    [{format_name(goalie):^15}]
                           🥅

          [{format_name(l1_defense[0] if len(l1_defense) > 0 else ''):^15}]    [{format_name(l1_defense[1] if len(l1_defense) > 1 else ''):^15}]
                      🛡️                  🛡️

  [{format_name(l1_forwards[0] if len(l1_forwards) > 0 else ''):^15}] [{format_name(l1_forwards[1] if len(l1_forwards) > 1 else ''):^15}] [{format_name(l1_forwards[2] if len(l1_forwards) > 2 else ''):^15}]
           ⚡️                 ⚡️                 ⚡️

───────────────────────────────────────────────────────────

                         LINE 2

          [{format_name(l2_defense[0] if len(l2_defense) > 0 else ''):^15}]    [{format_name(l2_defense[1] if len(l2_defense) > 1 else ''):^15}]
                      🛡️                  🛡️

  [{format_name(l2_forwards[0] if len(l2_forwards) > 0 else ''):^15}] [{format_name(l2_forwards[1] if len(l2_forwards) > 1 else ''):^15}] [{format_name(l2_forwards[2] if len(l2_forwards) > 2 else ''):^15}]
           ⚡️                 ⚡️                 ⚡️

═══════════════════════════════════════════════════════════
```
"""
    return card
