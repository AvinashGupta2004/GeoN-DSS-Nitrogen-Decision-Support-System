"""
Field Route — Analyzes user drawn GeoJSON polygon, calculates
field area (hectares), centroid coordinates, and mapped district.
"""
from fastapi import APIRouter
from app.schemas.request import GeoJSONPolygon
from app.services.gee_service import compute_polygon_metrics, resolve_nearest_district

router = APIRouter()


@router.post("/field/info")
def get_field_info(polygon: GeoJSONPolygon):
    geometry = polygon.geometry or {}
    coords = geometry.get("coordinates", [])

    # GeoJSON polygons coordinates are nested: [[[lon, lat], [lon, lat], ...]]
    flat_coords = coords[0] if coords and isinstance(coords[0], list) and isinstance(coords[0][0], list) else coords

    centroid_lat, centroid_lon, area_ha = compute_polygon_metrics(flat_coords)
    district = resolve_nearest_district(centroid_lat, centroid_lon)

    return {
        "centroid_lat": centroid_lat,
        "centroid_lon": centroid_lon,
        "field_area_ha": area_ha,
        "district": district,
        "state": "Uttar Pradesh"
    }
