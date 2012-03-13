#!/usr/bin/env python
"""
Python module which can be used to send SMS messages via the Clickatell HTTP/S API
Interface on https://api.clickatell.com/

See U{the Clickatell HTTP/S API documentation<http://www.clickatell.com/downloads/http/Clickatell_http_2.2.7.pdf>}
for more information on how their HTTP/S API interface works

Author: Jacques Marneweck <jacques@powertrip.co.za> (jacquesmarneweck.com)
Copyright: 2006-2012 Jacques Marneweck.  All rights reserved.
License: MIT LICENSE
"""

import urllib
import urllib2


class ClickatellError (Exception):
    """
    Base class for Clickatell errors
    """


class ClickatellAuthenticationError (ClickatellError):
    pass


class Clickatell(object):
    """
    Provides a wrapper around the Clickatell HTTP/S API interface
    """

    def __init__ (self, username, password, api_id, user_agent='pyclickatell'):
        """
        Initialise the Clickatell class

        Expects:
         - username - your Clickatell Central username
         - password - your Clickatell Central password
         - api_id - your Clickatell Central HTTP API identifier
        """
        self.has_authed = False

        self.username = username
        self.password = password
        self.api_id = api_id

        self.session_id = None
        self.user_agent = user_agent

    def auth (self):
        """
        Authenticate against the Clickatell API server
        """
        url = 'https://api.clickatell.com/http/auth'

        post = [
            ('user', self.username),
            ('password', self.password),
            ('api_id', self.api_id),
        ]

        result = self.curl (url, post)

        if result[0] == 'OK':
            assert (32 == len(result[1]))
            self.session_id = result[1]
            self.has_authed = True
            return True
        else:
            return False

    def getbalance (self):
        """
        Get the number of credits remaining at Clickatell
        """
        if self.has_authed == False:
            self.auth()

        url = 'https://api.clickatell.com/http/getbalance'

        post = [
            ('session_id', self.session_id),
        ]

        result = self.curl (url, post)
        if result[0] == 'Credit':
            assert (0 <= result[1])
            return result[1]
        else:
            return False

    def getmsgcharge (self, apimsgid):
        """
        Get the message charge for a previous sent message
        """
        if self.has_authed == False:
            self.auth()

        assert (32 == len(apimsgid))

        url = 'https://api.clickatell.com/http/getmsgcharge'

        post = [
            ('session_id', self.session_id),
            ('apimsgid', apimsgid),
        ]

        result = self.curl (url, post)
        result = ' '.join(result).split(' ')

        if result[0] == 'apiMsgId':
            assert (apimsgid == result[1])
            assert (0 <= result[3])
            return result[3]
        else:
            return False

    def ping (self):
        """
        Ping the Clickatell API interface to keep the session open
        """
        if self.has_authed == False:
            self.auth()

        url = 'https://api.clickatell.com/http/ping'

        post = [
            ('session_id', self.session_id),
        ]

        result = self.curl (url, post)

        if result[0] == 'OK':
            return True
        else:
            self.has_authed = False
            return False

    def sendmsg (self, message):
        """
        Send a mesage via the Clickatell API server

        message = {
            'to': 'to_msisdn',
            'sender': 'from_msisdn',
            'text': 'This is a test message',
            'climsgid': 'random_md5_hash',
        }

        result = clickatell.sendmsg(message)
        if result[0] == True:
            print "Message was sent successfully"
            print "Clickatell returned %s" % result[1]
        else:
            print "Message was not sent"

        """
        if self.has_authed == False:
            self.auth()

        url = 'https://api.clickatell.com/http/sendmsg'

        post = [
            ('session_id', self.session_id),
            ('to', message['to']),
            ('text', message['text'])
        ]

        if 'sender' in message:
            post.append(('from', message['sender']))

        if 'climsgid' in message:
            post.append(('climsgid', message['climsgid']))

        result = self.curl (url, post)

        if result[0] == 'ID':
            print result[1]
            assert (result[1])
            return (True, result[1])
        else:
            return (False, )

    def tokenpay (self, voucher):
        """
        Redeem a voucher via the Clickatell API interface
        """
        if self.has_authed == False:
            self.auth()

        assert (16 == len(voucher))

        url = 'https://api.clickatell.com/http/token_pay'

        post = [
            ('session_id', self.session_id),
            ('token', voucher),
        ]

        result = self.curl (url, post)

        if result[0] == 'OK':
            return True
        else:
            return False

    def curl (self, url, post_list):
        """
        Inteface for sending web requests to the Clickatell API Server
        """
        post_data = {}
        for item in post_list:
            post_data[item[0]] = item[1]

        req = urllib2.Request(url=url, data=urllib.urlencode(post_data))

        req.add_header("User-Agent", self.user_agent)
        req.add_header("Accept", '')

        fp = urllib2.urlopen(req)
        return fp.read().split(": ")
