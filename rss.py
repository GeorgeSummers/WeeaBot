import feedparser
import json
import csv
# TODO get_feed->enlist title dict -> get data -> check upds
# https://stackoverflow.com/questions/22211795/python-feedparser-how-can-i-check-for-new-rss-data


def get_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','a') as file:
        writer = csv.writer(file)
        writer.writerow((fd.feed.title, feed, fd.modified,f"{fd.feed.title}.json")) 
    with open (f"{fd.feed.title}.json",'w') as file:
        # TODO fill feedfile
        pass
    

def upd_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','r+') as file:
        reader = csv.reader(file)
        writer=csv.writer(file)
        for row in reader:
            if row[1] == feed and row[2]!=fd.modified:
                row[2]=fd.modified
                # TODO rewrite json

def updlist(uid):
    pass


def listen():
    pass

get_feed('https://ru.erai-raws.info/rss-1080/')