from typing import List, Dict

# Standard DawnBringer 16 palette
DB16 = [
    "#140c1c", "#442434", "#30346d", "#4e4a4e",
    "#854c30", "#346524", "#d04648", "#757161",
    "#597dce", "#d27d2c", "#8595a1", "#6daa2c",
    "#d2aa99", "#6dc2ca", "#dad45e", "#deeed6",
]

# Standard DawnBringer 32 palette
DB32 = [
    "#000000", "#222034", "#45283c", "#663931",
    "#8f563b", "#df7126", "#d9a066", "#eec39a",
    "#fbf236", "#99e550", "#6abe30", "#37946e",
    "#4b692f", "#524b24", "#323c39", "#3f3f74",
    "#306082", "#5b6ee1", "#639bff", "#5fcde4",
    "#cbdbfc", "#ffffff", "#9badb7", "#847e87",
    "#696a6a", "#595652", "#76428a", "#ac3232",
    "#d95763", "#d77bba", "#8f974a", "#8a6f30",
]

_BUILTIN_PALETTES: Dict[str, List[str]] = {
    "pxa-16-v1": DB16,
    "pxa-32-v1": DB32,
}

def get_builtin_palette(palette_id: str) -> List[str]:
    """
    Retrieve a builtin palette by its ID.
    Raises ValueError if the palette_id is not found.
    """
    if palette_id not in _BUILTIN_PALETTES:
        raise ValueError(f"Unknown builtin palette ID: '{palette_id}'. Available: {list(_BUILTIN_PALETTES.keys())}")

    return list(_BUILTIN_PALETTES[palette_id])  # return a copy to prevent accidental mutation

def is_builtin_palette(palette_id: str) -> bool:
    """
    Check if a palette ID exists in the builtin registry.
    """
    return palette_id in _BUILTIN_PALETTES
