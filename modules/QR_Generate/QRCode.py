import io
from pathlib import Path
from typing import Optional, Literal, Union

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import (
        RoundedModuleDrawer, CircleModuleDrawer,
        SquareModuleDrawer, GappedSquareModuleDrawer,
    )
    from qrcode.image.styles.colormasks import (
        SolidFillColorMask, RadialGradiantColorMask,
    )
    from PIL import Image
except ImportError as e:
    raise ImportError("pip install 'qrcode[pil]'") from e

from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

_MODULE_DRAWERS = {
    "square": SquareModuleDrawer, "rounded": RoundedModuleDrawer,
    "circle": CircleModuleDrawer, "gapped_square": GappedSquareModuleDrawer,
}


class QRCodeGenerator:
    """QR Code generator with styled modules, gradients, and logo embedding."""

    def __init__(self, error_correction: Literal["L", "M", "Q", "H"] = "H",
                 box_size: int = 10, border: int = 4) -> None:
        ec_map = {"L": qrcode.constants.ERROR_CORRECT_L,
                  "M": qrcode.constants.ERROR_CORRECT_M,
                  "Q": qrcode.constants.ERROR_CORRECT_Q,
                  "H": qrcode.constants.ERROR_CORRECT_H}
        self.error_correction = ec_map[error_correction]
        self.box_size = box_size
        self.border = border
        logger.info(f"QRCodeGenerator initialized | ec={error_correction}")

    def generate(self, data: str, fill_color: str = "black", back_color: str = "white",
                 output_path: Optional[str] = None, image_format: str = "PNG") -> bytes:
        """Generate a standard QR code image.

        Args:
            data: Data to encode (URL, text, vCard, WiFi, etc.).
            fill_color: Module foreground color.
            back_color: Background color.
            output_path: If provided, saves the image to this path.
            image_format: Output format ('PNG' or 'JPEG').

        Returns:
            Raw image bytes.

        Raises:
            ValueError: If data is empty.
            RuntimeError: If generation fails.
        """
        if not data or not data.strip():
            raise ValueError("data cannot be empty.")
        try:
            qr = qrcode.QRCode(error_correction=self.error_correction,
                               box_size=self.box_size, border=self.border)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            buffer = io.BytesIO()
            img.save(buffer, format=image_format)
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"QR code generation failed: {e}") from e

    def generate_styled(self, data: str,
                        module_style: Literal["square", "rounded", "circle",
                                              "gapped_square"] = "rounded",
                        fill_color: tuple = (0, 0, 0),
                        back_color: tuple = (255, 255, 255),
                        gradient: bool = False,
                        gradient_color: tuple = (100, 100, 255),
                        logo_path: Optional[str] = None,
                        logo_size_ratio: float = 0.25,
                        output_path: Optional[str] = None) -> bytes:
        """Generate a styled QR code with custom modules, gradients, and optional logo.

        Args:
            data: Data to encode.
            module_style: Module shape ('square', 'rounded', 'circle', 'gapped_square').
            fill_color: Foreground RGB tuple.
            back_color: Background RGB tuple.
            gradient: Apply a radial gradient.
            gradient_color: End color for gradient (RGB tuple).
            logo_path: Path to a logo image to embed in the center.
            logo_size_ratio: Logo width as fraction of QR width (0.0–0.4).
            output_path: If provided, saves the image to this path.

        Returns:
            Raw PNG image bytes.

        Raises:
            ValueError: If data is empty or logo_path not found.
            RuntimeError: If generation fails.
        """
        if not data or not data.strip():
            raise ValueError("data cannot be empty.")
        if logo_path and not Path(logo_path).exists():
            raise ValueError(f"Logo file not found: {logo_path}")
        if not 0.0 < logo_size_ratio <= 0.4:
            raise ValueError("logo_size_ratio must be between 0.0 and 0.4.")

        drawer_cls = _MODULE_DRAWERS.get(module_style, RoundedModuleDrawer)
        color_mask = (RadialGradiantColorMask(back_color=back_color,
                                               center_color=fill_color,
                                               edge_color=gradient_color)
                      if gradient else
                      SolidFillColorMask(back_color=back_color, front_color=fill_color))
        try:
            qr = qrcode.QRCode(error_correction=self.error_correction,
                               box_size=self.box_size, border=self.border)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(image_factory=StyledPilImage,
                                module_drawer=drawer_cls(),
                                color_mask=color_mask).convert("RGBA")
            if logo_path:
                logo = Image.open(logo_path).convert("RGBA")
                qr_w, qr_h = img.size
                logo_max = int(qr_w * logo_size_ratio)
                logo.thumbnail((logo_max, logo_max), Image.LANCZOS)
                lw, lh = logo.size
                img.paste(logo, ((qr_w - lw) // 2, (qr_h - lh) // 2), mask=logo)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Styled QR code generation failed: {e}") from e

    def decode(self, image_path: str) -> list[str]:
        """Decode QR codes from an image file."""
        if not image_path:
            raise ValueError("image_path cannot be empty.")
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"Image file not found: {image_path}")
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
        except ImportError as e:
            raise RuntimeError("pip install pyzbar") from e
        try:
            img = Image.open(path)
            return [obj.data.decode("utf-8") for obj in pyzbar_decode(img)]
        except Exception as e:
            raise RuntimeError(f"QR code decoding failed: {e}") from e
