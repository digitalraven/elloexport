# coding: UTF-8
#
# Copyright © 2015, Stew Wilson <stew@zeropointinformation.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided this permission
# notice appears in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import xmlrpclib
import dateutil.parser
try:
    from hashlib import md5
except:
    import md5 as _md5
    md5 = _md5.new


class livejournal:
    """
    A *very* basic class for posting to livejournal. No reading, no logging in,
    no friends-checking, no music, no mood or smilies or tags (so far, aynyway)
    just posting. Does authentication via XML-RPC challenge/response.

    Server is the fqdn of a website running a (fork of) the Livejournal
    codebase, e.g. "www.livejournal.com", "www.dreamwidth.org". Do not provide
    a protocol (http://) or a path (/interface/foo), these are added
    automatically.

    username is the name of the account to post to. Posting as a delegate or in
    communities is not supported.
    """
    def __init__(self, server, username, password):
        sname = "http://" + server + "/interface/xmlrpc"
        self.server = xmlrpclib.ServerProxy(sname)
        self.user = username
        self.password = password
    
    def _challenge(self):
        """
        Implements XML-RPC challenge/response and builds the base param set.
        """
        challenge = self.server.LJ.XMLRPC.getchallenge()
        params = {'username': self.user,
                  'ver': '1',
                  'auth_method': 'challenge',
                  'auth_challenge': challenge['challenge'],
                  'auth_response': self._calcchallenge(challenge['challenge'],self.password)}
        return params

    def _calcchallenge(self, challenge, password):
        """
        Calculate the correct response for the challenge.
        """
        return md5(challenge + md5(password).hexdigest()).hexdigest()

    def post(self, subject, post, timestamp):
        """
        Send a given post to the server, with the specified subject and
        timestamp.
        
        The timestamp is used to date the entry, but it is not noted as
        backdated.
        """

        postdate = dateutil.parser.parse(timestamp)
        postparams = {'subject': subject,
                      'event': post,
                      'security': 'private', #testing
                      'year': postdate.year,
                      'mon': postdate.month,
                      'day': postdate.day,
                      'hour': postdate.hour,
                      'min': postdate.minute,
                      'props': {'opt_backdated': False,
                                'opt_preformatted': True}
                     }
        postparams.update(self._challenge())
        out = self.server.LJ.XMLRPC.postevent(postparams)
        return out

if __name__ == "__main__":
    postdate = "2015-01-09T01:58:39Z"
    subject = "This is a test"
    server = "www.dreamwidth.org"
    username = "digitalraven"
    password = ""
    post = "<p>Did this one work?</p>"

    l = LiveJournal(server, username, password)
    l.post(subject, post, postdate)
