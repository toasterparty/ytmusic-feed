import musicbrainzngs

musicbrainzngs.set_useragent('ytmusic-feed', '0.1.0', 'toasterparty@derpymail.org')

def youtube_artist_to_mbid(artist_name, browse_id):
    try:
        artists = musicbrainzngs.search_artists(artist_name, limit=5)['artist-list']
    except Exception as e:
        print(e)
        return None

    for artist in artists:
        try:
            mbid = artist['id']
            artist = musicbrainzngs.get_artist_by_id(mbid, includes=['url-rels'])['artist']
            links = artist.get('url-relation-list', [])
            for link in links:
                if 'youtube' in link['target'] and browse_id in link['target']:
                    return mbid
        except Exception as e:
            print(e)

    return None
