from django.core.files.uploadedfile import InMemoryUploadedFile
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.db.models.signals import pre_save, post_save, post_delete

from .models import Cover, PodcastSeries, CoverSize, PodcastEpisode, Audio
from .utils import ImageUtil


@receiver(pre_save, sender=Cover, dispatch_uid='pre.save_image')
def save_image(sender, instance, **kwargs):
    if hasattr(CoverSize, instance.dim):
        width = CoverSize[instance.dim].value
    else:
        width = None

    with ImageUtil(instance.image) as img_util:
        file, name, content_type, size = img_util.image_resized(h=width, w=width)

        if instance.bg_color is None:
            instance.bg_color = img_util.most_common_used_color()

    instance.image = InMemoryUploadedFile(file, 'image', name, content_type, size, None)
    instance.width = width
    instance.height = width

    # async def delete_existing(model, obj):
    #     old = None
    #     async for img in model.objects.filter(pk=instance.pk):
    #         old = img
    #
    #     new = instance.image
    #     if (old is not None and old is not new) or (old and new and old.image.url != new.url):
    #         old.adelete()
    #
    # asyncio.run(delete_existing(model=sender, obj=instance))

'''
    IMPORTANT: Covers' physical location can be referred by multiple
    resources so not deleting them 
'''
# @receiver(post_delete, sender=Cover, dispatch_uid="post_delete.cover")
# def delete_cover(sender, instance, *args, **kwargs):
#     if instance.image is not None and default_storage.exists(instance.image.path):
#         default_storage.delete(instance.image.path)


@receiver(post_save, sender=PodcastSeries, dispatch_uid="post.save_series")
def save_series(sender, instance, *args, **kwargs):
    # async_to_sync(create_image_formats)(instance)
    if instance.image is not None:
        for cover in instance.covers.all():
            cover.delete()

        bg_color = ImageUtil(instance.image).most_common_used_color()

        for size in CoverSize:
            instance.covers.create(dim=size.name, image=instance.image, bg_color=bg_color)


async def create_image_formats(instance):
    # await asyncio.gather(*[
    #     instance.covers.acreate(dim="lg", image=instance.image),
    #     instance.covers.acreate(dim="md", image=instance.image),
    #     instance.covers.acreate(dim="thumb", image=instance.image)
    # ])
    for size in CoverSize:
        instance.covers.create(dim=size.value, image=instance.image),


@receiver(post_delete, sender=Audio, dispatch_uid="post_delete.audio")
def save_audio(sender, instance, *args, **kwargs):
    if instance.file is not None and default_storage.exists(instance.file.path):
        default_storage.delete(instance.file.path)


@receiver(post_save, sender=PodcastEpisode, dispatch_uid="post_save.podcast_episode_image")
def add_podcast_episode_cover(sender, instance, *args, **kwargs):
    if instance.image is None:
        if instance.covers is None or instance.covers.count() == 0:
            new_covers = [Cover(image=c.image, dim=c.dim, height=c.height, width=c.width, bg_color=c.bg_color, content=instance) for c in instance.podcast_series.covers.all()]
            Cover.objects.bulk_create(new_covers)
    else:
        for cover in instance.covers.all():
            cover.delete()

        with ImageUtil(instance.image) as pillow_image:
            bg_color = pillow_image.most_common_used_color()

        for size in CoverSize:
            instance.covers.create(dim=size.name, image=instance.image, bg_color=bg_color)
# @receiver(pre_save, sender=PodcastEpisode, dispatch_uid="post_save.podcast_episode_audio")
# def add_podcast_episode_audio(sender, instance, *args, **kwargs):
#     if instance.audio is not None:
#         for (a, _) in Audio.BITRATE_CHOICES:
#
#             instance.audios.create(file=insta bit_rate)


