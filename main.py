from flask import Flask, request, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:3306/blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'test'

##################################################

# This is the definition of the database the website will be using.

##################################################

# creates the table for all users and their data.
class users(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(20), unique = True)
    user_id = db.Column(db.Integer, primary_key=True, auto_increment = True)
    user_posts = db.relationship('Posts')
    password = db.Column(db.String(20))
    user_logged_in = db.Column(db.Boolean())
    def __init__(self, username, password, user_logged_in = False, user_posts = []):
        self.username = username
        self.user_posts = user_posts
        self.password = password
        self.user_logged_in = user_logged_in
        
# creates the table for all posts and their content, along with who made them.
class Posts(db.Model):
    __tablename__ = 'Posts'
    post_id = db.Column(db.Integer, primary_key=True, auto_increment = True)
    content = db.Column(db.String(240))
    title = db.Column(db.String(20))
    username = db.Column(db.String(20), db.ForeignKey('users.username'))

    def __init__(self, content, username, title):
        self.content = content
        self.username = username
        self.title = title

##################################################

# This section checks if the user is logged in. If not, it redirects them to the login page. 
# It's also the main route.

##################################################
@app.route('/', methods=['POST', 'GET'])
def index():
    
    user = users.query.filter_by(user_logged_in = True).first()
    if user != None:
        print(user.username)
        print('It works')
        posts = Posts.query.all()
        posts.reverse()
        session['username'] = user.username
        if posts == "Null" or posts == None:
            posts == []
        return render_template('blog.html', posts=posts, username = session['username'])
    else:
        return redirect(url_for('login'))

##################################################

# This section controls various form actions, allowing the addition of new posts and new users to the database.

##################################################

# commits a new post to the database.
@app.route('/submitted', methods=['POST','GET'])
def submitted():
    user = session['username']
    content = request.form['content']
    title = request.form['title']
    db.session.add(Posts(content, user, title))
    db.session.commit()
    return render_template('submitted.html')


# checks if a user is already in the database. If not, it commits a new user to the database.
@app.route('/join', methods = ['POST', 'GET'])
def join():
    user = request.form['user']
    password = request.form['pass']
    passCheck = request.form['passCheck']
    check = users.query.filter_by(username = user).first()

    if check == None:
        if password == passCheck:
            db.session.add(users(user, password, True))
            db.session.commit()
            session['username'] = user
            print(session['username'])
            return redirect(url_for('index'))
        else:
            return redirect(url_for('new_user', err= "Your passwords did not match."))
    else: 
        return redirect(url_for('new_user', err = "We're sorry, that name has already been taken."))

# Renders the new post template.
@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    
    return render_template('new_post.html')

# Username/Password validation.
@app.route('/login_attempt', methods=['POST', 'GET'])
def attempt():
    username = request.form['username']
    password = request.form['password']
    print(username, password)
    user = users.query.filter_by(username = username, password = password).first()

    if user != None:
        posts = Posts.query.all()
        posts.reverse()
        session['username'] = username
        user.user_logged_in = True
        return render_template('blog.html', posts = posts, username = session['username'])
    else:
        return render_template('error.html', err = 'Your username or password was incorrect. Please try again.')

##################################################

# This section deals with displaying posts in various formats.

##################################################

# Displays a single post.
@app.route('/post', methods = ['POST', 'GET'])
def post():
    args = request.args.get('id')
    args = int(args)
    
    post = Posts.query.filter_by(post_id = args).first()
    
    return render_template('post.html', post = post)

# Displays all posts.
@app.route('/blog', methods=['POST','GET'])
def blog():
    args = request.args.get('id')
    if args != None or args != '':
        return render_template('blog.html')
    else:
        post = Posts.query.filter_by(post_id = args)
        return render_template('post.html', post= post)


# Displays all posts made by a specific user.
@app.route('/history', methods = ['POST', 'GET'])
def history():
    args = request.args.get('user')
    if args:
        history = Posts.query.filter_by(username = args)
    else:
        history = Posts.query.filter_by(username = session['username'])
    return render_template('blog.html', posts = history, username = session['username'])


##################################################

# This section deals with logging out and rendering the log in template

##################################################

# Logs the user out and clears the Session dict.
@app.route('/logout')
def logout():
    user = users.query.filter_by(user_logged_in = True).first()
    user.user_logged_in = False
    db.session.commit()
    del session['username']
    
    return redirect(url_for('login'))

# Renders the login template. 
@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

# Renders the New User form.
@app.route('/new_user', methods=['POST', 'GET'])
def new_user():
    args = request.args.get('err')
    if args == None:
        args = ''
    
    return render_template('new_user.html', err = args)

##################################################





if __name__ == '__main__':
    app.run()