#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Christopher C. Strelioff <chris.strelioff@gmail.com>
#
# Distributed under terms of the MIT license.

"""
api.py -- the main lastfm api interface.
"""
import time
import json

from urllib.parse import urlencode

from urllib.request import urlopen
from urllib.request import Request
from urllib.request import HTTPError
from urllib.request import URLError


class client(object):

    def __init__(self, key, secret):
        self.API_URL = "http://ws.audioscrobbler.com/2.0/"
        self.API_KEY = key
        self.API_SEC = secret

        self.last_call = time.time()

        self.kwargs = {"api_key": self.API_KEY, "format": "json"}

        # set to True when user authenticated
        self.authenticated = False

    def _throttle(self):
        """Limit to minimum of 0.2 seconds per call."""
        min_time = 0.2

        now = time.time()
        time_since_last = now - self.last_call

        if time_since_last < min_time:
            time.sleep(min_time - time_since_last)

        self.last_call = now

    def _send_request(self, args, **kwargs):
        """General request to the API."""
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
            print("HTTP error: {:}".format(e.code))
        except URLError as e:
            print("Network error: {}".format(e.reason.args[1]))

        return response_data

    def artist_get_tags(self, artist=None, mbid=None, user=None,
                        autocorrect=1):
        """Artist: get artist tags by specific user.

        http://www.last.fm/api/show/artist.getTags

        :param artist: artist name, required unless mbid
        :type artist: str
        :param mbid: musicbrainz id for the artist, optional
        :type mbid: str
        :param user: username, required if not authenticated
        :type user: str
        :param autocorrect: autocorrect spelling, [0|1]
        :type autocorrect: int
        :rtype: list if raw=0 or dict if raw=1
        """
        if not artist and not mbid:
            raise TypeError("Must provide artist or mbid")

        if not self.authenticated and not user:
            raise TypeError("If user not authenticated, must provide user.")

        args = {"method": "artist.gettags", "autocorrect": 1}

        if artist:
            args["artist"] = artist
        elif mbid:
            args["mbid"] = mbid

        if user:
            args["user"] = user

        return self._send_request(args)
