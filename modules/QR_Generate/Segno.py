import io
from typing import Optional, Literal

try:
    import segno
    from segno import helpers as segno_helpers
except ImportError as e:
    raise ImportError("pip install segno") from e

from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)


class SegnoGenerator:
    """Advanced QR/Micro QR generator. Supports PNG, SVG, PDF, EPS, WiFi, vCard, Geo, Email."""

    def __init__(self, error_correction: Literal["L", "M", "Q", "H"] = "H",
                 micro: bool = False) -> None:
        self.error_correction = error_correction.lower()
        self.micro = micro
        logger.info(f"SegnoGenerator initialized | ec={error_correction} | micro={micro}")

    def _make_qr(self, data: str) -> segno.QRCode:
        try:
            return segno.make(data, error=self.error_correction,
                              micro=self.micro if self.micro else None)
        except Exception as e:
            raise RuntimeError(f"QR code creation failed: {e}") from e

    def generate(self, data: str,
                 output_format: Literal["png", "svg", "eps", "pdf"] = "png",
                 scale: int = 10, dark: str = "black", light: str = "white",
                 output_path: Optional[str] = None) -> bytes:
        """Generate a QR code in PNG, SVG, EPS, or PDF format.

        Args:
            data: Data to encode.
            output_format: Output file format.
            scale: Scale factor (pixels per module for raster).
            dark: Foreground color.
            light: Background color. Use 'transparent' for transparent background.
            output_path: If provided, saves output to this path.

        Returns:
            Raw bytes of the generated QR code.

        Raises:
            ValueError: If data is empty or format is invalid.
            RuntimeError: If generation fails.
        """
        if not data or not data.strip():
            raise ValueError("data cannot be empty.")
        valid_formats = {"png", "svg", "eps", "pdf"}
        if output_format not in valid_formats:
            raise ValueError(f"output_format must be one of {valid_formats}.")
        try:
            qr = self._make_qr(data)
            buffer = io.BytesIO()
            save_kwargs = {"kind": output_format, "scale": scale, "dark": dark,
                           "light": None if light == "transparent" else light}
            qr.save(buffer, **save_kwargs)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Segno QR generation failed: {e}") from e

    def generate_wifi(self, ssid: str, password: str,
                      security: Literal["WPA", "WEP", "nopass"] = "WPA",
                      hidden: bool = False, output_format: str = "png",
                      scale: int = 10, output_path: Optional[str] = None) -> bytes:
        """Generate a WiFi QR code that phones can scan to join a network."""
        if not ssid or not ssid.strip():
            raise ValueError("SSID cannot be empty.")
        try:
            qr = segno_helpers.make_wifi(ssid=ssid, password=password,
                                         security=security, hidden=hidden)
            buffer = io.BytesIO()
            qr.save(buffer, kind=output_format, scale=scale)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"WiFi QR generation failed: {e}") from e

    def generate_vcard(self, name: str, email: Optional[str] = None,
                       phone: Optional[str] = None, org: Optional[str] = None,
                       url: Optional[str] = None, output_format: str = "png",
                       scale: int = 10, output_path: Optional[str] = None) -> bytes:
        """Generate a vCard QR code for contact sharing."""
        if not name or not name.strip():
            raise ValueError("Contact name cannot be empty.")
        try:
            qr = segno_helpers.make_vcard(name=name, email=email, phone=phone,
                                          org=org, url=url)
            buffer = io.BytesIO()
            qr.save(buffer, kind=output_format, scale=scale)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"vCard QR generation failed: {e}") from e

    def generate_geo(self, latitude: float, longitude: float,
                     output_format: str = "png", scale: int = 10,
                     output_path: Optional[str] = None) -> bytes:
        """Generate a geo-location QR code (opens maps app on scan)."""
        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180.")
        try:
            qr = segno_helpers.make_geo(lat=latitude, lng=longitude)
            buffer = io.BytesIO()
            qr.save(buffer, kind=output_format, scale=scale)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Geo QR generation failed: {e}") from e

    def generate_email(self, to: str, subject: Optional[str] = None,
                       body: Optional[str] = None, output_format: str = "png",
                       scale: int = 10, output_path: Optional[str] = None) -> bytes:
        """Generate an email QR code that opens a pre-filled email composer."""
        if not to or not to.strip():
            raise ValueError("Recipient email address cannot be empty.")
        try:
            qr = segno_helpers.make_email(to=to, subject=subject, body=body)
            buffer = io.BytesIO()
            qr.save(buffer, kind=output_format, scale=scale)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Email QR generation failed: {e}") from e

    def print_terminal(self, data: str) -> None:
        """Print a QR code to the terminal using ASCII art."""
        if not data or not data.strip():
            raise ValueError("data cannot be empty.")
        try:
            self._make_qr(data).terminal(compact=True)
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Terminal QR rendering failed: {e}") from e
