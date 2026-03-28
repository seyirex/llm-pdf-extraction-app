"""Centralized LLM prompts used across the application."""

EXTRACTION_PROMPT = """You are a data extraction specialist. Extract ALL data from this German roller shutter order PDF into structured JSON.

Return a JSON object with exactly this structure:
{
  "header": {
    "lieferanschrift": "Delivery address from the Lieferanschrift field (company name, site address, or both)",
    "kommission": "Project/job reference number from the Kommission field (e.g., U2025-30770)",
    "rollladennummer": "Roller shutter order number from the Rollladennummer field (e.g., 0702260411)",
    "liefertermin": "Delivery date from the Liefertermin field in DD.MM.YYYY format",
    "rollladen": "Roller shutter material and color description (e.g., Aluminium Silber)",
    "konstruktion": "Construction type from the Konstruktion field (e.g., Erhöht)",
    "konstruktion_nummer": "Construction series number from the Konstruktion field (e.g., 2960er)",
    "aussenschuerze": "Outer apron (Außenschürze) specification (e.g., 140 mm Hartschaum)",
    "endleiste": "Bottom rail (Endleiste) description including RAL color code",
    "antrieb": "Drive/motor type from the header (e.g., IO-homecontrol, SMI)",
    "gesamt": "Total quantity (Gesamt) — sum of all Stück values"
  },
  "positions": [
    {
      "pos": "Window position code — EG = ground floor, OG = upper floor, DG = attic, followed by a number (e.g., EG1, OG3, DG4)",
      "breite": "Shutter width in mm from the Breite column",
      "hoehe": "Shutter height in mm from the Höhe column",
      "links": "L if the left guide rail column is marked, otherwise empty string",
      "rechts": "R if the right guide rail column is marked, otherwise empty string",
      "antrieb": "Drive/motor type for this position (e.g., Elektro)",
      "bemerkung": "Remarks/notes for this position — may include Notkurbel (emergency crank), Rolladenkasten, or mm dimensions",
      "stueck": "Quantity of shutters for this position from the Stück column"
    }
  ]
}

IMPORTANT RULES:
- Extract EVERY position row from the table, do not skip any
- Preserve exact German text — do not translate
- For L and R columns: use "L" or "R" if marked, empty string "" if not
- The Gesamt (total) should equal the sum of all Stück values
- Return ONLY the JSON, no explanations
"""