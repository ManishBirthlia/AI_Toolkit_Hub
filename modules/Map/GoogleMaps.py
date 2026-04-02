from typing import Optional

try:
    import googlemaps
except ImportError as e:
    raise ImportError("pip install googlemaps") from e

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class GoogleMapsClient:
    """Google Maps provider for geocoding, directions, distance matrix, places, and elevation."""

    def __init__(self) -> None:
        self.client = googlemaps.Client(key=get_api_key("GOOGLE_API_KEY"))
        logger.info("GoogleMapsClient initialized.")

    def geocode(self, address: str) -> dict:
        """Convert a human-readable address to coordinates.

        Returns:
            Dict with 'lat', 'lng', 'formatted_address', 'place_id'.

        Raises:
            ValueError: If address is empty or no results found.
            RuntimeError: If the API call fails.
        """
        if not address or not address.strip():
            raise ValueError("Address cannot be empty.")
        try:
            results = self.client.geocode(address)
            if not results:
                raise ValueError(f"No geocoding results found for: '{address}'")
            top = results[0]
            loc = top["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"],
                    "formatted_address": top.get("formatted_address", ""),
                    "place_id": top.get("place_id", "")}
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Geocoding failed: {e}") from e

    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Convert coordinates to a human-readable address."""
        try:
            results = self.client.reverse_geocode((lat, lng))
            if not results:
                raise ValueError(f"No address found for ({lat}, {lng}).")
            top = results[0]
            return {"formatted_address": top.get("formatted_address", ""),
                    "place_id": top.get("place_id", ""),
                    "components": top.get("address_components", [])}
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Reverse geocoding failed: {e}") from e

    def get_directions(self, origin: str, destination: str, mode: str = "driving",
                       waypoints: Optional[list[str]] = None,
                       avoid: Optional[list[str]] = None) -> dict:
        """Get step-by-step directions between two locations.

        Args:
            origin: Starting address or 'lat,lng' string.
            destination: Ending address or 'lat,lng' string.
            mode: 'driving', 'walking', 'bicycling', or 'transit'.
            waypoints: Optional intermediate stop addresses.
            avoid: Optional features to avoid ('tolls', 'highways', 'ferries').

        Returns:
            Dict with 'distance', 'duration', 'distance_meters',
            'duration_seconds', 'steps', 'polyline'.

        Raises:
            ValueError: If origin/destination empty or mode invalid.
            RuntimeError: If the API call fails.
        """
        if not origin or not origin.strip():
            raise ValueError("origin cannot be empty.")
        if not destination or not destination.strip():
            raise ValueError("destination cannot be empty.")
        valid_modes = {"driving", "walking", "bicycling", "transit"}
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}.")
        try:
            kwargs = {"mode": mode}
            if waypoints:
                kwargs["waypoints"] = waypoints
            if avoid:
                kwargs["avoid"] = avoid
            results = self.client.directions(origin, destination, **kwargs)
            if not results:
                raise ValueError(f"No route found from '{origin}' to '{destination}'.")
            leg = results[0]["legs"][0]
            steps = [{"instruction": s["html_instructions"],
                      "distance": s["distance"]["text"]}
                     for s in leg.get("steps", [])]
            return {"distance": leg["distance"]["text"],
                    "duration": leg["duration"]["text"],
                    "distance_meters": leg["distance"]["value"],
                    "duration_seconds": leg["duration"]["value"],
                    "steps": steps,
                    "polyline": results[0]["overview_polyline"]["points"]}
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Directions request failed: {e}") from e

    def distance_matrix(self, origins: list[str], destinations: list[str],
                        mode: str = "driving") -> dict:
        """Compute travel distances and times between multiple origins and destinations."""
        if not origins:
            raise ValueError("origins list cannot be empty.")
        if not destinations:
            raise ValueError("destinations list cannot be empty.")
        try:
            result = self.client.distance_matrix(origins, destinations, mode=mode)
            return {"origin_addresses": result.get("origin_addresses", []),
                    "destination_addresses": result.get("destination_addresses", []),
                    "rows": result.get("rows", [])}
        except Exception as e:
            raise RuntimeError(f"Distance matrix request failed: {e}") from e

    def search_places(self, query: str, location: Optional[tuple] = None,
                      radius_meters: int = 5000,
                      place_type: Optional[str] = None) -> list[dict]:
        """Search for places by text query."""
        if not query or not query.strip():
            raise ValueError("query cannot be empty.")
        try:
            kwargs = {}
            if location:
                kwargs["location"] = location
                kwargs["radius"] = radius_meters
            if place_type:
                kwargs["type"] = place_type
            result = self.client.places(query=query, **kwargs)
            places = []
            for p in result.get("results", []):
                loc = p.get("geometry", {}).get("location", {})
                hours = p.get("opening_hours", {})
                places.append({"name": p.get("name", ""),
                                "address": p.get("formatted_address", p.get("vicinity", "")),
                                "place_id": p.get("place_id", ""),
                                "lat": loc.get("lat"), "lng": loc.get("lng"),
                                "rating": p.get("rating"),
                                "open_now": hours.get("open_now")})
            return places
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Places search failed: {e}") from e

    def get_elevation(self, locations: list[tuple]) -> list[dict]:
        """Get elevation data for one or more coordinates."""
        if not locations:
            raise ValueError("locations list cannot be empty.")
        try:
            results = self.client.elevation(locations)
            return [{"lat": r["location"]["lat"], "lng": r["location"]["lng"],
                     "elevation": r["elevation"]} for r in results]
        except Exception as e:
            raise RuntimeError(f"Elevation request failed: {e}") from e
