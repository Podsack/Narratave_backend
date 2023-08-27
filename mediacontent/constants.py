from enum import Enum


class SectionEnum(Enum):
    WEEKLY_PICKS = "Weekly Picks"
    RECOMMENDED_FOR_YOU = "Recommended For You"
    CONTINUE_WHERE_YOU_LEFT = "Continue where you left"
    NEW_RELEASES = "New Releases"
    COMING_SOON = "Coming Soon"


BITRATE_CHOICES = [
    (32, '32 Kbps'),
    (64, '64 Kbps'),
    (128, '128 Kbps'),
]