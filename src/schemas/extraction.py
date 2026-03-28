"""Pydantic models for raw data extracted from PDFs by Gemini."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

StrCoerce = Annotated[str, BeforeValidator(lambda v: str(v) if v is not None else "")]


class ExtractedPosition(BaseModel):
    """A single position row extracted from the PDF order table."""

    pos: str = Field(
        ...,
        description="Position code from the PDF table (e.g., EG1, DG4)",
    )
    breite: StrCoerce = Field(
        ...,
        description="Width value from the Breite column",
    )
    hoehe: StrCoerce = Field(
        ...,
        description="Height value from the Höhe column",
    )
    links: str = Field(
        default="",
        description="Left indicator — 'L' if present, empty otherwise",
    )
    rechts: str = Field(
        default="",
        description="Right indicator — 'R' if present, empty otherwise",
    )
    antrieb: str = Field(
        default="",
        description="Drive type for this position (e.g., Elektro)",
    )
    bemerkung: str = Field(
        default="",
        description="Remark text (e.g., Notkurbel, Rolladenkasten)",
    )
    stueck: StrCoerce = Field(
        ...,
        description="Quantity (Stück) for this position",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pos": "EG1",
                "breite": "1200",
                "hoehe": "1500",
                "links": "L",
                "rechts": "",
                "antrieb": "Elektro",
                "bemerkung": "Notkurbel",
                "stueck": "1",
            }
        }


class ExtractedHeader(BaseModel):
    """Header-level fields extracted from the PDF order."""

    lieferanschrift: str = Field(
        ...,
        description="Delivery address company name (Lieferanschrift)",
    )
    kommission: str = Field(
        ...,
        description="Commission reference — Kunststofffenster für BV value",
    )
    rollladennummer: str = Field(
        ...,
        description="Order number under the Roll heading",
    )
    liefertermin: str = Field(
        ...,
        description="Delivery date in DD.MM.YYYY format",
    )
    rollladen: str = Field(
        ...,
        description="Roller shutter material (e.g., Aluminium Silber)",
    )
    konstruktion: str = Field(
        ...,
        description="Construction type (e.g., Erhöht)",
    )
    konstruktion_nummer: str = Field(
        ...,
        description="Construction number (e.g., 2960er)",
    )
    aussenschuerze: str = Field(
        ...,
        description="Outer apron description (e.g., 140 mm Hartschaum)",
    )
    endleiste: str = Field(
        ...,
        description="End strip description with RAL code",
    )
    antrieb: str = Field(
        ...,
        description="Drive type from header (e.g., IO-homecontrol, SMI)",
    )
    gesamt: StrCoerce = Field(
        ...,
        description="Total quantity (Stück total / Gesamt)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "lieferanschrift": "Musterbau & Holztechnik GmbH",
                "kommission": "U2025-30770",
                "rollladennummer": "0702260411",
                "liefertermin": "15.05.2026",
                "rollladen": "Aluminium Silber",
                "konstruktion": "Erhöht",
                "konstruktion_nummer": "2960er",
                "aussenschuerze": "140 mm Hartschaum",
                "endleiste": "Aluminium-Abschlussleiste RAL 9006",
                "antrieb": "IO-homecontrol",
                "gesamt": "15",
            }
        }


class ExtractedData(BaseModel):
    """Complete extraction result from a single PDF."""

    header: ExtractedHeader = Field(
        ...,
        description="Header-level fields extracted from the PDF",
    )
    positions: list[ExtractedPosition] = Field(
        ...,
        description="List of position rows from the order table",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "header": {
                    "lieferanschrift": "Musterbau & Holztechnik GmbH",
                    "kommission": "U2025-30770",
                    "rollladennummer": "0702260411",
                    "liefertermin": "15.05.2026",
                    "rollladen": "Aluminium Silber",
                    "konstruktion": "Erhöht",
                    "konstruktion_nummer": "2960er",
                    "aussenschuerze": "140 mm Hartschaum",
                    "endleiste": "Aluminium-Abschlussleiste RAL 9006",
                    "antrieb": "IO-homecontrol",
                    "gesamt": "15",
                },
                "positions": [
                    {
                        "pos": "EG1",
                        "breite": "1200",
                        "hoehe": "1500",
                        "links": "L",
                        "rechts": "",
                        "antrieb": "Elektro",
                        "bemerkung": "Notkurbel",
                        "stueck": "1",
                    }
                ],
            }
        }
