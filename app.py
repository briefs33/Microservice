
from flask import Flask, make_response, redirect, render_template, request, jsonify
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask_marshmallow import Marshmallow
import os


# 15.6 1:33PM - 4:33PM (3h) 
# 15.6 6:00PM - 7:00PM (1h)
# 15.6 5:15PM - 5:30PM (15min)
# 15.6 7:00PM - 8:00PM (1h)
# 15.6      = 5h 15min
# 16.6 6:45AM - 10:00AM (3h 15min)
# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])
# 16.6 1:15PM - 2:45PM (1h 30min) [pridanie zobrazenia príspevkov podla uzivatela]
# 16.6 6:00PM - 7:15 (1h 15min)
# 16.6      = 7h 30min
# 17.6 8:00AM - 11:30 (3h 30min -30min)
# 17.6 12:30PM - 13:30 (1h)
# 17.6 2:30PM - 5:00PM (2h 30min -15min)
# 17.6 6:00PM - 9:00PM (3h -30min)
# 17.6      = 8h 45min
# 18.6 5:00PM - 6:00PM (None) [Príprava oživenia db]
# 18.6 7:00PM - 10:00PM (3h)
# 18.6      = 3h 0min (+3h CSS)
# 19.6 8:00AM - 10:30AM (2h 30min) [filter_by(id/userId).all()]
# 19.6 12:00AM - () [Prekopanie stránky]
#
# 19.6      = h min
#
# """ Zdroje:
# https://www.youtube.com/watch?v=qbLc5a9jdXo&ab_channel=CalebCurry
# https://www.w3schools.com/
# https://www.youtube.com/watch?v=PTZiDnuC86g&ab_channel=TraversyMedia
# https://www.youtube.com/watch?v=zdgYw-3tzfI&ab_channel=freeCodeCamp.org
# https://www.hwlibre.com/sk/orm-object-relational-mapping/
# https://www.sqlalchemy.org/
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
# https://marshmallow.readthedocs.io/en/stable/quickstart.html
# https://flask.palletsprojects.com
# https://stackoverflow.com/
# https://python-adv-web-apps.readthedocs.io/en/latest/flask_db2.html [filter_by(id/userId).all()]
#
#
#
#
#
#
#
#
#
#
#
#
# """


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Mockend
# posts_objekt_json, users_objekt_json = [], []
# api_url = 'https://mockend.com/briefs33/Microservice'
# posts_objekt_json = requests.get(api_url + '/posts')
# users_objekt_json = requests.get(api_url + '/users')
# posts_dict = posts_objekt_json.json()
# users_dict = users_objekt_json.json()


# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)


# User Class/Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    children = db.relationship("Post")

    def __init__(self, name, remote_addr = None):
        self.name = name
        if remote_addr is None and request:
            remote_addr = request.remote_addr
        self.remote_addr = remote_addr

    def __repr__(self):
        return '<User %r>' % self.name

# Post Class/Model
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, title, body, userId, remote_addr = None):
        self.title = title
        self.body = body
        self.userId = userId
        if remote_addr is None and request:
            remote_addr = request.remote_addr
        self.remote_addr = remote_addr

    def __repr__(self):
        return '<Post %r>' % self.title

# def last_row(Table: type, *, session): # -> Table
#     primary_key = inspect(Table).primary_key[0].name # must be an arithmetic type
#     primary_key_row = getattr(Table, primary_key)
#     # get first, sorted by negative ID (primary key)
#     return session.query(Table).order_by(-primary_key_row).first()


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

# Post Schema
class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'body', 'userId')

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many = True)
post_schema = PostSchema()
posts_schema = PostSchema(many = True)


# GET Routes
@app.route('/', methods = ['GET'])
def index():
    """ Vráti domovskú stránku. """
    message = request.args.get("message", "None")
    return render_template("index.html", message = message)


@app.route('/registration', methods=['GET'])
def registration():
    """ Vráti formulár pre registráciu nového užívateľa. """
    return render_template("registration.html")


@app.route('/login', methods = ['GET'])
def css():
    """ Vráti formulár pre prihlásenie užívateľa """
    return render_template("login.html")


@app.route('/users', methods = ['GET'])
def get_users():
    """ Vráti zoznam užívateľov """
    users = User.query.all()
    result = users_schema.dump(users)
    return render_template("users.html", users = result)
    return render_template("users.html", users = jsonify(result)) # result.data
    return render_template("users.html", users = users_dict)


@app.route('/users/<userId>', methods = ['GET'])
def get_user(userId):
    """ Vráti užívateľa na základe userId. """
    return render_template("user.html", userId = userId) # result.data
    # user = User.query.get(userId)
    return render_template("user.html", user = jsonify(result)) # result.data
    # userId = request.args.get("userId", "None")
    output = {}
    # for d in posts_dict:
    #     if int(d['userId']) == int(userId): # upravuje poradie príspevkov
    #         output['post{}'.format(d['id'])] = d
    return render_template("user.html", user = output)


