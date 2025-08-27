import json
import os
import datetime
import copy

import ytmusicapi

from . import musicbrainz
from .config import Config, ArtistMode, DEFAULT_CONFIG, normalize_release_type

class Feed:
    credentials: ytmusicapi.OAuthCredentials | None
    client: ytmusicapi.YTMusic | None
    config: Config
    artists: dict

    def __init__(self, config=DEFAULT_CONFIG):
        self.config = config
        self.load_credentials_from_file()
        self.authenticate()

    def __str__(self):
        def default_serializer(x):
            if isinstance(x, (datetime.date, datetime.datetime)):
                return str(x)
            raise TypeError("Type not serializable")

        data = {
            'artists' : self.artists,
            'releases' : self.filtered_releases,
        }
        return json.dumps(data, default=default_serializer)

    def __repr__(self):
        return str(self)

    @property
    def filtered_releases(self):
        def is_not_blacklisted(x):
            blacklist = self.config.release_type_blacklist_normalized
            if normalize_release_type(x['type']) in blacklist:
                return False

            for type in x['secondary_types']:
                if normalize_release_type(type) in blacklist:
                    return False

            return True

        releases = copy.deepcopy(self.releases)
        releases = filter(is_not_blacklisted, releases)
        return list(releases)

    def print(self):
        date_width = 10
        type_width = max(len(r['type']) for r in self.filtered_releases)
        sec_width = max(len(' '.join(r['secondary_types'])) for r in self.filtered_releases)
        artist_width = max(len(r['artist']) for r in self.filtered_releases)
        for release in self.filtered_releases:
            print(
                f"{release['release_date']:<{date_width}} "
                f"{' '.join(release['secondary_types']):<{sec_width}} "
                f"{release['type']:<{type_width}} "
                f"{release['artist']:<{artist_width}} "
                f"- {release['title']}"
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
        self.releases = []
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

            releases = musicbrainz.get_releases(mbid)
            for release in releases:
                release['artist'] = artist_name

            self.artists[artist_name] = { 
                'browseId': browse_id,
                'mbid': mbid,
            }
            self.releases.extend(releases)

        def key(x):
            return x['release_date']

        self.releases.sort(key=key, reverse=True)

feed = Feed()
feed.collect_releases()
with open('out.json', 'w') as f:
    text = str(feed)
    f.write(text)
feed.print()
