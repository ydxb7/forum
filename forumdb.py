#
# Database access functions for the web forum.
# 

import time
import mysql.connector

## Database connection
# DB = []

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    mydb = mysql.connector.connect(
      host="localhost",
      user="learner",
      passwd="abcd1234",
      database="forum"
    )
    c = mydb.cursor()
    c.execute("update posts set content = 'cheese' where content like '%spam%'")
    c.execute("delete from posts where content = 'cheese'")
    query = '''select posts.time, content, username, touxiang, post_id, reply_to_id from posts join users 
    on posts.user_id = users.id order by time desc'''
    c.execute(query)
    
    DB = c.fetchall()
    
    #print "db", DB
    posts = [{'content': str(row[1]), 'time': str(row[0]), 'username': str(row[2]), 
              'touxiang': str(row[3]), 'post_id': row[4], 'reply_id': row[5]} for row in DB]
    #print "posts: ", posts
    posts.sort(key=lambda row: row['time'], reverse=True)
    mydb.close()
    return posts

## Add a post to the database.
def AddPost(content, username, reply_to_id):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
#    t = time.strftime('%c', time.localtime())
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    
    mydb = mysql.connector.connect(
      host="localhost",
      user="learner",
      passwd="abcd1234",
      database="forum"
    )
    c = mydb.cursor()
    #query = 'insert into posts(content) values( "%s")' % (content,)
    c.execute("select id from users where username = %s", (username,))    
    user_id = c.fetchall()[0][0]
    c.execute("insert into posts (content, user_id, reply_to_id) values (%s, %s, %s)", (content, user_id, reply_to_id))
    mydb.commit()
    mydb.close()
#    DB.append((t, content))

def checkUser(username, passwd):
    mydb = mysql.connector.connect(
      host="localhost",
      user="learner",
      passwd="abcd1234",
      database="forum"
    )
    c = mydb.cursor()
    c.execute("select passwd from users where username = %s and passwd = %s", (username, passwd))
    passwd = c.fetchall()
    if not passwd:
        return False
    return True