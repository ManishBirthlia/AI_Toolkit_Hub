import base64
from typing import Optional, Literal
from openai import OpenAI, APIError

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)


class DALLEClient:
    """OpenAI DALL·E provider for AI image generation."""

    DEFAULT_MODEL = "dall-e-3"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        logger.info(f"DALLEClient initialized | model='{self.model}'")

    def generate(self, prompt: str, size: str = "1024x1024",
                 quality: Literal["standard", "hd"] = "standard",
                 style: Literal["vivid", "natural"] = "vivid",
                 output_path: Optional[str] = None) -> bytes:
        """
        Generate an image from a text prompt using DALL·E.

        Args:
            prompt: Text description of the desired image.
            size: Image size. DALL·E 3 supports '1024x1024', '1792x1024', '1024x1792'.
            quality: 'standard' or 'hd'.
            style: 'vivid' (dramatic) or 'natural' (realistic).
            output_path: If provided, saves the image to this path.

        Returns:
            Raw PNG image bytes.

        Raises:
            ValueError: If prompt is empty or size is invalid.
            RuntimeError: If the API call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        valid_sizes = {"1024x1024", "1792x1024", "1024x1792"} if self.model == "dall-e-3" \
            else {"256x256", "512x512", "1024x1024"}
        if size not in valid_sizes:
            raise ValueError(f"Invalid size '{size}' for {self.model}. Valid: {valid_sizes}")

        try:
            kwargs = dict(model=self.model, prompt=prompt, n=1,
                          size=size, response_format="b64_json")
            if self.model == "dall-e-3":
                kwargs["quality"] = quality
                kwargs["style"] = style
            response = self.client.images.generate(**kwargs)
            image_bytes = base64.b64decode(response.data[0].b64_json)
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except APIError as e:
            raise RuntimeError(f"DALL·E generation failed: {e}") from e
