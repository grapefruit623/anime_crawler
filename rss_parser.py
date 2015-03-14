#! -*-coding: utf-8 -*-
import os
import re
import urllib

import feedparser
import transmissionrpc
import time

from BeautifulSoup import BeautifulSoup

userName = 'grf623BT'
passwd = '1234567'

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; windows NT)'
header = { 'User-Agent': user_agent }

class rss_parser():
    def __init__(self):
        self.parser = feedparser.parse('http://share.popgo.org/rss/rss.xml')
        self.keywordList = self.get_targetList()

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
        target = []
        for keyword in d:
            aAnimation = keyword.rstrip()
            target.append([aAnimation, False])
        return target

    def timerForSearch(self):
        while not self.parse_entries():
            print 'Not found'
            time.sleep(1800)
        print 'Found it!'

    '''
        pasre Animation's name, episode, coding to regex condition 
    '''
    def get_parseCondition(self):
        regex = ''
        pattern = u'(?=.*{0})'
        for anim in self.keywordList:
            for condition in anim[0].split(','):
                regex += pattern.format(unicode(condition, 'utf8'))

        regex += '.*'
        return regex


    '''
        Can get magnet href
        We must be check whether transmission is launched?
    '''
    def parse_entries(self):
        entries = self.parser.entries
        self.get_parseCondition()
        '''
            Can use title to filter animation and attr i.e. BIG5, MP4
        '''
        for item in entries:
            # u'' is meaning? unicode!!, re.MULTILINE is meaning?
            regex = self.get_parseCondition()
            if None != re.search(re.compile(regex, re.MULTILINE),
                                 item.title):
                print item.title
                print item.link
                htmlRes = urllib.urlopen(item.link, None, header)
                print htmlRes.getcode()
                '''
                Why this fail?

                magnet = BeautifulSoup(htmlRes.read()).find(name='a',
                                                     attrs={'href': re.compile(u'magnet')})
                '''
                '''
                Why this fail?
                magnet = BeautifulSoup(htmlRes.read()).find_all(name='a')
                '''
                magnet = BeautifulSoup(htmlRes.read()).find(href=re.compile('magnet'))
                print magnet
                self.tc.add_torrent(magnet['href'])
                return True
        return False

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
