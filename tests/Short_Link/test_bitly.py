import pytest
from unittest.mock import MagicMock, patch


class TestBitlyShortener:

    @patch("modules.Short_Link.Bitly.get_api_key", return_value="bitly_test")
    def setup_method(self, method, mock_key):
        from modules.Short_Link.Bitly import BitlyShortener
        self.shortener = BitlyShortener()
        self.shortener._group_guid = "Bg_testguid"

    @patch("modules.Short_Link.Bitly.requests.post")
    def test_shorten_returns_dict(self, mock_post):
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {
            "link": "https://bit.ly/3test", "long_url": "https://example.com",
            "id": "bit.ly/3test", "created_at": "2024-01-01"}
        result = self.shortener.shorten("https://example.com")
        assert result["short_url"] == "https://bit.ly/3test"

    def test_shorten_raises_on_empty_url(self):
        with pytest.raises(ValueError, match="URL cannot be empty"):
            self.shortener.shorten("")

    def test_shorten_raises_on_invalid_url(self):
        with pytest.raises(ValueError, match="Invalid URL"):
            self.shortener.shorten("not-a-url")

    @patch("modules.Short_Link.Bitly.requests.get")
    def test_expand_returns_url(self, mock_get):
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = {"long_url": "https://example.com"}
        assert self.shortener.expand("https://bit.ly/3test") == "https://example.com"

    @patch("modules.Short_Link.Bitly.requests.get")
    def test_get_clicks_returns_dict(self, mock_get):
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = {
            "link_clicks": [{"date": "2024-01-01", "clicks": 120},
                            {"date": "2024-01-02", "clicks": 85}]}
        result = self.shortener.get_clicks("https://bit.ly/3test")
        assert result["total_clicks"] == 205

    def test_get_clicks_raises_on_invalid_unit(self):
        with pytest.raises(ValueError, match="unit must be one of"):
            self.shortener.get_clicks("https://bit.ly/3test", unit="year")
