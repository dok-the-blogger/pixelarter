# PixelArt Image Format (.pixelart) v1-alpha

The `.pixelart` format is the canonical representation of pixel art within the `pixelarter` project.

## Logical Representation
Unlike common raster formats (such as PNG or JPEG), a `.pixelart` file stores **logical pixel data**, not physical display pixels.
The format operates on the principle that the core essence of pixel art is a matrix of indices mapped to a specific palette.

The canonical entity consists of:
- `palette` (colors)
- `indices` (2D grid of palette indices)
- `metadata`

Display factors like scaling, filtering, or physical screen dimensions are intentionally omitted from the core data structure. They are considered rendering concerns.

## JSON Implementation
In its current `v1-alpha` version, the format is implemented as a simple JSON file. This allows for easy inspection, debugging, and parsing without requiring complex binary decoders. While PNG is supported for importing and exporting, it is not the canonical form inside the `pixelarter` pipeline.

Future versions of this format may implement more efficient encodings (such as binary packing or RLE), but `v1-alpha` prioritizes simplicity.

## Palette Modes
The format supports two palette modes:

### Builtin Palette (`"builtin"`)
In this mode, the image uses a palette that is predefined and known to the `pixelarter` project. The JSON file will store a `palette_id` string (e.g., `"pxa-16-v1"`), rather than the raw color data. This ensures consistency and enforces standard palettes across multiple assets.

### Embedded Palette (`"embedded"`)
In this mode, the exact colors used by the image are stored directly within the JSON file under the `palette` field as an array of hex color strings (e.g., `["#000000", "#FFFFFF"]`). This allows for custom pixel art that does not conform to a builtin palette.

## Structure
A valid `.pixelart` JSON file must contain the following fields:

```json
{
  "format": "pixelart",
  "version": 1,
  "width": 16,
  "height": 16,
  "palette_mode": "builtin",
  "palette_id": "pxa-16-v1",
  "transparent_index": null,
  "encoding": "rows",
  "rows": [
    [0, 0, 1, 1, ...],
    ...
  ],
  "metadata": {}
}
```

### Fields:
- `format`: Must be exactly `"pixelart"`.
- `version`: Format version integer. Currently `1`.
- `width`, `height`: Logical dimensions of the image.
- `palette_mode`: `"builtin"` or `"embedded"`.
- `palette_id`: The ID of the builtin palette (required if mode is `"builtin"`).
- `palette`: Array of hex color strings (required if mode is `"embedded"`).
- `transparent_index`: Integer representing the palette index used for transparency, or `null`.
- `encoding`: Method used to store the indices. Currently `"rows"`.
- `rows`: A list of integer lists, where each sublist represents a horizontal row of logical palette indices.
- `metadata`: Key-value store for arbitrary data (e.g., source info, tags).
