#! -*-coding: utf-8 -*-
import os
import re
import urllib
import json

import feedparser
import transmissionrpc
import time

# from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; windows NT)'
header = { 'User-Agent': user_agent }

userName = 'BT'
passwd = '1234567'

'''
    Transmission unit
'''
class transmissionInst():

    def __init__(self):
        return self.getTransmissionClient()

    def openTransmissionClient(self):
        pid = os.fork()
        if 0 == pid:
            print ('child launch transmission-gtk')
            os.system('transmission-gtk')
            return 0
        else:
            print ('father pid: ', pid)
            return 1

    def getTransmissionClient(self):
        if self.openTransmissionClient():  # Father will add torent
            time.sleep(3)
            tc = transmissionrpc.Client('localhost', port=9091,
                                             user=userName, password=passwd)
            return tc


class rss_parser():

    def __init__(self):
        self.parser = feedparser.parse('http://share.popgo.org/rss/rss.xml')
        self.keywordList = self.get_targetList()
        self.get_parseCondition()
        self.tc = transmissionInst()

    def __del__(self):
        print ('__del__')

    '''
        .json format
    '''
    def get_targetList(self):
        f = open('targetList.json', 'r')
        j = json.load(f)
        f.close()
        return j


    def checkRSS(self):
        while 0 < len(self.regexList):
            self.parser = feedparser.parse('http://share.popgo.org/rss/rss.xml')
            self.parse_entries()
            print ('Not finish')
            time.sleep(600)
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
            regex = pattern.format(anim) 
            condition = self.keywordList[anim]
            for keyword in condition.values():
                regex += pattern.format(keyword)

            self.regexList.add(regex)

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
            for regex in self.regexList:
                # u'' is meaning? unicode!!, re.MULTILINE is meaning?
                if None != re.search(re.compile(regex, re.MULTILINE | re.IGNORECASE),
                                     item.title):
                    htmlRes = urllib.urlopen(item.link, None, header)
                    # print htmlRes.read()
                    # magnet = BeautifulSoup(htmlRes.read()).find(href=re.compile(u'magnet'))
                    magnet = BeautifulSoup(htmlRes.read()).find('a', href=re.compile(u'magnet'))
                    # print magnet
                    # print magnet.attrs
                    self.tc.add_torrent(magnet['href'])
                    self.regexList.remove( regex )
                    break

            if not self.regexList: # All animation are downloading
                return

if __name__ == '__main__':
    rssParser = rss_parser()
    rssParser.checkRSS()
    print ('__main__')
