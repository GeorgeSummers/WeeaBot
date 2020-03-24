import feedparser
import weeabot
import time
import json
import csv


def get_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','a',newline="") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow((fd.feed.title, feed, fd.entries[0].published,fd.entries[0].published)) 
    with open (f"{fd.feed.title}.json",'w') as file:
        titles = []
        for item in fd.entries:
            titles.append({item['title'] : item['link']})
        json.dump(titles,file)
        file.truncate()
    return fd.feed.title

def upd_feeds():
    with open('datrss.csv','r+',newline="") as file:
        reader = csv.reader(file)
        writer=csv.writer(file, delimiter=',')
        lines = list(reader)
        check= False
        for row in lines:
            fd = feedparser.parse(row[1])
            if not row[2] == fd.entries[0].published:   
               check = True   
               with open(f'{row[0]}.json','r+') as ff:
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
               row[2]=fd.entries[0].published
        if check:
            weeabot.notify()
        file.seek(0)
        file.truncate()
        newlines=[x for x in lines if x != []]
        writer.writerows(newlines)

def upd_data(cmd,uid,titles):
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
            elif cmd == 'sub':                  #feck
                data[str(uid)][1].append(title)
            elif cmd == 'unsub':
                try:
                    data[str(uid)][1].remove(f'{title} RSS')
                except:
                    continue

        fsub.seek(0)
        json.dump(data, fsub)
        fsub.truncate()

def listen():
    start_time=time.time()
    while True:
        upd_feeds()
        time.sleep(1800.0 - ((time.time()-start_time) % 1800.0))