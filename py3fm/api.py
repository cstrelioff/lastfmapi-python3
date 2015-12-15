#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Christopher C. Strelioff <chris.strelioff@gmail.com>
#
# Distributed under terms of the MIT license.

'''
api.py -- the main lastfm api interface.
'''
import time
import json

from urllib.parse import urlencode

from urllib.request import urlopen
from urllib.request import Request
from urllib.request import HTTPError
from urllib.request import URLError


class client(object):

    def __init__(self, key, secret):
        self.API_URL = 'http://ws.audioscrobbler.com/2.0/'
        self.API_KEY = key
        self.API_SEC = secret

        self.last_call = time.time()

        self.kwargs = {'api_key': self.API_KEY,
                       'format': 'json'}

        # set to True when user authenticated
        self.authenticated = False

    def _throttle(self):
        '''Limit to minimum of 0.2 seconds per call.'''
        min_time = 0.2

        now = time.time()
        time_since_last = now - self.last_call

        if time_since_last < min_time:
            time.sleep(min_time - time_since_last)

        self.last_call = now

    def _send_request(self, args, **kwargs):
        '''General request to the API.'''
        self._throttle()

        kwargs.update(args)
        kwargs.update(self.kwargs)

        try:
            # format data and request
            data = urlencode(kwargs).encode('utf8')
            req = Request(self.API_URL, data)

            # query lastfm
            response = urlopen(req)

            # parse response data
            response_data = json.loads(response.readall().decode('utf8'))
        except HTTPError as e:
            raise Exception('HTTP error: {:}'.format(e.code))
        except URLError as e:
            raise Exception('Network error: {}'.format(e.reason.args[1]))

        return response_data

    def artist_get_correction(self, artist):
        '''Use the last.fm corrections data to check whether the supplied
        artist has a correction to a canonical artist.

        http://www.last.fm/api/show/artist.getCorrection

        :param artist: artist name, required
        :type artist: str
        :rtype: dict
        '''
        args = {'method': 'artist.getcorrection',
                'artist': artist}

        return self._send_request(args)

    def artist_get_events(self, artist=None, mbid=None, autocorrect=1,
                          page=1, limit=10, festival=0):
        '''Get a list of upcoming events for this artist.

        http://www.last.fm/api/show/artist.getEvents

        :param artist: artist name, required unless mbid
        :type artist: str
        :param mbid: musicbrainz id for the artist, optional
        :type mbid: str
        :param autocorrect: autocorrect spelling, [0|1]
        :type autocorrect: int
        :param page: the page number to fetch, default page=1
        :type page: int
        :param limit: the number of results to fetch per page, default limit=10
        :type limit: int
        :param festival: Whether only festivals should be returned, or all
        events, [0|1], optional.
        :type festival: int
        :rtype: dict
        '''
        if not artist and not mbid:
            raise TypeError('Must provide artist or mbid')

        args = {'method': 'artist.getevents',
                'autocorrect': autocorrect,
                'page': page,
                'limit': limit,
                'festival': festival}

        if artist:
            args['artist'] = artist
        elif mbid:
            args['mbid'] = mbid

        return self._send_request(args)

    def artist_get_tags(self, artist=None, mbid=None, user=None,
                        autocorrect=1):
        '''Get the tags applied by an individual user to an artist on Last.fm.

        http://www.last.fm/api/show/artist.getTags

        :param artist: artist name, required unless mbid
        :type artist: str
        :param mbid: musicbrainz id for the artist, optional
        :type mbid: str
        :param user: username, required if not authenticated
        :type user: str
        :param autocorrect: autocorrect spelling, [0|1]
        :type autocorrect: int
        :rtype: dict
        '''
        if not artist and not mbid:
            raise TypeError('Must provide artist or mbid')

        if not self.authenticated and not user:
            raise TypeError('If user not authenticated, must provide user.')

        args = {'method': 'artist.gettags',
                'autocorrect': autocorrect}

        if artist:
            args['artist'] = artist
        elif mbid:
            args['mbid'] = mbid

        if user:
            args['user'] = user

        return self._send_request(args)

    def artist_get_top_albums(self, artist=None, mbid=None, autocorrect=1,
                              page=1, limit=10):
        '''Get the top albums for an artist on Last.fm, ordered by popularity.

        http://www.last.fm/api/show/artist.getTopAlbums

        :param artist: artist name, required unless mbid
        :type artist: str
        :param mbid: musicbrainz id for the artist, optional
        :type mbid: str
        :param autocorrect: autocorrect spelling, [0|1]
        :type autocorrect: int
        :param page: the page number to fetch, default page=1
        :type page: int
        :param limit: the number of results to fetch per page, default limit=10
        :type limit: int
        :rtype: dict
        '''
        if not artist and not mbid:
            raise TypeError('Must provide artist or mbid')

        args = {'method': 'artist.gettopalbums',
                'autocorrect': autocorrect,
                'page': page,
                'limit': limit}

        if artist:
            args['artist'] = artist
        elif mbid:
            args['mbid'] = mbid

        return self._send_request(args)

    def artist_get_top_fans(self, artist=None, mbid=None, autocorrect=1):
        '''Get the top fans for an artist on Last.fm, based on listening data.

        http://www.last.fm/api/show/artist.getTopFans

        :param artist: artist name, required unless mbid
        :type artist: str
        :param mbid: musicbrainz id for the artist, optional
        :type mbid: str
        :param autocorrect: autocorrect spelling, [0|1]
        :type autocorrect: int
        :rtype: dict
        '''
        if not artist and not mbid:
            raise TypeError('Must provide artist or mbid')

        args = {'method': 'artist.gettopfans',
                'autocorrect': autocorrect}

        if artist:
            args['artist'] = artist
        elif mbid:
            args['mbid'] = mbid

        return self._send_request(args)
