#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import BeautifulSoup
import ClientCookie
import MySQLdb
import category
import dbpass

db = None
def connectDB():
    global db
    db = MySQLdb.connect('localhost', dbpass.id, dbpass.passwd, dbpass.dbname)
    db.query("set character_set_connection=utf8;")
    db.query("set character_set_server=utf8;")
    db.query("set character_set_client=utf8;")
    db.query("set character_set_results=utf8;")
    db.query("set character_set_database=utf8;")
    return db


def http_get( url ):
        request = urllib2.Request( url )
        request.add_header('Referer', url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13')
        #response = urllib2.urlopen(request)
        response = ClientCookie.urlopen(request)

        return response

url2 = 'http://www2.torrentrg.com/bbs/board.php?bo_table=torrent_movie&wr_id=292517'
url1 = 'http://www2.torrentrg.com/bbs/board.php?bo_table=torrent_movie'
url3 = 'http://www2.torrentrg.com/bbs/board.php?bo_table=torrent_variety'
url4 = 'http://www.torrentrg.com/bbs/board.php?bo_table=torrent_tv'
url5 = 'http://www.dakchigo.com/bbs/board.php?bo_table=movie'
url6 = 'http://www.hibogo.net/'

def tak(bbs):
    url = 'http://www.dakchigo.com/bbs/board.php?bo_table='+bbs
    communityID = 'tak_'+bbs
    html = http_get(url).read().decode('cp949').encode('utf-8')
    soup = BeautifulSoup.BeautifulSoup(html)
    articles = soup.findAll('nobr',attrs={'style':'display:block; overflow:hidden;'})
    for item in articles :
        article = item.find('a')
        link = article['href']
        text = article.contents[0]
        #print text
        if check_dup(communityID, link) :
            continue
        print link
        files = tak_get_file_metadata(link)

        for i in files:
            if i['type'] != 'unknown' :
                filedata = http_get(i['link']).read()
                r = db_insert_torrent(communityID, link, i['title'] , i['name'], filedata, i['type'])
                if r != -1 :
                    keywords = get_keyword(i['title'])
                    if bbs == 'movie':
                        keywords.append('movie')
                    for keyword in keywords:
                        db_insert_keyword(keyword,r)
        
def tak_get_file_metadata(url):
    base = 'http://www.dakchigo.com/bbs/'
    fullUrl = base+url
    html = http_get(fullUrl).read().decode('cp949').encode('utf-8')
    chunk = 'javascript:file_download(\''
    idx = html.find('<title>')
    html = html[idx+len('<title>'):]
    idx = html.find('토렌트')
    title = html[:idx].strip()
    #print title
    
    fileInfo = []
    idx = html.find(chunk)
    while idx != -1 :
        html = html[idx+len(chunk):]
        idx = html.find('\'')
        link = html[:idx]
        html = html[idx+1:]
        idx = html.find('\'')
        html = html[idx+1:]
        idx = html.find('\'')
        filename = html[:idx]

        ext = filename.split('.')[-1]
        if ext in ['torrent','TORRENT'] :
            filetype = 'torrent'
        elif ext in ['srt','smi','SRT','SMI']:
            filetype = 'sub'
        else :
            filetype = 'unknown'

        fileInfo.append({'title':title, 'link':base+link,'name':filename,'type':filetype})
        idx = html.find(chunk)

    return fileInfo
    

def trg(bbs):
    url = 'http://www2.torrentrg.com/bbs/board.php?bo_table='+bbs
    communityID = 'rg_'+bbs
    
    html = http_get(url).read().decode('cp949').encode('utf-8')
    #print html
    soup = BeautifulSoup.BeautifulSoup(html)
    articles = soup.findAll('td', attrs={'class':"mw_basic_list_subject"})
        for item in articles :
        article = item.findAll('a')
        if len(article) > 1 and bbs == 'torrent_movie':
            article = article[1]
        else:
            article = article[0]
        link = article['href']
        
        title = article.contents[0].contents[0]

        #need to check duplicaion
        if check_dup(communityID, link) :
            continue
        print link  
        #print title
        title = title+''
        title = title.encode('cp949').decode('cp949').encode('utf-8')
        keywords = get_keyword(title)
        if bbs == 'torrent_movie' :
            keywords.append('movie')
        #print keywords

        files = trg_get_file_metadata(link)
        resultRows = []
        for i in files:
            if i['type'] != 'unknown' :
                filedata = http_get(i['link']).read()
                r = db_insert_torrent(communityID, link,title , i['name'], filedata, i['type'])
                if r != -1 :
                    resultRows.append(r)
        #insert keyword
        for row in resultRows :
            for keyword in keywords :
                db_insert_keyword(keyword,row)
    

def trg_get_file_metadata(url):
    base = 'http://www2.torrentrg.com/bbs/'
    fullUrl = base+url
    html = http_get(fullUrl).read().decode('cp949').encode('utf-8')
    #<td class=mw_basic_view_subject>
    try:
        soup = BeautifulSoup.BeautifulSoup(html)
    except:
        return []
    #titleTag = soup.find('td',attrs={'class':'mw_basic_view_subject'})
    #title = titleTag.contents[0].strip()
    #title = title.split('         ')[1]
    #print title
    fileInfo = []
    downloadInfo = soup.findAll('td', attrs={'class':'mw_basic_view_file'})
    for item in downloadInfo:
        href = item.find('a')['href']
        idx = href.find('\'')
        href = href[idx+1:]
        idx = href.find('\'')
        link = href[:idx]
        href = href[idx+1:]
        idx = href.find('\'')
        href = href[idx+1:]
        idx = href.find('\'')
        filename = href[:idx]
        filename = filename.encode('utf-8')
        
        ext = filename.split('.')[-1]
        if ext in ['torrent','TORRENT'] :
            filetype = 'torrent'
        elif ext in ['srt','smi','SRT','SMI']:
            filetype = 'sub'
        else :
            filetype = 'unknown'

        fileInfo.append({'link':base+link,'name':filename,'type':filetype})
    return fileInfo
    
def get_keyword(title):
    filterList = ['avi','hdtv','mp4','mkv','xvid', 'the', 'a','ac3','x264','kor','tp','h264']
    keyword = []
    title = title.replace('.',' ').replace('-',' ').replace(',',' ').replace('"',' ').replace('[',' ').replace(']',' ').replace('/',' ').replace('#','')
    title = title.replace('(',' ').replace(')',' ').replace('!',' ').replace('\'',' ').replace('_',' ').replace('~',' ').replace('+',' ').replace('&',' ')
    title = title.replace(':',' ')
    splitSpace = title.split()
    for word in splitSpace :
        word = word.lower()
        if not word in filterList and len(word) > 0 :
            keyword.append(word)
    return keyword

def check_dup(cid, link):
    cur = db.cursor()
    r = cur.execute('select * from torrent where community like %s and link like %s', (cid,link))
    return r > 0

def db_insert_torrent(comm , link , title, filename, data , filetype ) :
    cur = db.cursor()
    r = cur.execute("insert into torrent (community,link,title,filename,data,filetype) values ( %s, %s, %s, %s, %s, %s)",(comm, link , title, filename, data, filetype))
    if r > 0 :
        rowid = cur.lastrowid
    else:
        rowid = -1
    cur.close()
    return rowid

def db_get_keyword_id(keyword):
    cur = db.cursor()
    r = cur.execute("select no from torrent_keyword where value = %s", (keyword,))
    keyId = 0
    if r > 0 :
        keyId = cur.fetchone()[0]
    else:
        r = cur.execute("insert into torrent_keyword (value) values ( %s )", (keyword,))
        keyId = cur.lastrowid
    cur.close()
    return keyId

def db_insert_keyword(keyword, torrentId) :
    keyId = db_get_keyword_id(keyword)
    cur = db.cursor()
    r = cur.execute("insert into torrent_keyword_map (keyword,torrent_id) values ( %s,%s )", (keyId, torrentId))
    cur.close()


if __name__ == '__main__':
    connectDB()
    tak('movie')
    tak('kortv')
    tak('fortv')
    tak('ani')
    trg('torrent_variety')
    trg('torrent_movie')
    trg('torrent_tv')
    category.update()
    print 'done'
    #print http_get('http://www.dakchigo.com/bbs/board.php?bo_table=movie&wr_id=11090').read().decode('cp949').encode('utf-8')
