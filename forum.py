#
# DB Forum - a buggy web forum server backed by a good database
#

# The forumdb module is where the database interface code goes.
import forumdb
import os

# Other modules used to run a web server.
import cgi
from wsgiref.simple_server import make_server
from wsgiref import util

# HTML template for the forum page
HTML_WRAP = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>DB Forum</title>
    <style>
      h1, form { text-align: center; }
      textarea { width: 400px; height: 100px; }
      div.post { border: 1px solid #999;
                 padding: 10px 10px;
		 margin: 10px 20%%; }
      hr.postbound { width: 50%%; }
      em.date { color: #999 }
    </style>
  </head>
  <body>
    <h1>DB Forum</h1>
    <form method=post action="/post">
       User name: <input type="text" name="username"><br>
       Password: <input type="text" name="passwd">
       <input type="hidden" name="post_id" value=0>
      <div><textarea id="content" name="content" placeholder="Message"></textarea></div>
      <div><button id="go" type="submit">Post message</button></div>
    </form>
    <!-- post content will go here -->
%s
  </body>
</html>
'''


# HTML template for an individual comment
POST_0 = '''\
    <div class=post><img src="http://localhost:8001/%(touxiang)s" width=30 height=30><em class=date>%(username)s: %(time)s</em><br>%(content)s
'''
POST_1 = '''\
    <form method=post action="/post">
        User name: <input type="text" name="username" placeholder="username">
        Password: <input type="text" name="passwd" placeholder="password">
        <input type="text" name="content" placeholder="Message"><br>
        <input type="hidden" name="post_id" value=%(post_id)s>
        <div><button type="submit">Reply message</button></div>
    </form>
    </div>
'''
#POST_1 = '''\
#    <form method=post action="/reply">
#        <div><textarea name="content" placeholder="Message"></textarea></div>
#        <input type="hidden" name="post_id" value=%(post_id)s>
#        <div><button type="submit">Reply message</button></div>
#    </form>
#    </div>
#'''

#<div class=post><em class=date>%(user_name)s: %(time)s</em><br>%(content)s</div>
## Request handler for main page
def View(env, resp):
    '''View is the 'main page' of the forum.

    It displays the submission form and the previously posted messages.
    '''
    # get posts from database
    posts = forumdb.GetAllPosts()
    d = {}
    for each in posts:
        child_idx = each['post_id']
        parent_idx = each['reply_id']
        if parent_idx in d:
            d[parent_idx].append(child_idx)
        else:
            d[parent_idx] = [child_idx]
    posts = {each['post_id']: each for each in posts}
    
    def robot(curr_idx, d, posts):
        if curr_idx not in d:
            ans = POST_0 % posts[curr_idx] + POST_1 % posts[curr_idx]
            return ans
        temp = POST_0 % posts[curr_idx]
        for nxt_idx in d[curr_idx]:
            temp += robot(nxt_idx, d, posts)
            
        temp += POST_1 % posts[curr_idx]
        return temp
    
    ans = ''
    if len(d[0]) != 0:
        for i in d[0]:
            ans += robot(i, d, posts)
    # send results
    headers = [('Content-type', 'text/html')]
    resp('200 OK', headers)
    return [HTML_WRAP % (ans,)]

## Request handler for posting - inserts to database
def Post(env, resp):
    '''Post handles a submission of the forum's form.
  
    The message the user posted is saved in the database, then it sends a 302
    Redirect back to the main page so the user can see their new post.
    '''
    # Get post content
    print 'env = ', env
    input = env['wsgi.input']
    print 'input: ', input
    length = int(env.get('CONTENT_LENGTH', 0))
    # If length is zero, post is empty - don't save it.
    if length > 0:
        postdata = input.read(length)
        print 'postdata: ', postdata
        fields = cgi.parse_qs(postdata)
        content = fields['content'][0]
        username = fields['username'][0]
        passwd = fields['passwd'][0]
        reply_to_id = fields['post_id'][0]
        islegal = forumdb.checkUser(username, passwd)
        if not islegal:
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
            resp(status, headers)    
            return ['Not Found user']
        # If the post is just whitespace, don't save it.
        content = content.strip()
        if content:
            # Save it in the database
            forumdb.AddPost(content, username, reply_to_id)
    # 302 redirect back to the main page
    headers = [('Location', '/'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers) 
    return ['Redirecting']

## Dispatch table - maps URL prefixes to request handlers
DISPATCH = {'': View,
            'post': Post,
	    }

## Dispatcher forwards requests according to the DISPATCH table.
def Dispatcher(env, resp):
    '''Send requests to handlers based on the first path component.'''
    #print('ENV:', env)
    page = util.shift_path_info(env)
    print('page:', page)
    if page in DISPATCH:
        return DISPATCH[page](env, resp)
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain')]
        resp(status, headers)    
        return ['Not Found: ' + page]


# Run this bad server only on localhost!
httpd = make_server('', 8000, Dispatcher)
print( "Serving HTTP on port 8000...")
httpd.serve_forever()



