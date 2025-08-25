import json
import os
import ytmusicapi
from enum import Enum
from datetime import date

from . import musicbrainz

# TODO cache the results of most API calls

ArtistMode = Enum('ArtistMode', ('ALL', 'LIBRARY_ONLY', 'SUBSCRIPTIONS_ONLY'))

class YTMusicFeedConfig:
    auth_filepath: str
    oauth_filepath: str
    artist_mode: ArtistMode
    max_feed_len: int

    def __init__(
            self,
            auth_filepath="auth.json",
            oauth_filepath="oauth.json",
            arist_mode=ArtistMode.ALL,
            max_feed_len=100
        ):
        self.auth_filepath = auth_filepath
        self.oauth_filepath = oauth_filepath
        self.artist_mode = arist_mode
        self.max_feed_len = max_feed_len

class YTMusicFeed:
    credentials: ytmusicapi.OAuthCredentials | None
    client: ytmusicapi.YTMusic | None
    config: YTMusicFeedConfig
    artists: dict

    def __init__(self, config=YTMusicFeedConfig()):
        self.config = config
        self.load_credentials_from_file()
        self.authenticate()

    def load_credentials_from_file(self):
        filepath = self.config.auth_filepath
        if not os.path.exists(filepath):
            raise Exception(f"Could not find auth file '{filepath}'")

        with open(filepath, "r") as file:
            data = json.loads(file.read())
            self.credentials = ytmusicapi.OAuthCredentials(
                client_id=data["installed"]["client_id"],
                client_secret=data["installed"]["client_secret"]
            )

    def authenticate(self):
        def new_ytmusic():
            return ytmusicapi.YTMusic(self.config.oauth_filepath, oauth_credentials=self.credentials)

        try:
            self.ytmusic = new_ytmusic()
            self.ytmusic.get_library_artists(limit=1)
            return
        except Exception:
            pass

        refreshing_token = ytmusicapi.setup_oauth(self.credentials.client_id, self.credentials.client_secret)
        with open(self.config.oauth_filepath, "w") as file:
            file.write(refreshing_token.as_json())
        self.ytmusic = new_ytmusic()

    def collect_artists(self):
        self.artists = {}
        data = []

        if self.config.artist_mode in (ArtistMode.ALL, ArtistMode.LIBRARY_ONLY):
            data.extend(self.ytmusic.get_library_artists(limit=10000))
        if self.config.artist_mode in (ArtistMode.ALL, ArtistMode.SUBSCRIPTIONS_ONLY):
            data.extend(self.ytmusic.get_library_subscriptions(limit=10000))

        for x in data:
            browse_id = x['browseId'].removeprefix("MPLA")
            self.artists[x['artist']] = { 
                'browseId': browse_id,
                'mbid': musicbrainz.youtube_artist_to_mbid(x['artist'], browse_id),
            }

    def collect_releases(self):
        for artist_name in self.artists:
            artist = self.artists[artist_name]
            artist_data = self.ytmusic.get_artist(artist['browseId'])

            def collect(category):
                browse_id = artist_data[category].get('browseId')
                params = artist_data[category].get('params')
                if not browse_id or not params:
                    data = artist_data[category]['results']
                else:
                    data = self.ytmusic.get_artist_albums(
                        browse_id,
                        params=params,
                        limit=self.config.max_feed_len,
                        order="Recency"
                    )

                for x in data:
                    pass
                    # TODO: if year older than top 100, skip

                return data

            # TODO: dedupe singles that are in albums
            artist['albums'] = collect('albums')
            artist['singles'] = collect('singles')

feed = YTMusicFeed()
feed.collect_artists()
# feed.collect_releases()

print(json.dumps(feed.artists))
