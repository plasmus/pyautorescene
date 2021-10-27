import pickle
import datetime
import os
from urllib.parse import urlparse
import requests

class SRRDB_LOGIN:
    """
	https://stackoverflow.com/questions/12737740/python-requests-and-persistent-sessions
    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintine a cache-file for restoring session data from earlier
    script executions.
    """
    def __init__(self,
                 loginUrl,
                 loginData,
                 loginTestUrl,
                 loginTestString,
                 sessionFileAppendix = "_session.dat",
                 maxSessionTimeSeconds = 30 * 60,
                 proxies = None,
                 userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
                 debug = False,
                 forceLogin = False,
                 **kwargs):
        """
        save some information needed to login the session

        you'll have to provide 'loginTestString' which will be looked for in the
        responses html to make sure, you've properly been logged in

        'proxies' is of format { 'https' : 'https://user:pass@server:port', 'http' : ...
        'loginData' will be sent as post data (dictionary of id : value).
        'maxSessionTimeSeconds' will be used to determine when to re-login.
        """
        urlData = urlparse(loginUrl)

        self.proxies = proxies
        self.loginData = loginData
        self.loginUrl = loginUrl
        self.loginTestUrl = loginTestUrl
        self.maxSessionTime = maxSessionTimeSeconds
        self.sessionFile = urlData.netloc + sessionFileAppendix
        self.userAgent = userAgent
        self.loginTestString = loginTestString
        self.debug = debug

        self.login(forceLogin, **kwargs)

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def login(self, forceLogin = False, **kwargs):
        wasReadFromCache = False
        if self.debug:
            print("\n\t - Loading or generating session...")
        if os.path.exists(self.sessionFile) and not forceLogin:
            time = self.modification_date(self.sessionFile)         

            # only load if file less than 30 minutes old
            lastModification = (datetime.datetime.now() - time).seconds
            if lastModification < self.maxSessionTime:
                with open(self.sessionFile, 'rb') as f:
                    self.session = pickle.load(f)
                    wasReadFromCache = True
                    if self.debug:
                        print("\t - Loaded session from cache (last access %ds ago)" % lastModification, end="")
        if not wasReadFromCache:
            self.session = requests.Session()
            self.session.headers.update({"user-agent" : self.userAgent})
            res = self.session.post(self.loginUrl, data = self.loginData, proxies = self.proxies, **kwargs)

            if self.debug:
                print("\t - Created new session with login")
            self.saveSessionToCache()

        # test login
        res = self.session.get(self.loginTestUrl)
        if res.text.lower().find(self.loginTestString.lower()) < 0:
            raise ValueError("Could not log into provided site '%s' (did not find successful login string)" % self.loginUrl, end="")

    def saveSessionToCache(self):
        # always save (to update timeout)
        with open(self.sessionFile, "wb") as f:
            pickle.dump(self.session, f)
            if self.debug:
                print("\n\t - Updated session cache-file %s " % self.sessionFile, end="")

    def retrieveContent(self, url, method = "get", postData = None, **kwargs):
        if method == 'get':
            res = self.session.get(url , proxies = self.proxies, **kwargs)
        else:
            res = self.session.post(url , data = postData, proxies = self.proxies, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.saveSessionToCache()

        return res