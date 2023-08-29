from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_init

from .models import PodcastSeries, CoverSize, PodcastEpisode
from .utils import ImageUtil


@receiver(post_save, sender=PodcastSeries, dispatch_uid="post.save_series")
def save_series(sender, instance, *args, **kwargs):
    # async_to_sync(create_image_formats)(instance)
    if hasattr(instance, 'image'):
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


@receiver(pre_save, sender=PodcastEpisode, dispatch_uid="post_save.podcast_episode_audio")
def assign_episode_no(sender, instance, *args, **kwargs):
    if instance._state.adding and instance.episode_no == 1:
        with transaction.atomic():
            total_episode = PodcastEpisode.objects.filter(id=instance.podcast_series.id).count()
            instance.episode_no = total_episode + 1

