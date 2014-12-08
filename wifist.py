# The MIT License (MIT)
#
# Copyright (c) 2014 Jean Dupouy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
A simple script to reconnect to Wifirst.

Copyright (c) 2014 Jean Dupouy. All Rights Reserved.
"""

import argparse
import cookielib
import logging
import lxml.html
import signal
import sys
import time
import urllib
import urllib2

__author__     = "Jean Dupouy"
__version__    = "0.1.0"

USER_AGENT     = 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
TEST_URL       = 'http://example.com/'
TOKEN_URL      = 'https://selfcare.wifirst.net/sessions/new'
SESSION_URL    = 'https://selfcare.wifirst.net/sessions'
LOGIN_URL      = 'https://connect.wifirst.net/?perform=true'
REQUEST_URL    = 'https://wireless.wifirst.net:8090/goform/HtmlLoginRequest'
SUCCESS_URL    = 'https://apps.wifirst.net/?redirected=true'
ERROR_URL      = 'https://connect.wifirst.net/login_error'

TOKEN_XPATH    = '//input[@name=\'authenticity_token\']/@value'
USERNAME_XPATH = '//input[@name=\'username\']/@value'
PASSWORD_XPATH = '//input[@name=\'password\']/@value'

signal.signal(signal.SIGINT, lambda s, f: sys.exit())

logger  = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

cookies = cookielib.CookieJar()

crawler = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
crawler.addheaders = [('User-Agent', USER_AGENT)]

def main(login, password, delay):
  logger.info("Press Ctrl+C to stop")
  logger.info("")

  while 1:
    if test():
      logger.info("Wifirst is not blocking the connection.")
    else:
      logger.info("Wifirst is blocking the connection! (for now)")

      if reconnect(login, password):
        logger.info("Connection successful! :)")
        logger.info("I will keep checking every %ss, though", delay)
      else:
        logger.info("Connection failed... :(")

    logger.debug("Trying again in %ss.", delay)
    time.sleep(delay)

def test():
  logger.debug("Testing connection...")

  response = crawler.open(TEST_URL)

  return response.geturl() == TEST_URL

def reconnect(login, password):
  token = fetch_token()

  return authenticate(login, password, token)

def fetch_token():
  logger.info("Authenticating (1/4)...")
  logger.debug("Fetching a token...")

  response = crawler.open(TOKEN_URL)
  tree     = lxml.html.parse(response)
  token    = tree.xpath(TOKEN_XPATH)[0]

  logger.debug("Token: %s", token)

  return token

def authenticate(login, password, token):
  logger.info("Authenticating (2/4)...")
  logger.debug("Creating a session...")

  crawler.open(SESSION_URL, urllib.urlencode({
    'login': login,
    'password': password,
    'authenticity_token': token
  }))

  logger.info("Authenticating (3/4)...")
  logger.debug("Fetching temporary ids...")

  response = crawler.open(LOGIN_URL)
  tree     = lxml.html.parse(response)
  username = tree.xpath(USERNAME_XPATH)[0]
  tmp_pass = tree.xpath(PASSWORD_XPATH)[0]

  logger.debug("Username: %s", username)
  logger.debug("Password: %s", tmp_pass)

  logger.info("Authenticating (4/4)...")
  logger.debug("Signing in...")

  response = crawler.open(REQUEST_URL, urllib.urlencode({
    'username': username,
    'password': tmp_pass,
    'qos_class': 0,
    'success_url': SUCCESS_URL,
    'error_url': ERROR_URL
  }))

  return response.geturl() == SUCCESS_URL

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="A simple script to reconnect to Wifirst.")
  parser.add_argument('login', help='your Wifirst login (e-mail address)')
  parser.add_argument('password', help='your Wifirst password')
  parser.add_argument('-v', '--verbose', action='store_true', help='make me say stuff')
  parser.add_argument('-d', '--delay', type=int, default=10, help='delay between attempts, in seconds (default: 10)')

  args = parser.parse_args()

  if args.verbose:
    logger.setLevel(logging.DEBUG)

  main(args.login, args.password, args.delay)
