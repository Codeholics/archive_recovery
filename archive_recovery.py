#!/usr/bin/python3

'''Parse archived html files and import them into a
   wordpress database
   
   Notes:

   with open(‘[html file]’) as html:
       page = BeautifulSoup(html, ‘html.parser’)
   page.title - title tag
   page.find('div', {'class': 'td-post-content'}) - find post content
   page.find('div', {'class': 'td-post-content'}).find_all(‘p’) - only get array of paragraphs - ALL POST TEXT'''
import os
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, BigInteger, DateTime, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
#Post Object
class Post(Base):
    '''wpcp_posts table schema object'''
    #__tablename__ = 'wpcp_posts'
    __tablename__ = 'wp_posts'

    ID = Column(BigInteger, primary_key=True)
    post_author = Column(BigInteger, default=0)
    post_date = Column(DateTime, default='0000-00-00 00:00:00')
    post_date_gmt = Column(DateTime, default='0000-00-00 00:00:00')
    post_content = Column(String, default=None)
    post_title = Column(String, default=None)
    post_excerpt = Column(String, default='')
    post_status = Column(String, default='publish')
    comment_status = Column(String, default='open')
    ping_status = Column(String, default='open')
    post_password = Column(String, default='')
    post_name = Column(String, default='')
    to_ping = Column(String, default='')
    pinged = Column(String, default='')
    post_modified = Column(DateTime, default='0000-00-00 00:00:00') 
    post_modified_gmt = Column(DateTime, default='0000-00-00 00:00:00')
    post_content_filtered = Column(String, default='')
    post_parent = Column(BigInteger, default=0)
    guid = Column(String, default='')
    menu_order = Column(Integer, default=0)
    post_type = Column(String, default='post')
    post_mime_type = Column(String, default='')
    comment_count = Column(BigInteger, default=0)

    def __repr__(self):
        return "<Post(post_author='%s', post_date='%s', post_date_gmt='%s', \
                post_content='%s', post_title='%s', post_excerpt='%s', post_status='%s', \
                comment_status='%s', ping_status='%s', post_password='%s', post_name='%s', \
                to_ping='%s', pinged='%s', post_modified='%s', post_modified_gmt='%s', \
                post_content_filtered='%s', post_parent='%s', guid='%s', menu_order='%s' \
                post_type='%s', post_mime_type='%s', comment_count='%s')>" % \
                (self.post_author, self.post_date, self.post_date_gmt, self.post_content,
                 self.post_title, self.post_excerpt, self.post_status, self.comment_status,
                 self.ping_status, self.post_password, self.post_name, self.to_ping,
                 self.pinged, self.post_modified, self.post_modified_gmt,
                 self.post_content_filtered, self.post_parent, self.guid, self.menu_order,
                 self.post_type, self.post_mime_type, self.comment_count)

def main():
    # Path with wp post html files
    path='./posts'
    # SQLAlchemy Setup
    engine = create_engine('mysql://root@localhost/codeholics_wpdevel', echo=True)
    Session = sessionmaker(bind=engine)
    db_conn = Session()

    # list path html files and import them
    for html_page in os.scandir(path):
        # Beautiful Soup Setup (open html page)
        with open(os.path.abspath(os.path.join(path, html_page.name))) as html:
            page = BeautifulSoup(html, 'html.parser')

        # Title
        title = page.find('h1', {'class': 'entry-title'})
        # Permalink
        post_name = page.find('link', {'rel':'canonical'})['href'].split('/')[-2]
        # post timestamp
        #datetime.strptime('2016-04-14T19:57:39+00:00', '%Y-%m-%dT%H:%M:%S+00:00')
        timestamp = datetime.strptime(page.find('time').get('datetime'),
                                     '%Y-%m-%dT%H:%M:%S+00:00')
        # build content from p tags in td-post-conent
        content = ''
        for x in page.find('div', {'class': 'td-post-content'}).find_all('p'):
            #content += x.text
            content += x.prettify()
        # create post object
        post = Post(post_title=title.string,
                    post_author=1,
                    post_content=content,
                    #post_excerpt=content[:120:],
                    post_name=post_name,
                    post_date=timestamp,
                    post_date_gmt=timestamp)
        # insert into database
        try:
            db_conn.add(post)
            db_conn.commit()
        except Exception:
            raise

    db_conn.flush()
    db_conn.close()

if __name__ == '__main__':
    main()