@app.route('/posts', methods = ['GET'])
def get_posts():
    """ Vráti zoznam všetkých príspevkov. """
    posts = Post.query.all()
    result = posts_schema.dump(posts)
    return render_template("posts.html", posts = result)
    return render_template("posts.html", posts = jsonify(result)) # result.data
    return render_template("posts.html", posts = posts_dict)


@app.route('/posts/<id>', methods = ['GET'])
def get_post(id):
    """ Vráti príspevok na základe id.
    - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť """
    post = Post.query.get(id)
    return render_template("post.html", post = post)
    return render_template("post.html", post = post_schema.jsonify(post))
    output = {}

    # for d in posts_dict:
    #     if int(d['id']) == int(id):
    #         output = d
    #         break
    # print(int(id))
    return render_template("post.html", post = output)


@app.route('/users/<userId>/posts', methods = ['GET'])
def get_user_posts(userId):
    """ Vráti zoznam všetkých príspevkov na základe userId. """
    posts = Post.query.filter_by(userId = userId).all()
    result = posts_schema.dump(posts)
    return render_template("posts.html", posts = result)
    return render_template("posts.html", posts = jsonify(result)) # result.data
    output = {}

    # for d in posts_dict:
    #     if int(d['userId']) == int(userId): # upravuje poradie príspevkov
    #         output['post{}'.format(d['userId'])] = d
    # print(int(userId))
    return render_template("posts.html", posts = output)


@app.route('/users/<userId>/new_post', methods=['GET'])
def new_post(userId):
    """ Vráti formulár pre napísanie nového článku. """
    return render_template("new_post.html", userId = userId)


# POST Routes
@app.route('/', methods = ['POST'])
def signin():
    """ Po úspešnom prihlásení užívateľa vráti domovskú stránku. """
    message = request.form.get("name", "None")
    return render_template("index.html", message = message)


@app.route('/register', methods=['POST'])
def add_user():
    """ Pridá nového užívateľa do databázy, a vráti ???
    Pridanie užívateľa - potrebné validovať userID pomocou externej API """
    name = request.form.get("name")
    if not name:
        return render_template("registration.html?chyba=no_name")

    new_user = User(name = name)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")
    return user_schema.jsonify(new_user)
    userId = int(users_dict[-1]['id']) + 1

    thisdict = {
        "id": userId,
        "name": name
    }

    users_dict.append(thisdict)


@app.route('/users/<userId>/posts', methods=['POST'])
def add_post(userId):
    """ Pridá nový článok do databázy, a vráti ???
    Pridanie príspevku - potrebné validovať userID pomocou externej API """
    title = request.form.get("title")
    body = request.form.get("body")
    # userId = request.form.get("userId")

    if not title or not body or not userId:
       return render_template("new_post.html?chyba=no_title_or_body_or_who_you_are")

    new_post = Post(title = title, body = body, userId = userId)

    db.session.add(new_post)
    db.session.commit()

    return redirect("/posts")
    return post_schema.jsonify(new_post)
    id = int(posts_dict[-1]['id']) + 1

    thisdict = {
        "id": id,
        "title": title,
        "body": body,
        "userId": userId
    }

    posts_dict.append(thisdict)



""" Neoverené: """

# # PUT Routes
# @app.route('/posts/<id>', methods=['PUT'])
# def put_post(id, title, body, userId):
# # def update_post(id):
#     """ Upravenie príspevku - potrebné validovať userID pomocou externej API """
#     for d in posts_dict:
#         if int(d['id']) == int(id):
#             d["title"] = title
#             d["body"] = body
#             d["userId"] = userId
#             return (d, {"Správa": "Príspevok bol upravený."})

#     post = Post.queryfilter_by(id = id).all()

#     title = request.json['title']
#     body = request.json['body']
#     userId = request.json['userId']

#     post.title = title
#     post.body = body
#     post.userId = userId

#     db.session.commit()

#     return post_schema.jsonify(post)
#     return {'Chyba': "Príspevok som nenašiel!"}


# # PATCH Routes
# @app.route('/posts/<id>', methods=['PATCH'])
# def patch_post(id, title, body):
#     """ Upravenie príspevku - možnosť meniť title a body """
#     for d in posts_dict:
#         if int(d['id']) == int(id):
#             d["title"] = title
#             d["body"] = body
#             return (d, {"Správa": "Príspevok bol upravený."})
#     return {'Chyba': "Príspevok som nenašiel!"}


# # DELETE Routes
# @app.route('/posts/<id>', methods=['DELETE'])
# def delete_post(id):
#     """ Odstránenie príspevku """
#     post = get_posts(id)
#     if post == {'Chyba': 404}:
#         return {'Chyba': "Príspevok som nenašiel!"}
#     posts_dict.pop(id) # put_post -> for d in posts_dict: if int(d['id']) == int(id):

#     post = Post.query.filter_by(id = id).all()

#     db.session.delete(post)
#     db.session.commit()

#     return post_schema.jsonify(post)
#     return {"Správa": "Príspevok bol odstránený."}


# python cls:
#     >>> from app import db
#     >>> db.create_all()

# First run
# export --- export FLASK_APP=application.py
# export --- export FLASK_ENV=development

# Run Server
# if __name__ == '__main__':
#     app.run(debug = True) # False!
