import json
import os
import datetime

import ytmusicapi

from . import musicbrainz
from .config import Config, ArtistMode

# TODO cache the results of most API calls

class YTMusicFeed:
    credentials: ytmusicapi.OAuthCredentials | None
    client: ytmusicapi.YTMusic | None
    config: Config
    artists: dict

    def __init__(self, config=Config()):
        self.config = config
        self.load_credentials_from_file()
        self.authenticate()

    def __str__(self):
        def default_serializer(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return str(obj)
            raise TypeError("Type not serializable")
        
        return json.dumps(
            self.artists,
            default=default_serializer
        )

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

    def collect_releases(self):
        self.artists = {}
        data = []

        if self.config.artist_mode in (ArtistMode.ALL, ArtistMode.LIBRARY):
            data.extend(self.ytmusic.get_library_artists(limit=10000))
        if self.config.artist_mode in (ArtistMode.ALL, ArtistMode.SUBSCRIPTIONS):
            data.extend(self.ytmusic.get_library_subscriptions(limit=10000))

        for x in data:
            browse_id = x['browseId'].removeprefix("MPLA").removeprefix("UC")
            artist_name = x['artist']

            def get_compare_releases():
                yt_artist = self.ytmusic.get_artist(x['browseId'])
                yt_releases = []
                for yt_release_type in ['songs', 'albums']:
                    yt_releases.extend([
                        release.get('title') for release in yt_artist.get(yt_release_type,{}).get('results', [])
                    ])
                return yt_releases
            mbid = musicbrainz.youtube_artist_to_mbid(artist_name, browse_id, get_compare_releases)

            if not mbid:
                continue

            releases = musicbrainz.get_releases(mbid, self.config.release_type_blacklist)

            # TODO: de-dupe singles

            self.artists[artist_name] = { 
                'browseId': browse_id,
                'mbid': mbid,
                'releases': releases,
            }

feed = YTMusicFeed()
feed.collect_releases()
print(str(feed))
