import datetime
import re

import musicbrainzngs

from .config import normalize_release_type

musicbrainzngs.set_useragent('ytmusic-feed', '0.1.0', 'toasterparty@derpymail.org')

cache = {}

def get_artist_data(mbid):
    global cache

    if mbid not in cache:
        try:
            cache[mbid] = musicbrainzngs.get_artist_by_id(mbid, includes=['url-rels', 'release-groups'])['artist']
        except Exception as e:
            print(e)

    return cache.get(mbid)

def normalize_release_title(x: str):
    return re.sub(r'[^a-zA-Z0-9]', '', x).lower()

def youtube_artist_to_mbid(artist_name, browse_id, get_compare_releases):
    try:
        artists = musicbrainzngs.search_artists(artist_name, limit=5)['artist-list']
    except Exception as e:
        print(e)
        return None

    for artist in artists:
        try:
            mbid = artist['id']
            artist_data = get_artist_data(mbid)
            links = artist_data.get('url-relation-list', [])
            for link in links:
                if 'youtube' in link['target'] and browse_id in link['target']:
                    return mbid

        except Exception as e:
            print(e)
            continue

    scores = []

    compare_releases = [normalize_release_title(x) for x in get_compare_releases()]
    for artist in artists:
        try:
            mbid = artist['id']
            artist_data = get_artist_data(mbid)
            release_data = artist_data.get('release-group-list', [])
            releases = [normalize_release_title(x['title']) for x in release_data]
            score = 0
            for compare_release in compare_releases:
                for release in releases:
                    if release in compare_release or compare_release in release:
                        score += 1
            scores.append((score, mbid))
        except Exception as e:
            print(e)

    try:
        scores.sort(reverse=True)
        return scores[0][1]
    except Exception as e:
        print(e)
        return None

def parse_release_date(release_date: str):
    d = None

    if not d:
        try:
            d = datetime.datetime.strptime(release_date, '%Y-%m-%d')
        except Exception:
            pass

    if not d:
        try:
            d = datetime.datetime.strptime(release_date, '%Y-%m')
        except Exception:
            pass

    if not d:
        try:
            d = datetime.datetime.strptime(release_date, '%Y')
        except Exception:
            pass

    try:
        d = d.date()
        if d > datetime.date.today():
            d = None
    except Exception:
        d = None
    
    return d

def get_releases(mbid, release_type_blacklist: list[str]):
    releases = []
    if not mbid:
        return releases

    try:
        release_data = get_artist_data(mbid)['release-group-list']
    except Exception as e:
        print(e)
        return releases

    for x in release_data:
        release_type_primary = x['primary-type']
        if normalize_release_type(release_type_primary) in release_type_blacklist:
            continue

        match = False
        release_type_secondary = None
        for secondary_type in x.get('secondary-type-list', []):
            if not release_type_secondary:
                release_type_secondary = secondary_type
            if normalize_release_type(secondary_type) in release_type_blacklist:
                match = True
                break
        if match:
            continue

        try:
            release_date = parse_release_date(x['first-release-date'])
        except Exception:
            release_date = None

        if not release_date:
            continue

        releases.append(
            {
                'title': x['title'],
                'type': release_type_primary,
                'secondary_type': release_type_secondary,
                'release_date': release_date,
            }
        )
    
    def key(x):
        return x['release_date']

    releases.sort(key=key, reverse=True)

    return releases
