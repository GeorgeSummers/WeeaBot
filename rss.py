import feedparser
import json
import csv

# TODO buffer for new titles -> listening to feed -> delivery
# https://stackoverflow.com/questions/22211795/python-feedparser-how-can-i-check-for-new-rss-data


def get_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','a') as file:
        writer = csv.writer(file)
        writer.writerow((fd.feed.title, feed, fd.entries[0].published,f"{fd.feed.title}.json")) 
    with open (f"{fd.feed.title}.json",'w') as file:
        titles = []
        for item in fd.entries:
            titles.append({item['title'] : item['link']})
        json.dump(titles,file)
        file.truncate()

def upd_feed(feed):
    fd = feedparser.parse(feed)
    with open('datrss.csv','r+') as file:
        reader = csv.reader(file)
        writer=csv.writer(file)
        lines = list(reader)
        for row in lines:
            if row[1] == feed and row[2]!=fd.modified:
               row[2]=fd.entries[0].published      
               with open(row[3],'r+') as ff:
                    titles = []
                    for item in fd.entries:
                        if not item.published==row[2]:
                            titles.append({item['published'] : item['link']})
                        else: 
                            break
                    ff.seek(0)
                    ff.truncate()
                    json.dump(titles,ff)
                    ff.truncate()
        writer.writerows(lines)

def upd_ongoing(cmd,uid,titles):
    with open('subrss.json','r+') as fsub:
        data = json.load(fsub)
        for title in titles:
            if cmd == "del":
                try:
                    data[str(uid)][1].remove(title)
                except:
                    print('meh')
                    continue
            elif cmd == "add":
                data[str(uid)][1].append(title)

        fsub.seek(0)
        json.dump(data, fsub)
        fsub.truncate()

def listen():
    pass
