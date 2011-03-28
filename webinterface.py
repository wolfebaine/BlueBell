#!/usr/bin/env python

import sys
import hashlib
import cyclone.web
import peewee
from twisted.python import log
from twisted.internet import defer, reactor

database = peewee.Database(peewee.SqliteAdapter(), 'BlueBell.db')

class Webuser(peewee.Model):
    id = peewee.PrimaryKeyField()
    username = peewee.CharField()
    salt = peewee.CharField()
    pwhash = peewee.CharField()
    class Meta:
        db_table = 'webusers'
        database = database

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.write('Welcome, %s <a href="/auth/logout">logout</a>' % (self.current_user))

class LoginHandler(BaseHandler):
    def get(self):
        err = self.get_argument("e", None)
        self.write("""
            <html><body><form action="/auth/login" method="post">
            username: <input type="text" name="u"><br>
            password: <input type="password" name="p"><br>
            <input type="submit" value="sign in"><br>
            %s
            </body></html>
        """ % (err == "invalid" and "invalid username or password" or ""))

    def post(self):
        u, p = self.get_argument("u"), self.get_argument("p")
        database.connect()
        try:
            user = Webuser.get(username=u)
        except StopIteration:
            self.redirect("/auth/login?e=invalid")
        else:
            pwhash_to_test = hashlib.sha256(p + user.salt).hexdigest()
            if pwhash_to_test == user.pwhash:
                self.set_secure_cookie("user", str(user.username))
                self.redirect("/")
            else:
                self.redirect("/auth/login?e=invalid")
        database.close()

class LogoutHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

class Application(cyclone.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/auth/login", LoginHandler),
            (r"/auth/logout", LogoutHandler),
        ]
        settings = dict(
            login_url="/auth/login",
            cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        )
        cyclone.web.Application.__init__(self, handlers, **settings)

def main(port):
    reactor.listenTCP(port, Application())
    reactor.run()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    main(8888)