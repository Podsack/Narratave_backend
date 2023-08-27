import sys
import io
import os
import datetime
from django.core.files import File
from django.db.models import F

from PIL import Image
from pydub import AudioSegment

from .models import PodcastEpisode
from .v1.serializers import PodcastEpisodeSerializer


class ImageUtil:
    name = None
    image = None
    _conversion_format = "JPEG"

    def __enter__(self):
        return self  # Return the context manager instance (optional)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.image is not None:
            self.image = None
            self.name = None
            print("-----------------closing image-----------")

    def __init__(self, image):
        self.name = image.name
        self.image = Image.open(image).convert(mode="RGB")

    def most_common_used_color(self):
        # Get width and height of Image
        img = self.image
        width, height = img.size

        # Initialize Variable
        r_total = 0
        g_total = 0
        b_total = 0

        count = 0

        pixels = list(img.getdata())

        # Iterate through each pixel
        for pixel in pixels:
            if img.mode == "RGB":
                r, g, b = pixel
            elif img.mode == "RGBA":
                r, g, b, a = pixel
            else:
                raise IOError("Unsupported image mode")

            r_total += r
            g_total += g
            b_total += b
            count += 1

        color_tuple = r_total / count, g_total / count, b_total / count
        return covert_rgb_to_hex(color_tuple)

    def image_resized(self, h=None, w=None):
        _image = self.image
        content_type = Image.MIME[self._conversion_format]
        [rw, rh] = _image.size

        if h is None or w is None:
            h = rh
            w = rw

        if rh >= rw:
            new_width = rw
            new_height = rw
        else:
            new_height = rh
            new_width = rh

        left = (rw - new_width) / 2
        top = (rh - new_height) / 2
        right = (rw + new_width) / 2
        bottom = (rh + new_height) / 2

        image_cropped = _image.crop((left, top, right, bottom))

        imageTemproaryResized = image_cropped.resize((w, h))
        file = io.BytesIO()
        imageTemproaryResized.save(file, self._conversion_format)
        file.seek(0)
        size = sys.getsizeof(file)
        file_name, file_extension = os.path.splitext(self.name)
        output_file_name = f"{file_name}.{self._conversion_format}"
        return file, output_file_name, content_type, size


def covert_rgb_to_hex(rgb_tuple):
    rgb_values = tuple(int(val) for val in rgb_tuple)
    return "#{:02x}{:02x}{:02x}".format(*rgb_values)


def convert_audio_in_aac(segmented_audio, bitrate, file_name):
    if bitrate is None:
        raise ValueError("Parameters are not defined")

    converted_format = "aac"
    ts = int(datetime.datetime.utcnow().timestamp())
    out_file_name = f"{file_name}_{ts}_{bitrate}.{converted_format}"
    new_audio = segmented_audio.export(format="adts", bitrate=f"{bitrate}k")
    audio_duration = segmented_audio.duration_seconds
    converted_file = File(file=new_audio, name=out_file_name)
    file_size = converted_file.size/1024

    return file_size, converted_file, converted_format, audio_duration


def get_segmented_audio(audio_file):
    if audio_file is None:
        raise ValueError("Parameters are not defined")

    file_name, file_extension = os.path.splitext(audio_file.name)
    curr_audio = AudioSegment.from_file(file=audio_file, format=file_extension.replace('.', ''))
    return file_name, curr_audio
