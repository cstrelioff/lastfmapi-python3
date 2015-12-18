#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Christopher C. Strelioff <chris.strelioff@gmail.com>
#
# Distributed under terms of the MIT license.

'''
auth.py -- authentication code for lastfm users.
'''
import time
import json
import hashlib

from urllib.parse import urlencode

from urllib.request import urlopen
from urllib.request import Request
from urllib.request import HTTPError
from urllib.request import URLError


class authenticate(object):

    def __init__(self, key, secret):
        self.API_URL = 'http://ws.audioscrobbler.com/2.0/'
        self.API_KEY = key
        self.API_SEC = secret
        self.token = None

        self.AUTH_URL = 'http://www.last.fm/api/auth/'

        self.last_call = time.time()

        self.kwargs = {'api_key': self.API_KEY,
                       'format': 'json'}

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

            print('\n-----')
            print('req.full_url:', req.full_url)
            print('req.data:', req.data.decode('utf8'))
            url = req.full_url + '?' + req.data.decode('utf8')
            print('full url:', url)
            print('-----\n')

            # query lastfm
            response = urlopen(req)

            # parse response data
            response_data = json.loads(response.readall().decode('utf8'))
        except HTTPError as e:
            raise Exception('HTTP error: {:}'.format(e.code))
        except URLError as e:
            raise Exception('Network error: {}'.format(e.reason.args[1]))

        return response_data

    def _generate_api_sig(self, arg_list):
        '''Generate an api signature by joining the passed arg_list and
        returning the md5 hash.'''
        arg_string = ''.join(arg_list).encode('utf8')

        m = hashlib.md5()
        m.update(arg_string)

        return m.hexdigest()

    def auth_get_token(self):
        '''Fetch an unathorized request token for an API account. This is step
        2 of the authentication process for desktop applications. Web
        applications do not need to use this service. 

        http://www.last.fm/api/show/auth.getToken 

        :rtype: str
        '''
        args = {'method': 'auth.gettoken'}
        response = self._send_request(args)
        self.token = response['token']

        return self.token

    def auth_get_session(self):
        '''Fetch a session key for a user. The third step in the authentication
        process. See the authentication how-to for more information. 

        :rtype: dict
        '''
        if self.token is None:
            raise Exception('Can\'t generate URL without token!')

        # generate api_sig for this call
        arg_list = ['api_key', self.API_KEY,
                    'method', 'auth.getSession',
                    'token', self.token,
                    self.API_SEC]
        api_sig = self._generate_api_sig(arg_list)

        # make reuest to get seesion key
        # -- KEEP THIS SAFE SOMEWHERE!
        args = {'method': 'auth.getsession',
                'token': self.token,
                'api_sig': api_sig}
        response = self._send_request(args)

        return response

    def generate_user_auth_url(self):
        '''Generate URL where user can authorize your code to access account
        information.

        :rtype: str
        '''
        if self.token is None:
            raise Exception('Can\'t generate URL without token!')

        kwargs = {'api_key': self.API_KEY,
                  'token': self.token}
        data = urlencode(kwargs).encode('utf8')

        req = Request(self.AUTH_URL, data)
        url = req.full_url + '?' + req.data.decode('utf8')

        return url
