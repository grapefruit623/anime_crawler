#! -*-coding: utf-8 -*-
import os
import re
import urllib

import feedparser
import transmissionrpc
import time

from BeautifulSoup import BeautifulSoup

userName = 'BT'
passwd = '1234567'

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; windows NT)'
header = { 'User-Agent': user_agent }

class rss_parser():
    def __init__(self):
        self.parser = feedparser.parse('http://share.popgo.org/rss/rss.xml')
        self.keywordList = self.get_targetList()
        self.get_parseCondition()

        if self.open_transmissionClient():  # Father will add torent
            time.sleep(3)
            self.tc = transmissionrpc.Client('localhost', port=9091,
                                             user=userName, password=passwd)
            self.timerForSearch()

    def __del__(self):
        print '__del__'

    def get_targetList(self):
        f = open('targetList.txt', 'r')
        d = f.readlines()
        f.close()
        target = set([])
        for keyword in d:
            aAnimation = keyword.rstrip()
            target.add(aAnimation)
        return target


    def timerForSearch(self):
        while 0 != len(self.regexList):
            self.parse_entries()
            time.sleep(1800)
            print 'Not finish'
        print 'finish!'

    '''
        pasre Animation's name, episode, coding to regex condition 
        ToDo:
            To filter RAW files
    '''
    def get_parseCondition(self):
        self.regexList = set([]) 
        pattern = u'(?=.*{0})'
        for anim in self.keywordList:
            regex = ''
            for condition in anim.split(','):
                regex += pattern.format(unicode(condition, 'utf8'))

            regex += '.*'
            self.regexList.add( regex )



    '''
        Can get magnet href
        We must be check whether transmission is launched?
    '''
    def parse_entries(self):
        entries = self.parser.entries
        '''
            Can use title to filter animation and attr i.e. BIG5, MP4
            Why sometimes variable magnet is NoneType??
        '''
        print self.regexList
        for item in entries:
            print item.title
            for regex in self.regexList:
                # u'' is meaning? unicode!!, re.MULTILINE is meaning?
                if None != re.search(re.compile(regex, re.MULTILINE),
                                     item.title):
                    htmlRes = urllib.urlopen(item.link, None, header)
                    print htmlRes.getcode()
                    magnet = BeautifulSoup(htmlRes.read()).find(href=re.compile(u'magnet'))
                    print magnet
                    self.tc.add_torrent(magnet['href'])
                    '''
                        Why removimg action will fail???
                    '''
                    self.regexList.remove( regex )
                    break

            if not self.regexList: # All animation are downloading
                return
    '''
        must be mult thresad
    '''
    def open_transmissionClient(self):
        pid = os.fork()
        if 0 == pid:
            print 'child launch transmission-gtk'
            os.system('transmission-gtk')
            return 0
        else:
            print 'father pid: ', pid
            return 1

if __name__ == '__main__':
    rssParser = rss_parser()
    # rss.print_all()
    # rssParser.open_transmissionClient()
    # rssParser.parse_entries()
    print '__main__'
