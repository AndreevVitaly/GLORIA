import uuid
import warnings
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_AVATAR_BYTES = 5 * 1024 * 1024
MAX_AVATAR_PIXELS = 16_000_000
ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


def avatar_path(instance, filename):
    return f"avatars/{instance.user.uuid}/{uuid.uuid4().hex}.jpg"


def prepare_avatar(upload):
    """Validate decoded content, then store a small JPEG without metadata or active content."""
    if upload.size > MAX_AVATAR_BYTES:
        raise ValidationError("Размер фотографии не должен превышать 5 МБ.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            upload.seek(0)
            with Image.open(upload) as image:
                if image.format not in ALLOWED_FORMATS:
                    raise ValidationError("Загрузите фотографию в формате JPEG, PNG или WebP.")
                if getattr(upload, "content_type", None) != ALLOWED_FORMATS[image.format]:
                    raise ValidationError("Тип файла не соответствует содержимому фотографии.")
                if image.width * image.height > MAX_AVATAR_PIXELS:
                    raise ValidationError("Фотография слишком большая: максимум 16 мегапикселей.")
                image.load()
                image = ImageOps.exif_transpose(image).convert("RGB")
                image = ImageOps.fit(image, (512, 512), method=Image.Resampling.LANCZOS)
                result = BytesIO()
                image.save(result, format="JPEG", quality=88)
        return ContentFile(result.getvalue(), name=f"{uuid.uuid4().hex}.jpg")
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as error:
        raise ValidationError("Не удалось прочитать фотографию. Выберите другой файл.") from error
    finally:
        upload.seek(0)
