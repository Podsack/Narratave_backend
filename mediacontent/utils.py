import sys
import io
import os
import datetime
from django.core.files import File

from PIL import Image
from pydub import AudioSegment


def most_common_used_color(img):
    # Get width and height of Image
    width, height = img.size

    # Initialize Variable
    r_total = 0
    g_total = 0
    b_total = 0

    count = 0

    # Iterate through each pixel
    for x in range(0, width):
        for y in range(0, height):
            # r,g,b value of pixel
            r, g, b = img.getpixel((x, y))

            r_total += r
            g_total += g
            b_total += b
            count += 1

    color_tuple = r_total / count, g_total / count, b_total / count
    return covert_rgb_to_hex(color_tuple)


def image_resized(image, h=None, w=None):
    name = image.name
    _image = Image.open(image)
    content_type = Image.MIME[_image.format]

    if h is None or w is None:
        [h, w] = _image.size

    bg_color = most_common_used_color(img=_image)
    imageTemproaryResized = _image.resize((w, h))
    file = io.BytesIO()
    imageTemproaryResized.save(file, _image.format)
    file.seek(0)
    size = sys.getsizeof(file)
    return file, name, content_type, size, bg_color


def covert_rgb_to_hex(rgb_tuple):
    rgb_values = tuple(int(val) for val in rgb_tuple)
    return "#{:02x}{:02x}{:02x}".format(*rgb_values)


def convert_audio_in_aac(segmented_audio, bitrate, file_name):
    if bitrate is None:
        raise ValueError("Parameters are not defined")

    converted_format = ".aac"
    ts = int(datetime.datetime.utcnow().timestamp())
    out_file_name = f"{file_name}_{ts}_{bitrate}_{converted_format}"
    new_audio = segmented_audio.export(out_f=out_file_name, format="adts", bitrate=f"{bitrate}k")
    audio_duration = segmented_audio.duration_seconds
    file_size = os.path.getsize(out_file_name)/1000

    return file_size, new_audio, converted_format, audio_duration


def get_segmented_audio(audio_file):
    if audio_file is None:
        raise ValueError("Parameters are not defined")

    file_name, file_extension = os.path.splitext(audio_file.name)
    curr_audio = AudioSegment.from_file(file=audio_file, format=file_extension.replace('.', ''))
    return file_name, curr_audio
