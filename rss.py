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
        titles =[]
        for item in fd.entries:
            titles.append({item['title'] : item['link']})
        json.dump(titles,file)
        file.truncate()

def upd_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','r+') as file:
        reader = csv.reader(file)
        writer=csv.writer(file)
        for row in reader:
            if row[1] == feed and row[2]!=fd.modified:
                row[2]=fd.modified
                with open(row[3],'r+') as ff:
                    ff.seek(0)
                    ff.truncate()
                    titles =[]
                    for item in fd.entries:
                        titles.append({item['title'] : item['link']})
                    json.dump(titles,file)
                    file.truncate()

def updlist(uid):
    pass


def listen():
    pass

get_feed('https://ru.erai-raws.info/rss-1080/')