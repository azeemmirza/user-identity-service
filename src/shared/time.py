from datetime import datetime, timezone


def utc_now():
    '''Returns the current UTC time as a timezone-aware datetime object.'''
    return datetime.now(timezone.utc)

def utc_now_naive():
    '''Returns the current UTC time as a naive datetime object (without timezone information).'''
    return utc_now().replace(tzinfo=None)