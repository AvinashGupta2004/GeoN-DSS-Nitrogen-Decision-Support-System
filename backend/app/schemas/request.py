"""
Pydantic request schemas for the prediction endpoint.
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class CropType(str, Enum):
    WHEAT = "WHEAT"; RICE = "RICE"; MAIZE = "MAIZE"; BAJRA = "BAJRA"
    SUGARCANE = "SUGARCANE"; POTATO = "POTATO"; ONION = "ONION"
    MUSTARD = "MUSTARD"; WATERMELON = "WATERMELON"; FODDER_MAIZE = "FODDER_MAIZE"
    ARHAR = "ARHAR"; SOYBEAN = "SOYBEAN"; CHICKPEA = "CHICKPEA"
    LENTIL = "LENTIL"; MOONG = "MOONG"


class CropSeason(str, Enum):
    KHARIF = "KHARIF"; RABI = "RABI"; ZAID = "ZAID"


class GrowthStage(str, Enum):
    GERMINATION = "GERMINATION"; VEGETATIVE = "VEGETATIVE"
    TILLERING = "TILLERING"; BOOTING = "BOOTING"
    FLOWERING = "FLOWERING"; GRAIN_FILL = "GRAIN_FILL"; MATURITY = "MATURITY"


class IrrigationType(str, Enum):
    FLOOD = "FLOOD"; SPRINKLER = "SPRINKLER"; DRIP = "DRIP"; RAINFED = "RAINFED"


class PreviousCrop(str, Enum):
    WHEAT = "WHEAT"; RICE = "RICE"; MAIZE = "MAIZE"; BAJRA = "BAJRA"
    SUGARCANE = "SUGARCANE"; POTATO = "POTATO"; MUSTARD = "MUSTARD"
    ARHAR = "ARHAR"; SOYBEAN = "SOYBEAN"; CHICKPEA = "CHICKPEA"
    LENTIL = "LENTIL"; MOONG = "MOONG"
    LEGUME_GENERIC = "LEGUME_GENERIC"; FALLOW = "FALLOW"


class GeoJSONPolygon(BaseModel):
    """GeoJSON polygon boundary drawn by user on the map."""
    type: str = "Feature"
    geometry: dict  # GeoJSON geometry object with coordinates


class PredictRequest(BaseModel):
    """Full request payload for nitrogen recommendation."""
    field_polygon: GeoJSONPolygon = Field(..., description="GeoJSON polygon of the field")
    crop_type: CropType
    crop_season: CropSeason
    growth_stage: GrowthStage
    days_after_sowing: int = Field(..., ge=0, le=365)
    previous_crop: PreviousCrop
    irrigation_type: IrrigationType
    target_yield_tha: float = Field(..., gt=0, description="Target yield in tonnes/ha")

    class Config:
        json_schema_extra = {
            "example": {
                "crop_type": "WHEAT",
                "crop_season": "RABI",
                "growth_stage": "TILLERING",
                "days_after_sowing": 35,
                "previous_crop": "RICE",
                "irrigation_type": "FLOOD",
                "target_yield_tha": 4.5
            }
        }
