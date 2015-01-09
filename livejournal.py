import xmlrpclib
import dateutil.parser
try:
    from hashlib import md5
except:
    import md5 as _md5
    md5 = _md5.new


class livejournal:
    def __init__(self, server, username, password):
        sname = "http://" + server + "/interface/xmlrpc"
        self.server = xmlrpclib.ServerProxy(sname)
        self.user = username
        self.password = password
    
    def challenge(self):
        challenge = self.server.LJ.XMLRPC.getchallenge()
        params = {'username': self.user,
                  'ver': '1',
                  'auth_method': 'challenge',
                  'auth_challenge': challenge['challenge'],
                  'auth_response': self.calcchallenge(challenge['challenge'],self.password)}
        return params

    def calcchallenge(self, challenge, password):
        return md5(challenge + md5(password).hexdigest()).hexdigest()

    def post(self, subject, post, timestamp):
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
        postparams.update(self.challenge())
        print postparams
        out = self.server.LJ.XMLRPC.postevent(postparams)
        return out

if __name__ == "__main__":
    postdate = "2015-01-09T01:58:38.269Z"
    subject = "This is a test"
    server = "www.dreamwidth.org"
    username = "digitalraven"
    password = ""
    post = "<p>Did this work?</p>"

    l = LiveJournal(server, username, password)
    l.post(subject, post, postdate)
