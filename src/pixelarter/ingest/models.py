from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_NORMALIZATION = "accepted_with_normalization"
    REJECTED = "rejected"

@dataclass
class PngInspectionResult:
    verdict: Verdict
    score: int  # 0 to 100
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggested_normalizations: list[str] = field(default_factory=list)
    applied_normalizations: list[str] = field(default_factory=list)

    source_width: int = 0
    source_height: int = 0
    logical_width: int = 0
    logical_height: int = 0

    unique_colors: int = 0
    effective_colors: int = 0  # e.g., after near-color merge if applied/estimated

    suspected_integer_scale: int | None = None
    alpha_mode_summary: str = "none"  # "none", "binary", "semi-transparent", "dirty"

    output_suitability_flags: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "score": self.score,
            "reasons": self.reasons,
            "warnings": self.warnings,
            "suggested_normalizations": self.suggested_normalizations,
            "applied_normalizations": self.applied_normalizations,
            "source_dimensions": {"width": self.source_width, "height": self.source_height},
            "logical_dimensions": {"width": self.logical_width, "height": self.logical_height},
            "colors": {
                "unique": self.unique_colors,
                "effective": self.effective_colors
            },
            "suspected_integer_scale": self.suspected_integer_scale,
            "alpha_mode_summary": self.alpha_mode_summary,
            "output_suitability_flags": self.output_suitability_flags,
            "metadata": self.metadata
        }
