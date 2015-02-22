#! -*-coding: utf-8 -*-
import feedparser
import urllib
import urllib2
import re

import transmissionrpc
from BeautifulSoup import BeautifulSoup

userName = 'grf623BT'
passwd = '1234567'
tc = transmissionrpc.Client('localhost', port=9091, user=userName, password=passwd)

class rss_parser():
    def __init__(self):
        self.parser = feedparser.parse('http://share.popgo.org/rss/rss.xml')
    
    def print_all(self):
        print self.parser

    def print_feed(self):
        print self.parser.feed

    '''
        Can get magnet href
    '''
    def parse_entries(self):
        entries = self.parser.entries
        htmlRes = urllib.urlopen(entries[0].link).read()
        magnet = BeautifulSoup(htmlRes).find( name='a', attrs={'href': re.compile('magnet')} )
        print magnet['href']

        tc.add_torrent( magnet['href'] )

        '''
            Can use title to filter animation and attr i.e. BIG5, MP4
        '''
        '''
        for item in entries:
            print item.title, item.link
            fTitle = item.title.find('BIG5') 
            print fTitle
            '''

if __name__ == '__main__':
    rssParser = rss_parser()
    #rss.print_all()
    rssParser.parse_entries()
    pass
