import os
from flask import Flask, make_response, redirect, render_template, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.inspection import inspect


# 20.6 8:00AM - 10:30M (2h 30min) [JSON + PostMan]
# 20.6 11:00AM - 11:45M (1h 45min)
# 20.6 12:15PM - 3:45PM (3h 30min)
# 20.6 M - M (h min)
# 20.6      = h min
# 21.6 M - M (h min)
# 21.6 M - M (h min)
# 21.6 M - M (h min)
# 21.6      = h min
#
# """ Zdroje:
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
# user_schema = UserSchema(strict = True)
# users_schema = UserSchema(many = True, strict = True)
# post_schema = PostSchema(strict = True)
# posts_schema = PostSchema(many = True, strict = True)


# Session informations
user_session = {"json": "false", "userId": "", "name": ""}


# Routes
@app.route('/', methods = ['GET', 'POST'])
def index():
    """ Využíva metódy:
    'GET': Vráti domovskú stránku.
    'POST': Prihlásenie a odhlásenie
    """
    if request.method == 'GET': # OK
        return jsonify(user_session)

    elif request.method == 'POST': # upraviť!
        name = request.get_json()
        # print(name) # type dict
        return jsonify(name)


@app.route('/users', methods = ['GET', 'POST'])
def users():
    """ Využíva metódy:
    'GET': Vráti zoznam užívateľov.
    'POST': Pridá nového užívateľa do databázy
    """
    if request.method == 'GET': # OK
        users = User.query.all()
        result = users_schema.dump(users)
        return jsonify(result)

    elif request.method == 'POST': # OK
        name = request.get_json()
        name = name['name']
        user = User.query.filter_by(name = name).first()
        # print(user)
        if user is None:
            new_user = User(name = name)

            db.session.add(new_user)
            db.session.commit()

            result = {"Úspech": f"Užívateľ >>{name}<< bol registrovaný."}
            return jsonify(result)

        result = {"Chyba": f"Užívateľ >>{name}<< už existuje."}
        return jsonify(result)


@app.route('/users/<userId>', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user(userId):
    """ Využíva metódy:
    'GET': Vráti užívateľa na základe userId.
    'POST': Zavolá funkciu na zmenu užívateľských údajov.
    'PUT': Upravenie užívateľa - potrebné validovať userID pomocou externej API ???
    'PATCH': Upravenie užívateľa - potrebné validovať userID pomocou externej API ???
    'DELETE': Odstráni užívateľa ale nie jeho články.
    """
    if request.method == 'GET': # OK
        user = User.query.filter_by(id = userId).first() # .first_or_404
        return user_schema.jsonify(user)

    elif request.method == 'POST':
        name = request.get_json()
        return {"Chyba": f"Užívateľ >>{name}<< už existuje."}

    elif request.method == 'PUT':
        # user = User.queryfilter_by(id = userId).all()

        if name == None:
            name = request.json['name']

        # user.name = name

        # db.session.upgrade(user)
        # db.session.commit()

        # return redirect("/users/<userId>")
        return (userId, name)

    elif request.method == 'PATCH':
        user = User.query.filter_by(id = userId).first()

        name = request.json['name']

        user.name = name

        db.session.commit()

        return redirect(f"/users/{userId}")

    elif request.method == 'DELETE': # OK
        get_user = request.get_json()
        get_userId = get_user['userId']
        user = User.query.filter_by(id = get_userId).first() # .first_or_404
        if user is None:
            result = {"Chyba": f"Užívateľ >>{get_user}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(user)
        db.session.commit()

        result = {"Úspech": f"Užívateľ >>{user}<< bol úspešne odstránený."}
        return jsonify(result)


@app.route('/users/<userId>/posts', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_posts(userId):
    """ Využíva metódy:
    'GET': Vráti zoznam všetkých príspevkov na základe userId.
    'POST': Pridá nový príspevok do databázy a vráti titulok príspevku. Titulok musí byť vyplnený!
        Pridanie príspevku - potrebné validovať userID pomocou externej API
    'PUT':
    'PATCH':
    'DELETE':
    """
    if request.method == 'GET': # OK
        posts = Post.query.filter_by(userId = userId).all()
        result = posts_schema.dump(posts)
        return jsonify(result)

    elif request.method == 'POST': # OK - Chýba validácia!
        # validácia userID pomocou externej API
        # if not valit:
        #     return ...

        post = request.get_json()
        # print(post['title'], post['body'])
        # if post['title'] != '' or post['userId'] != '':
        #     new_post = Post(title = post['title'], body = post['body'], userId = post['userId'])
        if post['title'] != '':
            new_post = Post(title = post['title'], body = post['body'], userId = userId)

            db.session.add(new_post)
            db.session.commit()

            result = {"Úspech": f"Článok >>{post['title']}<< bol pridaný."}
            return jsonify(result)

        # result = {"Chyba": "Buď je autor neznýmy, alebo titulok článku je prázdny."}
        result = {"Chyba": "Titulok článku je prázdny."}
        return jsonify(result)

    elif request.method == 'PUT':
        pass

    elif request.method == 'PATCH':
        pass

    elif request.method == 'DELETE':
        pass


@app.route('/posts', methods = ['GET'])
def posts():
    """ Využíva metódy:
    'GET': Vráti zoznam všetkých príspevkov.
    """
    if request.method == 'GET': # OK
        posts = Post.query.all()
        result = posts_schema.dump(posts)
        return jsonify(result)


@app.route('/posts/<id>', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def post(id):
    """ Využíva metódy:
    'GET': Vráti príspevok na základe id.
        - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
    'POST': Zavolá funkciu pre odstránenie príspevku.
    'PUT': Upravenie príspevku - potrebné validovať userID pomocou externej API
    'PATCH': Upravenie príspevku - potrebné validovať userID pomocou externej API
    'DELETE': Odstráni príspevok.
    """
    if request.method == 'GET': # OK
        post = Post.query.get(id)
        return post_schema.jsonify(post)

    elif request.method == 'POST':
        return

    elif request.method == 'PUT':
        post = Post.queryfilter_by(id = id).all()

        if title == None or body == None or userId == None:
            title = request.json['title']
            body = request.json['body']
            userId = request.json['userId']

        post.title = title
        post.body = body
        post.userId = userId

        db.session.upgrade(post)
        db.session.commit()

        return post_schema.jsonify(post)

    elif request.method == 'PATCH':
        post = Post.query.filter_by(id = id).first()

        if request.json['title']:
            title = request.json['title']
        if request.json['body']:
            body = request.json['body']
        if request.json['userId']:
            userId = request.json['userId']

        if title is not None:
            post.title = title
        if body is not None:
            post.body = body
        if userId is not None:
            post.userId = userId

        db.session.commit()

        return redirect(f"/posts/{id}")

    elif request.method == 'DELETE': # OK
        get_post = request.get_json()
        get_id = get_post['id']
        post = Post.query.filter_by(id = get_id).first() # .first_or_404
        if post is None:
            result = {"Chyba": f"Príspevok >>{get_post}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(post)
        db.session.commit()

        result = {"Úspech": f"Príspevok >>{post}<< bol úspešne odstránený."}
        return jsonify(result)


# python cls:
#     >>> from app import db
#     >>> db.create_all()

# First run
# export --- export FLASK_APP=application.py
# export --- export FLASK_ENV=development

# Run Server
if __name__ == '__main__':
    app.run(debug = False)
