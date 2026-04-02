import math
from typing import Optional
import requests

from utils.logger import get_logger

logger = get_logger(__name__)

_NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
_OSRM_BASE = "https://router.project-osrm.org"
_OVERPASS_BASE = "https://overpass-api.de/api/interpreter"
_DEFAULT_USER_AGENT = "AIUtilityToolkit/1.0"


class OpenStreetMapClient:
    """OpenStreetMap provider — fully free, no API key required."""

    def __init__(self, user_agent: str = _DEFAULT_USER_AGENT) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Language": "en"})
        logger.info(f"OpenStreetMapClient initialized | user_agent='{user_agent}'")

    def geocode(self, address: str, limit: int = 1,
                country_codes: Optional[list[str]] = None) -> list[dict]:
        """Convert an address to coordinates via Nominatim.

        Args:
            address: Address or place name to geocode.
            limit: Maximum number of results.
            country_codes: Optional ISO 3166-1 alpha-2 codes to restrict results.

        Returns:
            List of dicts with 'lat', 'lng', 'display_name', 'type', 'osm_id'.

        Raises:
            ValueError: If address is empty or no results found.
            RuntimeError: If the request fails.
        """
        if not address or not address.strip():
            raise ValueError("Address cannot be empty.")
        params = {"q": address, "format": "json", "limit": limit, "addressdetails": 1}
        if country_codes:
            params["countrycodes"] = ",".join(country_codes)
        try:
            resp = self.session.get(f"{_NOMINATIM_BASE}/search",
                                    params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                raise ValueError(f"No geocoding results found for: '{address}'")
            return [{"lat": float(r["lat"]), "lng": float(r["lon"]),
                     "display_name": r.get("display_name", ""),
                     "type": r.get("type", ""), "osm_id": r.get("osm_id", "")}
                    for r in data]
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"OSM geocoding failed: {e}") from e

    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Convert coordinates to a human-readable address via Nominatim."""
        params = {"lat": lat, "lon": lng, "format": "json", "addressdetails": 1}
        try:
            resp = self.session.get(f"{_NOMINATIM_BASE}/reverse", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise ValueError(f"No address found for ({lat}, {lng}): {data['error']}")
            return {"display_name": data.get("display_name", ""),
                    "address": data.get("address", {}), "osm_id": data.get("osm_id", "")}
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"OSM reverse geocoding failed: {e}") from e

    def get_directions(self, origin_lat: float, origin_lng: float,
                       dest_lat: float, dest_lng: float,
                       mode: str = "driving") -> dict:
        """Get route information between two coordinates via OSRM.

        Args:
            origin_lat: Origin latitude.
            origin_lng: Origin longitude.
            dest_lat: Destination latitude.
            dest_lng: Destination longitude.
            mode: 'driving', 'walking', or 'cycling'.

        Returns:
            Dict with 'distance_meters', 'distance_km', 'duration_seconds',
            'duration_text', 'geometry', 'steps'.

        Raises:
            ValueError: If mode is invalid or no route found.
            RuntimeError: If the request fails.
        """
        valid_modes = {"driving", "walking", "cycling"}
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}.")

        profile_map = {"driving": "car", "walking": "foot", "cycling": "bike"}
        coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        url = f"{_OSRM_BASE}/route/v1/{profile_map[mode]}/{coords}"

        try:
            resp = self.session.get(url, params={"overview": "full",
                                                  "geometries": "polyline",
                                                  "steps": "true"}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM returned no route: {data.get('message')}")
            route = data["routes"][0]
            leg = route["legs"][0]
            distance_m = route["distance"]
            duration_s = route["duration"]
            hours = int(duration_s // 3600)
            minutes = int((duration_s % 3600) // 60)
            duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes} mins"
            steps = [{"instruction": s.get("maneuver", {}).get("type", ""),
                      "distance_m": s.get("distance", 0)}
                     for s in leg.get("steps", [])]
            return {"distance_meters": distance_m,
                    "distance_km": f"{distance_m / 1000:.1f} km",
                    "duration_seconds": duration_s, "duration_text": duration_text,
                    "geometry": route.get("geometry", ""), "steps": steps}
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"OSM directions request failed: {e}") from e

    def calculate_distance(self, lat1: float, lng1: float,
                           lat2: float, lng2: float) -> float:
        """Calculate straight-line (Haversine) distance in kilometers. No API call."""
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 3)

    def search_nearby(self, lat: float, lng: float, amenity: str,
                      radius_meters: int = 1000, limit: int = 10) -> list[dict]:
        """Search for nearby amenities using the Overpass API.

        Args:
            lat: Center latitude.
            lng: Center longitude.
            amenity: OSM amenity type (e.g. 'restaurant', 'hospital', 'atm').
            radius_meters: Search radius in meters.
            limit: Maximum results to return.

        Returns:
            List of place dicts with 'name', 'lat', 'lng', 'osm_id', 'tags'.

        Raises:
            ValueError: If amenity is empty.
            RuntimeError: If the Overpass request fails.
        """
        if not amenity or not amenity.strip():
            raise ValueError("amenity cannot be empty.")
        query = (f"[out:json][timeout:10];"
                 f"node[amenity={amenity}](around:{radius_meters},{lat},{lng});"
                 f"out {limit};")
        try:
            resp = self.session.post(_OVERPASS_BASE, data={"data": query}, timeout=15)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            return [{"osm_id": el.get("id"), "lat": el.get("lat"),
                     "lng": el.get("lon"),
                     "name": el.get("tags", {}).get("name", "Unnamed"),
                     "tags": el.get("tags", {})}
                    for el in elements if el.get("lat") and el.get("lon")]
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"OSM nearby search failed: {e}") from e
