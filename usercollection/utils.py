def add_duration(value, podcast1):
    total_duration = value + podcast1['podcastepisode__duration_in_sec']
    return total_duration


def get_cover_from_list(podcast_episode_list):
    if podcast_episode_list is None or len(podcast_episode_list) == 0:
        return ''

    return podcast_episode_list[0]['podcastepisode__covers'][0]
