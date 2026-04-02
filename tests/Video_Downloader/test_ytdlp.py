import pytest
from unittest.mock import MagicMock, patch


class TestVideoDownloader:

    def setup_method(self):
        from modules.Video_Downloader.YtDlp import VideoDownloader
        self.downloader = VideoDownloader(output_dir="/tmp/test_dl")

    def test_raises_on_empty_url_get_info(self):
        with pytest.raises(ValueError, match="URL cannot be empty"):
            self.downloader.get_info("")

    def test_raises_on_empty_url_download_video(self):
        with pytest.raises(ValueError):
            self.downloader.download_video("")

    def test_raises_on_empty_url_download_audio(self):
        with pytest.raises(ValueError):
            self.downloader.download_audio("")

    @patch("modules.Video_Downloader.YtDlp.yt_dlp.YoutubeDL")
    def test_get_info_returns_dict(self, mock_ydl_cls):
        mock_ydl = MagicMock()
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            "title": "Test Video", "duration": 120, "formats": []}
        result = self.downloader.get_info("https://youtube.com/watch?v=test")
        assert result["title"] == "Test Video"

    @patch("modules.Video_Downloader.YtDlp.yt_dlp.YoutubeDL")
    def test_raises_on_download_error(self, mock_ydl_cls):
        import yt_dlp
        mock_ydl = MagicMock()
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Not found")
        with pytest.raises(RuntimeError, match="Failed to extract video info"):
            self.downloader.get_info("https://youtube.com/watch?v=invalid")
