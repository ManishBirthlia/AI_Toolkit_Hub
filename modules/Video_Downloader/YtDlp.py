from pathlib import Path
from typing import Optional, Literal

try:
    import yt_dlp
except ImportError as e:
    raise ImportError("pip install yt-dlp") from e

from utils.helpers import sanitize_filename
from utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_OUTPUT_DIR = "downloads"


class VideoDownloader:
    """Video downloader using yt-dlp. Supports 1000+ platforms."""

    def __init__(self, output_dir: str = _DEFAULT_OUTPUT_DIR) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VideoDownloader initialized | output_dir='{self.output_dir.resolve()}'")

    def _base_opts(self, extra: dict = None) -> dict:
        opts = {"outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
                "quiet": True, "no_warnings": True,
                "progress_hooks": [self._progress_hook]}
        if extra:
            opts.update(extra)
        return opts

    @staticmethod
    def _progress_hook(d: dict) -> None:
        if d.get("status") == "finished":
            logger.info(f"Download complete | file='{Path(d.get('filename', '')).name}'")

    def get_info(self, url: str) -> dict:
        """Extract metadata from a video URL without downloading.

        Args:
            url: Video URL from any supported platform.

        Returns:
            Dict with 'title', 'uploader', 'duration', 'view_count',
            'description', 'upload_date', 'thumbnail', 'formats'.

        Raises:
            ValueError: If url is empty.
            RuntimeError: If metadata extraction fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                return ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Failed to extract video info: {e}") from e

    def list_formats(self, url: str) -> list[dict]:
        """List all available download formats for a URL."""
        info = self.get_info(url)
        return [{"format_id": f.get("format_id", ""), "ext": f.get("ext", ""),
                 "resolution": f.get("resolution", "audio only"), "fps": f.get("fps"),
                 "filesize": f.get("filesize"), "vcodec": f.get("vcodec", "none"),
                 "acodec": f.get("acodec", "none"), "note": f.get("format_note", "")}
                for f in info.get("formats", [])]

    def download_video(self, url: str,
                       quality: Literal["best", "worst", "1080p", "720p", "480p", "360p"] = "best",
                       format_id: Optional[str] = None, filename: Optional[str] = None,
                       embed_subs: bool = False) -> str:
        """Download a video from a URL.

        Args:
            url: Video URL.
            quality: Quality preset (ignored if format_id is provided).
            format_id: Specific yt-dlp format ID (overrides quality preset).
            filename: Optional custom output filename (without extension).
            embed_subs: Embed available subtitles into the video.

        Returns:
            Absolute path to the downloaded file.

        Raises:
            ValueError: If url is empty.
            RuntimeError: If download fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        quality_map = {
            "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "worst": "worstvideo+worstaudio/worst",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio/best[height<=360]",
        }
        outtmpl = str(self.output_dir / (f"{sanitize_filename(filename)}.%(ext)s"
                                          if filename else "%(title)s.%(ext)s"))
        extra = {"format": format_id or quality_map.get(quality, quality_map["best"]),
                 "outtmpl": outtmpl, "merge_output_format": "mp4"}
        if embed_subs:
            extra.update({"writesubtitles": True, "subtitleslangs": ["en"],
                          "embedsubtitles": True})

        downloaded_path: list[str] = []

        def capture_hook(d):
            self._progress_hook(d)
            if d.get("status") == "finished":
                downloaded_path.append(d.get("filename", ""))

        opts = self._base_opts(extra)
        opts["progress_hooks"] = [capture_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return downloaded_path[-1] if downloaded_path else ""
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Video download failed: {e}") from e

    def download_audio(self, url: str,
                       audio_format: Literal["mp3", "m4a", "wav", "flac", "ogg"] = "mp3",
                       audio_quality: str = "192",
                       filename: Optional[str] = None) -> str:
        """Extract and download only the audio from a video URL.

        Args:
            url: Video URL.
            audio_format: Output audio format.
            audio_quality: Audio bitrate in kbps. Defaults to '192'.
            filename: Optional custom output filename.

        Returns:
            Absolute path to the downloaded audio file.

        Raises:
            ValueError: If url is empty.
            RuntimeError: If download fails.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        outtmpl = str(self.output_dir / (f"{sanitize_filename(filename)}.%(ext)s"
                                          if filename else "%(title)s.%(ext)s"))
        extra = {"format": "bestaudio/best", "outtmpl": outtmpl,
                 "postprocessors": [{"key": "FFmpegExtractAudio",
                                     "preferredcodec": audio_format,
                                     "preferredquality": audio_quality}]}
        downloaded_path: list[str] = []

        def capture_hook(d):
            self._progress_hook(d)
            if d.get("status") == "finished":
                downloaded_path.append(d.get("filename", ""))

        opts = self._base_opts(extra)
        opts["progress_hooks"] = [capture_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            path = str(Path(downloaded_path[-1]).with_suffix(f".{audio_format}")) \
                if downloaded_path else ""
            return path
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Audio download failed: {e}") from e

    def download_playlist(self, url: str, quality: str = "best",
                          audio_only: bool = False,
                          max_downloads: Optional[int] = None,
                          start_index: int = 1,
                          end_index: Optional[int] = None) -> list[str]:
        """Download all or a range of videos from a playlist."""
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        extra: dict = {"playliststart": start_index, "ignoreerrors": True}
        if end_index:
            extra["playlistend"] = end_index
        if max_downloads:
            extra["max_downloads"] = max_downloads
        if audio_only:
            extra["format"] = "bestaudio/best"
            extra["postprocessors"] = [{"key": "FFmpegExtractAudio",
                                         "preferredcodec": "mp3",
                                         "preferredquality": "192"}]
        else:
            extra["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            extra["merge_output_format"] = "mp4"

        downloaded_paths: list[str] = []

        def capture_hook(d):
            self._progress_hook(d)
            if d.get("status") == "finished":
                downloaded_paths.append(d.get("filename", ""))

        opts = self._base_opts(extra)
        opts["progress_hooks"] = [capture_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return downloaded_paths
        except yt_dlp.utils.MaxDownloadsReached:
            return downloaded_paths
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Playlist download failed: {e}") from e

    def download_subtitles(self, url: str, languages: Optional[list[str]] = None,
                           subtitle_format: str = "srt") -> list[str]:
        """Download subtitles for a video without downloading the video itself."""
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        extra = {"writesubtitles": True, "writeautomaticsub": True,
                 "subtitlesformat": subtitle_format, "skip_download": True}
        if languages:
            extra["subtitleslangs"] = languages

        downloaded_paths: list[str] = []

        def capture_hook(d):
            if d.get("status") == "finished":
                downloaded_paths.append(d.get("filename", ""))

        opts = self._base_opts(extra)
        opts["progress_hooks"] = [capture_hook]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return downloaded_paths
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Subtitle download failed: {e}") from e
