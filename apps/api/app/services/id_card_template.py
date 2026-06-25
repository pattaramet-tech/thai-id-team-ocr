"""Thai ID Card Template Manager for Structured Extraction.

Manages ROI presets and field configurations for Thai ID card OCR extraction.
Inspired by AksonOCR but local-only using OpenCV + Tesseract.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TemplateVersion(str, Enum):
    """Available template versions for different image types."""
    V1 = "template_v1"  # Perfect color/front-facing card
    V2 = "template_v2"  # B&W copy / close-up
    V3 = "template_v3"  # Cropped / unclear edges


@dataclass
class ROIDefinition:
    """Region of Interest definition for a field."""
    x: int
    y: int
    width: int
    height: int

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


@dataclass
class FieldConfig:
    """Configuration for extracting a single field."""
    fieldName: str
    label: str
    language: str  # tha+eng or eng
    psm: int  # Tesseract PSM mode
    parser: str  # Parser method name
    expectedPattern: Optional[str] = None  # Regex for validation
    weight: float = 1.0  # Importance weight for scoring
    requiredForSave: bool = True  # Must be present to save
    rois: Dict[TemplateVersion, ROIDefinition] = field(default_factory=dict)


@dataclass
class ThaiIDCardTemplate:
    """Thai ID Card template with ROI definitions."""
    templateName: str = "thai_id_card_v1"
    standardWidth: int = 1000
    standardHeight: int = 630

    # Field configurations
    thai_full_name: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="thai_full_name",
        label="ชื่อตัวและชื่อสกุล",
        language="tha+eng",
        psm=6,
        parser="parse_thai_full_name_from_roi",
        expectedPattern=None,
        weight=1.0,
        requiredForSave=True
    ))

    english_first_name: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="english_first_name",
        label="Name",
        language="eng",
        psm=7,
        parser="parse_english_name_from_roi",
        expectedPattern=None,
        weight=0.8,
        requiredForSave=False
    ))

    english_last_name: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="english_last_name",
        label="Last name",
        language="eng",
        psm=7,
        parser="parse_english_name_from_roi",
        expectedPattern=None,
        weight=0.8,
        requiredForSave=False
    ))

    dob_thai: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="dob_thai",
        label="เกิดวันที่",
        language="tha+eng",
        psm=7,
        parser="extract_date_of_birth",
        expectedPattern=r"\d{1,2}\s+[ก-ฮ\.]+\s+\d{4}",
        weight=1.0,
        requiredForSave=True
    ))

    dob_english: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="dob_english",
        label="Date of Birth",
        language="eng",
        psm=7,
        parser="extract_date_of_birth",
        expectedPattern=r"\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
        weight=1.0,
        requiredForSave=True
    ))

    expiry_thai: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="expiry_thai",
        label="สิ้นสุด",
        language="tha+eng",
        psm=7,
        parser="extract_date_of_birth",
        expectedPattern=None,
        weight=0.5,
        requiredForSave=False
    ))

    expiry_english: FieldConfig = field(default_factory=lambda: FieldConfig(
        fieldName="expiry_english",
        label="Expiry",
        language="eng",
        psm=7,
        parser="extract_date_of_birth",
        expectedPattern=None,
        weight=0.5,
        requiredForSave=False
    ))


# Template V1: Perfect color/front-facing card
TEMPLATE_V1_ROIS = {
    "thai_full_name": ROIDefinition(x=250, y=205, width=520, height=75),
    "english_first_name": ROIDefinition(x=360, y=265, width=360, height=55),
    "english_last_name": ROIDefinition(x=360, y=320, width=360, height=55),
    "dob_thai": ROIDefinition(x=350, y=370, width=360, height=55),
    "dob_english": ROIDefinition(x=385, y=420, width=360, height=55),
    "expiry_thai": ROIDefinition(x=620, y=485, width=330, height=50),
    "expiry_english": ROIDefinition(x=620, y=535, width=330, height=50),
}

# Template V2: B&W copy / close-up
TEMPLATE_V2_ROIS = {
    "thai_full_name": ROIDefinition(x=190, y=180, width=650, height=95),
    "english_first_name": ROIDefinition(x=310, y=250, width=430, height=70),
    "english_last_name": ROIDefinition(x=310, y=310, width=430, height=70),
    "dob_thai": ROIDefinition(x=300, y=365, width=430, height=65),
    "dob_english": ROIDefinition(x=330, y=420, width=440, height=65),
    "expiry_thai": ROIDefinition(x=600, y=490, width=350, height=60),
    "expiry_english": ROIDefinition(x=600, y=545, width=350, height=60),
}

# Template V3: Cropped / unclear edges
TEMPLATE_V3_ROIS = {
    "thai_full_name": ROIDefinition(x=220, y=190, width=580, height=85),
    "english_first_name": ROIDefinition(x=330, y=260, width=400, height=65),
    "english_last_name": ROIDefinition(x=330, y=315, width=400, height=65),
    "dob_thai": ROIDefinition(x=320, y=370, width=400, height=60),
    "dob_english": ROIDefinition(x=350, y=425, width=420, height=60),
    "expiry_thai": ROIDefinition(x=610, y=490, width=340, height=55),
    "expiry_english": ROIDefinition(x=610, y=540, width=340, height=55),
}


class ThaiIDCardTemplateManager:
    """Manager for Thai ID Card templates."""

    def __init__(self):
        self.template = ThaiIDCardTemplate()
        self._setup_rois()

    def _setup_rois(self):
        """Set up ROI definitions for all templates."""
        fields_map = {
            "thai_full_name": self.template.thai_full_name,
            "english_first_name": self.template.english_first_name,
            "english_last_name": self.template.english_last_name,
            "dob_thai": self.template.dob_thai,
            "dob_english": self.template.dob_english,
            "expiry_thai": self.template.expiry_thai,
            "expiry_english": self.template.expiry_english,
        }

        roi_presets = {
            TemplateVersion.V1: TEMPLATE_V1_ROIS,
            TemplateVersion.V2: TEMPLATE_V2_ROIS,
            TemplateVersion.V3: TEMPLATE_V3_ROIS,
        }

        for field_name, field_config in fields_map.items():
            for version, rois in roi_presets.items():
                if field_name in rois:
                    field_config.rois[version] = rois[field_name]

    def get_field_config(self, field_name: str) -> Optional[FieldConfig]:
        """Get configuration for a field."""
        fields_map = {
            "thai_full_name": self.template.thai_full_name,
            "english_first_name": self.template.english_first_name,
            "english_last_name": self.template.english_last_name,
            "dob_thai": self.template.dob_thai,
            "dob_english": self.template.dob_english,
            "expiry_thai": self.template.expiry_thai,
            "expiry_english": self.template.expiry_english,
        }
        return fields_map.get(field_name)

    def get_roi(self, field_name: str, version: TemplateVersion) -> Optional[ROIDefinition]:
        """Get ROI for a field in a specific template version."""
        field_config = self.get_field_config(field_name)
        if field_config and version in field_config.rois:
            return field_config.rois[version]
        return None

    def get_all_field_names(self) -> List[str]:
        """Get all field names."""
        return [
            "thai_full_name", "english_first_name", "english_last_name",
            "dob_thai", "dob_english", "expiry_thai", "expiry_english"
        ]

    def update_roi(self, field_name: str, version: TemplateVersion, roi: ROIDefinition):
        """Update ROI for a field (useful for fine-tuning)."""
        field_config = self.get_field_config(field_name)
        if field_config:
            field_config.rois[version] = roi


# Global template manager instance
thai_id_template_manager = ThaiIDCardTemplateManager()
