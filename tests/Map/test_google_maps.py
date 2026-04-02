import pytest
from unittest.mock import MagicMock, patch


class TestGoogleMapsClient:

    @patch("modules.Map.GoogleMaps.googlemaps.Client")
    @patch("modules.Map.GoogleMaps.get_api_key", return_value="gm_test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.Map.GoogleMaps import GoogleMapsClient
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.maps = GoogleMapsClient()

    def test_geocode_returns_dict(self):
        self.mock_client.geocode.return_value = [{
            "geometry": {"location": {"lat": 28.6139, "lng": 77.2090}},
            "formatted_address": "New Delhi, India", "place_id": "ChIJ_test"}]
        result = self.maps.geocode("New Delhi")
        assert result["lat"] == 28.6139 and "New Delhi" in result["formatted_address"]

    def test_geocode_raises_on_empty(self):
        with pytest.raises(ValueError, match="Address cannot be empty"):
            self.maps.geocode("")

    def test_geocode_raises_no_results(self):
        self.mock_client.geocode.return_value = []
        with pytest.raises(ValueError, match="No geocoding results"):
            self.maps.geocode("xyznonexistent")

    def test_directions_raises_on_empty_origin(self):
        with pytest.raises(ValueError, match="origin cannot be empty"):
            self.maps.get_directions("", "Agra")

    def test_directions_raises_on_invalid_mode(self):
        with pytest.raises(ValueError, match="mode must be one of"):
            self.maps.get_directions("Delhi", "Agra", mode="flying")
