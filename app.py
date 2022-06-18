from flask import Flask, redirect, render_template, request, jsonify
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])
# 16.6 1:15PM - 2:45PM (1h 30min) [pridanie zobrazenia príspevkov podla uzivatela]
# 16.6 6:00PM - 7:15 (1h 15min)
# 17.6 8:00AM - 11:30 (3h 30min -30min)
# 17.6 12:30PM - 13:30 (1h)
# 17.6 2:30PM - 5:00PM (2h 30min -15min)
# 17.6 6:00PM? - 9:00PM (3h -30min)
# 18.6 11:00AM -  ()
#
#
#
#
#
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
#
#
#
# """


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Mockend
posts_objekt_json, users_objekt_json = [], []
api_url = 'https://mockend.com/briefs33/Microservice'
posts_objekt_json = requests.get(api_url + '/posts')
users_objekt_json = requests.get(api_url + '/users')
posts_dict = posts_objekt_json.json()
users_dict = users_objekt_json.json()


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

# Post Class/Model
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self) -> None:
        super().__init__()
    # def __init__(self, title, body, userId)
        # self.title = title
        # self.body = body
        # self.userId = userId

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

# """
# python cls:
#     >>> from app import db
#     >>> db.create_all()
# """


# Run Server
# if __name__ == '__main__':
#     app.run(debug = True)


@app.route('/', methods = ['GET'])
def index():
    """ Domovská stránka """
    message = request.args.get("message", "None")
    return render_template("index.html", message = message)


@app.route('/', methods = ['POST'])
def signin():
    """ Domovská stránka """
    message = request.form.get("message", "None")
    return render_template("index.html", message = message)


@app.route('/login', methods = ['GET'])
def css():
    """ Prihlásenie """
    return render_template("login.html")


@app.route('/posts', methods = ['GET'])
def get_posts():
    """ Zobrazenie príspevkov alebo príspevku
    - na základe id alebo userId
    - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
      (platné iba pre vyhľadávanie pomocou id príspevku) """
    id = request.args.get("id", "None")
    userId = request.args.get("userId", "None")
    output = {}

    if not id=="None":
        for d in posts_dict:
            if int(d['id']) == int(id):
                output = d
                break

        # post = Post.query.get(id)
        # return post_schema.jsonify(post)
        return render_template("post.html", post = output)
    elif not userId=="None":
        for d in posts_dict:
            if int(d['userId']) == int(userId): # upravuje poradie príspevkov
                output['post{}'.format(d['userId'])] = d

        # posts = Post.query.get(userId)
        # result = posts_schema.dump(posts)
        # return jsonify(result.data)
        return render_template("posts.html", posts = output)

    # posts = Post.query.all()
    # result = posts_schema.dump(all_posts)
    # return jsonify(result.data)
    return render_template("posts.html", posts = posts_dict)


@app.route('/users', methods = ['GET'])
def get_users():
    """ Zobrazenie užívateľov """
    userId = request.args.get("userId", "None")
    output = {}

    if not userId=="None":
        for d in posts_dict:
            if int(d['userId']) == int(userId): # upravuje poradie príspevkov
                output['post{}'.format(d['id'])] = d

        # posts = User.query.get(userId)
        # result = posts_schema.dump(posts)
        # return jsonify(result.data)
        return render_template("user.html", user = output)

    # users = User.query.all()
    # result = users_schema.dump(all_users)
    # return jsonify(result.data)
    return render_template("users.html", users = users_dict)


@app.route('/new_post', methods=['GET'])
def new_post():
    return render_template("new_post.html", users = users_dict)


@app.route('/posts', methods=['POST'])
def add_post():
    """ Pridanie príspevku - potrebné validovať userID pomocou externej API """
    id = int(posts_dict[-1]['id']) + 1
    title = request.form.get("title")
    body = request.form.get("body")
    userId = request.form.get("userId")

    thisdict = {
        "id": id,
        "title": title,
        "body": body,
        "userId": userId
    }

    if not title or not body or not userId:
       return render_template("failure.html")

    # new_post = Post(title, body, userId)
    #
    # db.session.add(new_post)
    # db.session.commit()
    # 
    # return post_schema.jsonify(new_post)
    posts_dict.append(thisdict)
    return redirect("/posts")


@app.route('/registration', methods=['GET'])
def registration():
    return render_template("registration.html")


@app.route('/register', methods=['POST'])
def add_user():
    """ Pridanie užívateľa - potrebné validovať userID pomocou externej API """
    userId = int(users_dict[-1]['id']) + 1
    name = request.form.get("name")

    thisdict = {
        "id": userId,
        "name": name
    }

    if not name:
        return render_template("failure.html")

    # new_user = User(name)
    #
    # db.session.add(new_user)
    # db.session.commit()
    # 
    # return user_schema.jsonify(new_user)
    users_dict.append(thisdict)
    return redirect("/users")


@app.route('/posts/<id>', methods=['PUT'])
def put_post(id, title, body, userId):
# def update_post(id):
    """ Upravenie príspevku - potrebné validovať userID pomocou externej API """
    for d in posts_dict:
        if int(d['id']) == int(id):
            d["title"] = title
            d["body"] = body
            d["userId"] = userId
            return (d, {"Správa": "Príspevok bol upravený."})

    # post = Post.query.get(id)
    #
    # title = request.json['title']
    # body = request.json['body']
    # userId = request.json['userId']
    #
    # post.title = title
    # post.body = body
    # post.userId = userId
    #
    # db.session.commit()
    # 
    # return post_schema.jsonify(post)
    return {'Chyba': "Príspevok som nenašiel!"}


@app.route('/posts/<id>', methods=['PATCH'])
def patch_post(id, title, body):
    """ Upravenie príspevku - možnosť meniť title a body """
    for d in posts_dict:
        if int(d['id']) == int(id):
            d["title"] = title
            d["body"] = body
            return (d, {"Správa": "Príspevok bol upravený."})
    return {'Chyba': "Príspevok som nenašiel!"}


@app.route('/posts/<id>', methods=['DELETE'])
def delete_post(id):
    """ Odstránenie príspevku """
    post = get_posts(id)
    if post == {'Chyba': 404}:
        return {'Chyba': "Príspevok som nenašiel!"}
    posts_dict.pop(id) # put_post -> for d in posts_dict: if int(d['id']) == int(id):

    # post = Post.query.get(id)
    #
    # db.session.delete(post)
    # db.session.commit()
    #
    # return post_schema.jsonify(post)
    return {"Správa": "Príspevok bol odstránený."}
