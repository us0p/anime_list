from PIL import Image
import io
from aiohttp import ClientSession

class ImagePixels:
    default_width = 30
    default_height = 23
    _pixel_count = 0
    image_pixels: list[tuple[int,int,int]]

    def __init__(
        self,
        image_pixels: list[tuple[int,int,int]],
        default_height: int
    ):
        self.image_pixels = image_pixels
        self.default_height = default_height

    def __len__(self):
        return len(self.image_pixels)

    def __iter__(self):
        return self

    def __next__(self):
        image_line_count = len(self.image_pixels)/self.default_width
        if self._pixel_count >= image_line_count:
            raise StopIteration

        start = self._pixel_count * self.default_width
        end = (self._pixel_count + 1) * self.default_width
        self._pixel_count += 1
        return self.image_pixels[start:end]

class ImageBuilder():
    async def produce_ascii_image(
        self,
        session: ClientSession,
        image_url: str
    ) -> ImagePixels:
        image_bytes = await self._get_image(session, image_url)
        return self._build_image(image_bytes)

    def _build_image(self, image_bytes: bytes) -> ImagePixels:
        with Image.open(io.BytesIO(image_bytes)) as image_file:
            w, h = image_file.size
            aspect_ratio = h / w
            new_h = aspect_ratio * ImagePixels.default_width * 0.55
            image = image_file.resize(
                (
                    ImagePixels.default_width,
                    int(new_h)
                )
            )
            image_pixels = list(image.getdata())
            default_height = int(
                len(image_pixels) / ImagePixels.default_width
            )
            return ImagePixels(image_pixels, default_height)

    async def _get_image(
            self,
            session: ClientSession,
            image_url: str
    ) -> bytes:
        async with session.get(image_url) as response:
                return await response.read()
