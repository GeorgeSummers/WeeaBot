import feedparser
import weeabot
import sched, time
import json
import csv

# https://stackoverflow.com/questions/22211795/python-feedparser-how-can-i-check-for-new-rss-data

def get_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','a',newline="") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow((fd.feed.title, feed, fd.entries[0].published,f"{fd.feed.title}.json")) 
    with open (f"{fd.feed.title}.json",'w') as file:
        titles = []
        for item in fd.entries:
            titles.append({item['title'] : item['link']})
        json.dump(titles,file)
        file.truncate()

def upd_feeds(sc):
    with open('datrss.csv','r+',newline="") as file:
        reader = csv.reader(file)
        writer=csv.writer(file, delimiter=',')
        lines = list(reader)
        for row in lines:
            fd = feedparser.parse(row[1])
            if row[2]!=fd.entries[0].published:      
               with open(row[3],'r+') as ff:
                   titles = []
                   for item in fd.entries:
                       if not item.published==row[2]:
                           titles.append({item['title'] : item['link']})
                       else: 
                           break
                   ff.seek(0)
                   ff.truncate()
                   json.dump(titles,ff)
                   ff.truncate()
               weeabot.notify()
            row[2]=fd.entries[0].published
        file.seek(0)
        file.truncate()
        writer.writerows(lines)
        sc.enter(1800,1,upd_feeds,(sc,))

def upd_ongoing(cmd,uid,titles):
    with open('subrss.json','r+') as fsub:
        data = json.load(fsub)
        for title in titles:
            if cmd == "del":
                try:
                    data[str(uid)][0].remove(title)
                except:
                    continue
            elif cmd == "add":
                data[str(uid)][0].append(title)
                data[str(uid)][0] = sorted(data[str(uid)][0])

        fsub.seek(0)
        json.dump(data, fsub)
        fsub.truncate()

def listen():
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1800,1,upd_feeds,(s,))
    s.run()