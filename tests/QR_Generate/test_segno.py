import pytest
from unittest.mock import MagicMock, patch


class TestSegnoGenerator:

    def setup_method(self):
        from modules.QR_Generate.Segno import SegnoGenerator
        self.gen = SegnoGenerator()

    def test_raises_on_empty_data(self):
        with pytest.raises(ValueError):
            self.gen.generate("")

    def test_raises_on_invalid_format(self):
        with pytest.raises(ValueError, match="output_format must be one of"):
            self.gen.generate("data", output_format="bmp")

    def test_wifi_raises_on_empty_ssid(self):
        with pytest.raises(ValueError, match="SSID cannot be empty"):
            self.gen.generate_wifi(ssid="", password="pass")

    def test_vcard_raises_on_empty_name(self):
        with pytest.raises(ValueError, match="Contact name cannot be empty"):
            self.gen.generate_vcard(name="")

    def test_geo_raises_on_invalid_lat(self):
        with pytest.raises(ValueError, match="latitude must be between"):
            self.gen.generate_geo(latitude=91.0, longitude=77.0)

    def test_geo_raises_on_invalid_lng(self):
        with pytest.raises(ValueError, match="longitude must be between"):
            self.gen.generate_geo(latitude=28.0, longitude=200.0)

    def test_email_raises_on_empty_recipient(self):
        with pytest.raises(ValueError, match="Recipient email address cannot be empty"):
            self.gen.generate_email(to="")
