import datetime

def release_date(release_date: str):
    """
    e.g. arg.: data['album']['release_date']
    """
    try:
        _release_date=datetime.date.fromisoformat(release_date)
    except ValueError:
        ymd = [1]*3
        for i, x in enumerate(release_date.split('-')):
            ymd[i] = int(x)
        _release_date = datetime.date(ymd[0], ymd[1], ymd[2])

    return _release_date

def image_url(data: dict):
    """
    e.g. arg.: data['track']['album']
    """
    try:
        image_url = data['images'][1]['url']
    except IndexError:
        try:
            image_url = data['images'][0]['url']
        except IndexError:
            return None
    except KeyError:
        image_url = None

    return image_url

def added_played_at(data: dict):
    """"
    e.g. arg.: data[items][0]
    """
    try:
        try:
            dt = data['added_at']
        except KeyError:
            dt = data['played_at']
    except KeyError:
        return None
    
    try:
        date = datetime.datetime.fromisoformat(dt)
    except ValueError:
        date = datetime.datetime.strptime(dt, r'%Y-%m-%dT%H:%M:%S.%fZ')

    date = date.replace(tzinfo=datetime.timezone.utc)
    return date

def artist_names(artists: dict):
    artist_names = ",".join([artist['name'] for artist in artists])
    return artist_names

def get_user_favourite_pl_id(user_id: str):
    return user_id + '-fv'

def get_user_recently_played_pl_id(user_id: str):
    return user_id + '-rp'
    