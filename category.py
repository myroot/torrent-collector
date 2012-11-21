#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import BeautifulSoup
import ClientCookie
import MySQLdb
import dbpass

db = None
def connectDB():
    global db
    if db != None :
        return db
    db = MySQLdb.connect('localhost', dbpass.id, dbpass.passwd, dbpass.dbname)
    db.query("set character_set_connection=utf8;")
    db.query("set character_set_server=utf8;")
    db.query("set character_set_client=utf8;")
    db.query("set character_set_results=utf8;")
    db.query("set character_set_database=utf8;")
    return db

def update ():
    db = connectDB()
    cur = db.cursor()
    r = cur.execute("select * from torrent where `group` = 0 order by no asc")
    r = cur.fetchall()
    for record in r :
        print record[0],
        cur.execute("SELECT * FROM `torrent_keyword_map` as a join ( select * from torrent_keyword ) as b on a.keyword=b.no where a.torrent_id = %s",(record[0],))
        keys = cur.fetchall()
        keywords = []
        for keyword in keys:
            if keyword[5] == 0 and isKeyword(keyword[4]) :
                #print keyword[4],
                keywords.append(keyword[4])
        #print ''
        keywords = set(keywords)
        cur.execute("select * from torrent_group")
        groups = cur.fetchall()
        for group in groups :
            groupKeys = group[2].split(',')
            groupKeys = set(groupKeys)
            if groupKeys == set([]):
                continue
            if keywords == groupKeys :
                print 'same group'
                cur.execute("update torrent_group set title = %s,`update` = CURRENT_TIMESTAMP,count = count+1 where no = %s",(record[3],group[0]))
                updateGroupMap(record[0],group[0])
                break
        else:
            print 'create group'
            keywordsql = ','.join(keywords)
            cur.execute("insert into torrent_group ( `title`, `keywords` ) values ( %s , %s )",(record[3],keywordsql))  
            gid = cur.lastrowid
            updateGroupMap(record[0],gid)

def updateGroupMap(torrentid , groupid):
    db = connectDB()
    cur = db.cursor()
    cur.execute("insert into torrent_group_map ( group_id , torrent_id ) values ( %s, %s)", (groupid,torrentid))
    cur.execute("update torrent set `group` = %s where no = %s",(groupid,torrentid))
    cur.close()

def isKeyword(keyword):
    keyword = keyword.replace('#','').replace('_','').replace('…','')
    test = keyword.lower().replace('ep','').replace('e','').replace('s','').replace('기','').replace('p','')
    if test.isdigit() :
        return False
    test = keyword.replace('화','').replace('회','').replace('편','').replace('부','').replace('제','')
    if test.isdigit() :
        return False
    return True
    
def test():
    db = connectDB()
    cur = db.cursor()
    cur.execute("select * from torrent_group")
    r = cur.fetchall()
    for d in r:
        print d[0]
        cnt = cur.execute("select * from torrent_group_map where group_id = %s",(d[0],))
        cur.execute("update torrent_group set `count` = %s where no = %s",(cnt,d[0]))
        

if __name__ =='__main__':
    #connectDB()
    update()
