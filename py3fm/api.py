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
                        autocorrect=1, raw=0):
        """Artist: get tags for specific user.
        
        Parameters:
        ----------
        artist (Required, unless mbid): artist name
        mbid (Optional): musicbrainz id for the artist
        user (Optional): username; required if not authenticated
        autocorrect[0|1] (Optional): correct spelling
        raw: set raw=1 for full json
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
        
        response = self._send_request(args)
        print('response:\n', response, '\n\n')

        if raw:
            return response
        else:
            processed = []
            for tag in response[u"tags"]["tag"]:
                processed.append(tag[u"name"])

            return processed

    def artist_get_top_tags(self, artist=None, mbid=None, autocorrect=1,
            raw=0):
        """Artist: get top tags from all users.
        
        Parameters:
        ----------
        artist (Required, unless mbid): artist name
        mbid (Optional): musicbrainz id for the artist
        autocorrect[0|1] (Optional): correct spelling
        raw: set raw=1 for full json
        """
        if not artist and not mbid:
            raise TypeError("Must provide artist or mbid")
        
        args = {"method": "artist.gettoptags", "autocorrect":1}

        if artist:
            args["artist"] = artist
        elif mbid:
            args["mbid"] = mbid

        response = self._send_request(args)

        if raw:
            return response
        else:
            processed = {}
            for tag in response[u"toptags"]["tag"]:
                processed[tag[u"name"]] = tag[u"count"]

            return processed


    def tag_get_top_artists(self, tag, limit=3):
        """Tag: get top artists by tag."""
        args = {"method": "tag.gettopartists", "limit": limit, "tag": tag}
        
        return self._send_request(args)
        
    def track_get_similar(self, track, artist, limit=3):
        """Track: get similar tracks."""
        args = {"method": "track.getsimilar", "limit": limit,
                "track": track, "artist": artist}

        return self._send_request(args)

