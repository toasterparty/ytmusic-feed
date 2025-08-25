from enum import Enum

ArtistMode = Enum('ArtistMode', ('ALL', 'LIBRARY', 'SUBSCRIPTIONS'))

def normalize_release_type(x: str):
    return x.lower().replace(' ', '').replace('-', '')

class Config:
    auth_filepath: str
    oauth_filepath: str
    artist_mode: ArtistMode
    release_type_blacklist: list[str] # https://musicbrainz.org/doc/Release_Group/Type
    max_feed_len: int

    def __init__(
            self,
            auth_filepath="auth.json",
            oauth_filepath="oauth.json",
            arist_mode=ArtistMode.ALL,
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
        ):
        self.auth_filepath = auth_filepath
        self.oauth_filepath = oauth_filepath
        self.artist_mode = arist_mode
        self.max_feed_len = max_feed_len

        self.release_type_blacklist = []
        for i in range(len(release_type_blacklist)):
            self.release_type_blacklist.append(normalize_release_type(release_type_blacklist[i]))
