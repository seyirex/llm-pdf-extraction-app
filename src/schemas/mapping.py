"""Pydantic models for mapped output data."""

from pydantic import BaseModel, Field


class MappedHeader(BaseModel):
    """Header fields after applying mapping rules.

    Attributes:
        lieferanschrift: Delivery address company name.
        kommission: Commission reference.
        rollladennummer: Order number.
        liefertermin: Delivery date.
        rollladen: Mapped roller shutter type (SILBER/ANTHRAZIT/WEISS).
        konstruktion: Construction type.
        konstruktion_nummer: Construction number.
        aussenschuerze: Outer apron description.
        endleiste: Mapped end strip code (hwf9006/hwf7016/hwf9016).
        antrieb: Mapped drive type (SMI/IO).
        gesamt: Total quantity.
    """

    lieferanschrift: str = Field(
        ...,
        description="Delivery address company name",
    )
    kommission: str = Field(
        ...,
        description="Commission reference",
    )
    rollladennummer: str = Field(
        ...,
        description="Order number",
    )
    liefertermin: str = Field(
        ...,
        description="Delivery date",
    )
    rollladen: str = Field(
        ...,
        description="Mapped roller shutter type (SILBER, ANTHRAZIT, WEISS)",
    )
    konstruktion: str = Field(
        ...,
        description="Construction type",
    )
    konstruktion_nummer: str = Field(
        ...,
        description="Construction number",
    )
    aussenschuerze: str = Field(
        ...,
        description="Outer apron description",
    )
    endleiste: str = Field(
        ...,
        description="Mapped end strip code (hwf9006, hwf7016, hwf9016)",
    )
    antrieb: str = Field(
        ...,
        description="Mapped drive type (SMI, IO)",
    )
    gesamt: str = Field(
        ...,
        description="Total quantity",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "lieferanschrift": "Musterbau & Holztechnik GmbH",
                "kommission": "U2025-30770",
                "rollladennummer": "0702260411",
                "liefertermin": "15.05.2026",
                "rollladen": "SILBER",
                "konstruktion": "Erhöht",
                "konstruktion_nummer": "2960er",
                "aussenschuerze": "140 mm Hartschaum",
                "endleiste": "hwf9006",
                "antrieb": "IO",
                "gesamt": "15",
            }
        }


class MappedPosition(BaseModel):
    """A single position row after applying mapping rules.

    Attributes:
        line: Running line number starting at 1.
        stueck: Quantity.
        breite: Width.
        hoehe: Height.
        links: Mapped left indicator (1 or 0).
        rechts: Mapped right indicator (1 or 0).
        antrieb: Mapped drive value (0, 1, or 2).
        pos: Position code.
        bemerkung: Mapped remark (8, Rolladenkasten, or 0).
        bemerkung_nummer: Extracted dimension from remark (e.g., 180mm) or 0.
    """

    line: int = Field(
        ...,
        description="Running line number starting at 1",
    )
    stueck: str = Field(
        ...,
        description="Quantity for this position",
    )
    breite: str = Field(
        ...,
        description="Width value",
    )
    hoehe: str = Field(
        ...,
        description="Height value",
    )
    links: str = Field(
        ...,
        description="Mapped left indicator — '1' if L present, else '0'",
    )
    rechts: str = Field(
        ...,
        description="Mapped right indicator — '1' if R present, else '0'",
    )
    antrieb: str = Field(
        ...,
        description="Mapped drive — '1' (Elektro+IO), '2' (Elektro+SMI), '0'",
    )
    pos: str = Field(
        ...,
        description="Position code (e.g., EG1, DG4)",
    )
    bemerkung: str = Field(
        ...,
        description="Mapped remark — '8' (Notkurbel), 'Rolladenkasten', or '0'",
    )
    bemerkung_nummer: str = Field(
        ...,
        description="Dimension from remark (e.g., '180mm') or '0'",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "line": 1,
                "stueck": "1",
                "breite": "1200",
                "hoehe": "1500",
                "links": "1",
                "rechts": "0",
                "antrieb": "1",
                "pos": "EG1",
                "bemerkung": "8",
                "bemerkung_nummer": "180mm",
            }
        }


class MappedResult(BaseModel):
    """Complete mapping result for a PDF.

    Attributes:
        header: Mapped header fields.
        positions: List of mapped position rows.
    """

    header: MappedHeader = Field(
        ...,
        description="Mapped header fields",
    )
    positions: list[MappedPosition] = Field(
        ...,
        description="List of mapped position rows",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "header": {
                    "lieferanschrift": "Musterbau & Holztechnik GmbH",
                    "kommission": "U2025-30770",
                    "rollladennummer": "0702260411",
                    "liefertermin": "15.05.2026",
                    "rollladen": "SILBER",
                    "konstruktion": "Erhöht",
                    "konstruktion_nummer": "2960er",
                    "aussenschuerze": "140 mm Hartschaum",
                    "endleiste": "hwf9006",
                    "antrieb": "IO",
                    "gesamt": "15",
                },
                "positions": [
                    {
                        "line": 1,
                        "stueck": "1",
                        "breite": "1200",
                        "hoehe": "1500",
                        "links": "1",
                        "rechts": "0",
                        "antrieb": "1",
                        "pos": "EG1",
                        "bemerkung": "8",
                        "bemerkung_nummer": "180mm",
                    }
                ],
            }
        }
