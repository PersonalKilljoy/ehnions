import sys
import getopt
import re
import hashlib
# in python3 urllib2 is divided into 2 different libs
# import urllib2
# from requests.auth import HTTPBasicAuth  # apt-get install python-requests
import requests
import MySQLdb  # apt-get install python-MySQLdb
import socket
import socks  # socksipy
from BeautifulSoup import BeautifulSoup
from util import DataBs

bufsize = 0
PAGE_HASH = 'acbc159c7062332360bcd792ff9c6e294cb32ec3a5b87577e25da36117518b172f2c77c59c1a9bb18f8d905d1f67eeab9cca217990f23828444c2c9aff865e0b'
SOCKS_PORT = 9050
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT, True)
socket.setdefaulttimeout(200)
socket.socket = socks.socksocket
socket.getaddrinfo = lambda *x: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', x)]

# Scanning, or loading new onions?
inputfile = ''


def main():
    try:
        cl_options, cl_args = getopt.getopt(sys.argv[1:], "i:")
        for option, arg in cl_options:
            if option == '-i':
                inputfile = arg
                load_onions(inputfile)
            else:
                print("Usage: %s -i onionlist" % sys.argv[0])
                print("onionlost MUST CONTAIN one onion per line, without the .onion in the address")
                print("Use no arguments to run the standard onion scan")
        onion_scan()
    except IOError as e:
        print ("Error opening file: {0}".format(e.strerror))
    except MySQLdb.Error as err:
        print ("Error opening Database: {0}".format(err.strerror))
    except:
        print ("Unknown exception")


def fetch_hs(addr):
    try:
        # password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        # password_mgr.add_password(None, addr, 'user', 'password')
        # handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        # opener = urllib.request.build_opener(handler)
        # urllib._urlopener = opener
        print('Trying to retrieve address')
        response = requests.get(addr)  # urllib2.urlopen(addr)  # , urlencode({'user': 'user', 'password':'pass'})
        print(response.request.headers)
        print(response.headers)
        print('Opened URL')
        document = response.content
        # print(response.content)
        # print(document)
        return document
    except Exception as e:
        print(e)
        print("cannot reach address\n")
        print("----------------------")
        return "unreachable"


def test_hash(s):
    sha = hashlib.sha512(s).hexdigest()
    # print 'Hash(' + str(len(s)) +") = ",sha
    if sha == PAGE_HASH:
        print("MATCH", s)
        exit()
    return sha


def load_onions(inputfile):
    regex = re.compile("([a-z2-7]){16}")
    try:
        with DataBs as db:
            try:
                print('Opening File %s ...' % inputfile)
                onion_addrs = ''
                with open(inputfile, "r+") as onionlist:
                    print('file opened successfully')
                    onion_addrs = onionlist.readlines()
                for onion_addr in onion_addrs:
                    if regex.match(onion_addr):
                        data_onion = (onion_addr, inputfile)
                        db.add_onion(data_onion)
            except:
                print("Error opening " .inputfile)
    except MySQLdb.Error as err:  # initializer exception
        print(err)


def onion_scan():
    try:
        with DataBs as db:
            try:
                print('Querying...')
                for onion_addr in db.select_scannable():
                    db.add_onion_scan(parseOnion(onion_addr[0]))
            except Exception as e:
                print(e)
                print("Error opening " .inputfile)
    except MySQLdb.Error as err:  # initializer exception
        print(err)


def parseOnion(url):
    print("----------------------")
    onionurl = "http://" + url + ".onion"
    print("Parsing: " + onionurl)
    contents = fetch_hs(onionurl)
    if contents != "unreachable":
        contenthash = test_hash(contents)
        print("Success")
        parsedcontents = contents
        try:
            parsedcontents = BeautifulSoup(contents)
        except:
            parsedcontents = contents
        pagetitle = ""
        if (parsedcontents.title is None) or (parsedcontents.title == ""):  # | (parsedcontents.title.string=="") | (parsedcontents.title.string is None):
            pagetitle = ""
        else:
            pagetitle = parsedcontents.title.string
            # (  print pagetitle.encode('utf-8'))
        data_onionscan = (
            url,
            'true',
            contents,
            pagetitle,
            contenthash)
        print(data_onionscan)
    else:
        print("Content unreachable")
        data_onionscan = (
            url,
            'false',
            contents, '', '')
        print(data_onionscan)
    return data_onionscan


main()
# parsePage("fvtddif4bucpdsxx")

# The reason that http://fvtddif4bucpdsxx.onion is simple - urllib2 doesnt have
# connection keep-alive, only close and i assume that this is the reason for
# this specific onion not to send the page. Requests use urllib3 which has
# keep-alive option and which is used by default in Requests
