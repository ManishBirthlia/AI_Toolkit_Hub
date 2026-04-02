import pytest
from unittest.mock import MagicMock, patch


class TestOpenStreetMapClient:

    def setup_method(self):
        from modules.Map.OpenStreetMap import OpenStreetMapClient
        self.osm = OpenStreetMapClient()

    def test_geocode_raises_on_empty(self):
        with pytest.raises(ValueError, match="Address cannot be empty"):
            self.osm.geocode("")

    def test_calculate_distance_returns_float(self):
        dist = self.osm.calculate_distance(28.6139, 77.2090, 27.1767, 78.0081)
        assert isinstance(dist, float) and 180 < dist < 250

    def test_calculate_distance_same_point_is_zero(self):
        assert self.osm.calculate_distance(28.6, 77.2, 28.6, 77.2) == 0.0

    def test_search_nearby_raises_on_empty_amenity(self):
        with pytest.raises(ValueError, match="amenity cannot be empty"):
            self.osm.search_nearby(28.6, 77.2, amenity="")
