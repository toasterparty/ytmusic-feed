from dataclasses import dataclass
from enum import Enum

ArtistMode = Enum('ArtistMode', ('ALL', 'LIBRARY', 'SUBSCRIPTIONS'))

def normalize_release_type(x: str):
    return x.lower().replace(' ', '').replace('-', '')

@dataclass
class Config:
    auth_filepath: str
    oauth_filepath: str
    artist_mode: ArtistMode
    release_type_blacklist: list[str] # https://musicbrainz.org/doc/Release_Group/Type
    max_feed_len: int

    @property
    def release_type_blacklist_normalized(self):
        return [normalize_release_type(x) for x in self.release_type_blacklist]

DEFAULT_CONFIG = Config(
    auth_filepath="auth.json",
    oauth_filepath="oauth.json",
    artist_mode=ArtistMode.ALL,
    release_type_blacklist=[
        "Broadcast",
        "Other",
        "Compilation",
        "Spokenword",
        "Interview",
        "Audiobook",
        "Audio Drama",
        "Live",
        "Remix",
        "DJ-mix",
    ],
    max_feed_len=100
)
