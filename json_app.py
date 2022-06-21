import os
from flask import Flask, make_response, redirect, render_template, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.inspection import inspect


# 20.6 8:00AM - 10:30M (2h 30min) [JSON + PostMan]
# 20.6 11:00AM - 11:45M (1h 45min)
# 20.6 12:15PM - 3:45PM (3h 30min)
# 20.6 4:30PM - 5:30PM (1h)
# 20.6 6:00PM - 11:00PM (5h)
# 20.6      = 13h 45min
# 21.6 7:00AM - M (h min)
# 21.6 M - M (h min)
# 21.6 M - M (h min)
# 21.6      = h min
#
# """ Zdroje:
# https://www.youtube.com/playlist?list=PLNAMH_0HgWT812u973ptEbZlQ2uIqp-II
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
user_session = {"json": False, "prihlaseny": False, "userId": "", "name": ""}


# Routes
@app.route('/', methods = ['GET', 'POST'])
def index():
    """ Využíva metódy:
    'GET': Vráti domovskú stránku a vypíše user_session.
    'POST': Prihlásenie a odhlásenie
    """
    if request.method == 'GET': # OK ... Plne unkčné
        result = user_session
        return jsonify(result)

    elif request.method == 'POST': # OK ... Plne unkčné
        result_get = request.get_json()
        user_session['json'] = result_get['json']
        user_session['name'] = result_get['name']

        if user_session['name'] or user_session['name'] == '':
            user_query = User.query.filter_by(name = user_session['name']).first()

            if user_query is None:
                user_session['prihlaseny'] = False
                user_session['userId'] = ""
                user_session['name'] = ""

                result = {"Chyba prihlásenia": f"{result_get['name']}. Teba nepoznám, najprv sa zaregistruj!"}
                return jsonify(result)

            user_session['prihlaseny'] = True
            user_session['userId'] = user_query.id
            user_session['name'] = user_query.name

            result = (user_session, f"Vitaj {user_session['name']}")
            return jsonify(result)

        user_session['prihlaseny'] = False
        user_session['userId'] = ""
        user_session['name'] = ""

        result = (user_session, f"Odhlásenie")
        return jsonify(result)


@app.route('/users', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def users():
    """ Využíva metódy:
    'GET': Vráti zoznam užívateľov.
    'POST': Pridá užívateľa do databázy. Registrácia užívateľa.
        Ak je {name: true} => '1',
        ak je {name: false} => '0',
        ak je {name: "true"} => 'true',
        ak je {name: "false"} => 'false'
    'PUT': Zmení meno užívateľa.
    'DELETE': Odstráni užívateľa z databázy.
    """
    if request.method == 'GET': # OK ... Plne unkčné
        users_query = User.query.all()
        result = users_schema.dump(users_query)
        return jsonify(result)

    elif request.method == 'POST': # OK ... Plne unkčné
        user_get = request.get_json()
        user_get_name = user_get['name']

        if user_get and user_get_name != '':
            user_query = User.query.filter_by(name = user_get_name).first()

            if user_query is None:
                user_query = User(name = user_get_name)

                db.session.add(user_query)
                db.session.commit()

                result = {"Úspech": f"Užívateľ >>{user_query.name}<< bol registrovaný."}
                return jsonify(result)

            result = {"Chyba": f"Užívateľ >>{user_query.name}<< už existuje."}
            return jsonify(result)

        result = {"Chyba": "Meno užívateľa je prázdne."}
        return jsonify(result)

    elif request.method == 'PUT': # OK ... Plne unkčné
        user_get = request.get_json()
        user_get_id = user_get['id']
        user_get_name = user_get['name']

        user_query = User.query.filter_by(name = user_get_name).first()

        if user_query is None and user_get_id != '':
            user_query = User.query.filter_by(id = user_get_id).first()

            user_query.name = user_get_name

            db.session.commit()

            user_query = User.query.filter_by(id = user_get_id).first()
            return user_schema.jsonify(user_query) # Meno bolo úspešne zmenené.

        result = {"Chyba": "Chýba id alebo meno užívateľa už je v databáze."}
        return jsonify(result)

    elif request.method == 'DELETE': # OK ... Plne unkčné
        user_get = request.get_json()
        user_get_id = user_get['id']

        user_query = User.query.filter_by(id = user_get_id).first()

        if user_query is None:
            result = {"Chyba": f"Užívateľ >>{user_get}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(user_query)
        db.session.commit()

        result = {"Úspech": f"Užívateľ >>{user_query.name}<< bol úspešne odstránený."}
        return jsonify(result)


@app.route('/posts', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def posts():
    """ Využíva metódy:
    'GET':
    'POST':
    'PUT':
    'PATCH':
    'DELETE':
    """
    if request.method == 'GET': # O
        posts_query = Post.query.all()
        result = posts_schema.dump(posts_query)
        return jsonify(result)

    elif request.method == 'POST': # O - Chýba validácia!
        # validácia userID pomocou externej API
        # if not valit:
        #     return ...

        post_get = request.get_json()
        post_get_title = post_get['title']
        post_get_body = post_get['body']
        post_get_userId = post_get['userId']

        if post_get and post_get_title != '' and post_get_userId != '':
            post_query = Post(title = post_get_title, body = post_get_body, userId = post_get_userId)

            db.session.add(post_query)
            db.session.commit()

            result = {"Úspech": f"Článok >>{post_query.title}<< bol pridaný."} # možná chyba => post_get_title
            return jsonify(result)

        result = {"Chyba": "Buď je autor neznámy, alebo titulok článku je prázdny."}
        return jsonify(result)

    elif request.method == 'PUT': # O
        post_get = request.get_json()

        if post_get and post_get_id != '':
            post_get_id = post_get['id']
            post_get_title = post_get['title']
            post_get_body = post_get['body']
            post_get_userId = post_get['userId']

            post_query = Post.query.filter_by(id = post_get_id).first()

            if post_get_title != '':
                post_query.title = post_get_title

            if post_get_body != '':
                post_query.body = post_get_body

            if post_get_userId != '':
                post_query.userId = post_get_userId

            db.session.commit()

            post_query = Post.query.filter_by(id = post_get_id).first()
            return post_schema.jsonify(post_query)

        result = {"Chyba: Chýba id príspevku."}
        return jsonify(result)

    elif request.method == 'PATCH': # O
        post_get = request.get_json()
        post_get_what = post_get['what']
        post_get_from = post_get['from']
        post_get_to = post_get['to']

        if post_get and post_get_what != '' and post_get_from != '' and post_get_to != '':

            if post_get_what == 'id': # O
                posts_query = Post.query.filter_by(id = post_get_from).all()
                posts_query.id = post_get_to

                db.session.commit()

                posts_query = Post.query.filter_by(id = post_get_to).all()
                result = posts_schema.dump(posts_query)
                return jsonify(result)

            elif post_get_what == 'title': # O
                posts_query = Post.query.filter_by(title = post_get_from).all()
                posts_query.title = post_get_to

                db.session.commit()

                posts_query = Post.query.filter_by(title = post_get_to).all()
                result = posts_schema.dump(posts_query)
                return jsonify(result)

            elif post_get_what == 'body': # O
                posts_query = Post.query.filter_by(body = post_get_from).all()
                posts_query.body = post_get_to

                db.session.commit()

                posts_query = Post.query.filter_by(body = post_get_to).all()
                result = posts_schema.dump(posts_query)
                return jsonify(result)

            elif post_get_what == 'userId': # O
                posts_query = Post.query.filter_by(userId = post_get_from).all()
                posts_query.userId = post_get_to

                db.session.commit()

                posts_query = Post.query.filter_by(userId = post_get_to).all()
                result = posts_schema.dump(posts_query)
                return jsonify(result)

        result = {"Chyba: Chýba čo ['what'], z čoho ['from'] alebo na čo ['to'] príspevku."}
        return jsonify(result)

    elif request.method == 'DELETE': # O
        post_get = request.get_json()
        post_get_id = post_get['id']

        post_query = Post.query.filter_by(id = post_get_id).first()

        if post_query is None:
            result = {"Chyba": f"Príspevok >>{post_get}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"Úspech": f"Príspevok >>{post_schema.jsonify(post_query)}<< bol úspešne odstránený."} # jsonify
        return jsonify(result)


@app.route('/users/<userId>', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user(userId):
    """ Využíva metódy:
    'GET': Vráti užívateľa na základe userId.
    'POST': Zavolá funkciu na zmenu užívateľských údajov pre HTML.
    'PUT': Upravenie užívateľa - potrebné validovať userID pomocou externej API ???
    'PATCH': Upravenie užívateľa - potrebné validovať userID pomocou externej API ???
    'DELETE': Odstráni užívateľa ale nie jeho články.
    """
    if request.method == 'GET': # O
        user_query = User.query.filter_by(id = userId).first()
        return user_schema.jsonify(user_query)

    elif request.method == 'POST': # O
        """ presmerovanie pre HTML """

        result = {"Info": "Metóda zatiaľ nie je definovaná."}
        return jsonify(result)

    elif request.method == 'PUT': # O
        user_get = request.get_json()
        user_get_name = user_get['name']

        user_query = User.query.filter_by(name = user_get_name).first()

        if user_query is None and userId != '':
            user_query = User.query.filter_by(id = userId).first()

            user_query.name = user_get_name

            db.session.commit()

            user_query = User.query.filter_by(id = userId).first()
            return user_schema.jsonify(user_query) # Meno bolo úspešne zmenené.

        result = {"Chyba": "Meno užívateľa už je v databáze."}
        return jsonify(result)

    elif request.method == 'PATCH': # O
        result = {"Info": "Metóda zatiaľ nie je definovaná."}
        return jsonify(result)

    elif request.method == 'DELETE': # O
        user_get = request.get_json()

        user_query = User.query.filter_by(id = userId).first()

        if user_query is None:
            result = {"Chyba": f"Užívateľ >>{userId, user_get}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(user_query)
        db.session.commit()

        result = {"Úspech": f"Užívateľ >>{user_query.name}<< bol úspešne odstránený."}
        return jsonify(result)


@app.route('/users/<userId>/posts', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user_posts(userId):
    """ Využíva metódy:
    'GET': Vráti zoznam všetkých príspevkov na základe userId.
    'POST': Pridá nový príspevok do databázy a vráti titulok príspevku. Titulok musí byť vyplnený!
        Pridanie príspevku - potrebné validovať userID pomocou externej API
    'PUT':
    'DELETE':
    """
    if request.method == 'GET': # O
        posts_query = Post.query.filter_by(userId = userId).all()
        result = posts_schema.dump(posts_query)
        return jsonify(result)

    elif request.method == 'POST': # O - Chýba validácia!
        # validácia userID pomocou externej API
        # if not valit:
        #     return ...

        post_get = request.get_json()

        if post_get or post_get['title'] != '':
            post_get_title = post_get['title']
            post_get_body = post_get['body']

            post_query = Post(title = post_get_title, body = post_get_body, userId = userId)

            db.session.add(post_query)
            db.session.commit()

            result = {"Úspech": f"Článok >>{post_get_title}<< bol pridaný."}
            return jsonify(result)

        result = {"Chyba": "Titulok článku je prázdny."}
        return jsonify(result)

    elif request.method == 'PUT': # O
        post_get = request.get_json()

        if post_get and post_get_id != '':
            post_get_id = post_get['id']
            post_get_title = post_get['title']
            post_get_body = post_get['body']

            post_query = Post.query.filter_by(id = post_get_id, userId = userId).first()

            if post_query is None:
                result = {"Chyba": f"V repozitári užívateľa >>{userId}<< sa nenachýdza príspevok s identifikátorom >>{post_get_id}<<."}
                return jsonify(result)

            if post_get_title != '':
                post_query.title = post_get_title

            if post_get_body != '':
                post_query.body = post_get_body

            db.session.commit()

            post_query = Post.query.filter_by(id = post_get_id).first()
            return post_schema.jsonify(post_query)

        result = {"Chyba: Chýba id príspevku."}
        return jsonify(result)

    elif request.method == 'DELETE': # O
        post_get = request.get_json()
        post_get_id = post_get['id']

        post_query = Post.query.filter_by(id = post_get_id, userId = userId).first()

        if post_query is None:
            result = {"Chyba": f"Príspevok >>{post_get}<< nepatrí užívateľovi >>{userId}<< alebo nie je v databáze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"Úspech": f"Príspevok >>{post_get_id}<< bol úspešne odstránený."}
        return jsonify(result)


@app.route('/posts/<id>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def post(id):
    """ Využíva metódy:
    'GET': Vráti príspevok na základe id.
        - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
    'POST': Zavolá funkciu pre odstránenie príspevku.
    'PUT': Upravenie príspevku - potrebné validovať userID pomocou externej API
    'DELETE': Odstráni príspevok.
    """
    if request.method == 'GET': # O
        post = Post.query.get(id)
        return post_schema.jsonify(post)

    elif request.method == 'POST': # O
        result = {"Info": "Metóda zatiaľ nie je definovaná."}
        return jsonify(result)

    elif request.method == 'PUT': # O potrebné validovať userID pomocou externej API
        post_get = request.get_json()

        if post_get:
            post_get_title = post_get['title']
            post_get_body = post_get['body']
            post_get_userId = post_get['userId']

            post_query = Post.query.filter_by(id = id).first()

            if post_get_title != '':
                post_query.title = post_get_title

            if post_get_body != '':
                post_query.body = post_get_body

            if post_get_userId != '':
                post_query.userId = post_get_userId

            db.session.commit()

            post_query = Post.query.filter_by(id = id).first()
            return post_schema.jsonify(post_query)

        result = {"Chyba: Chýba príkaz k upraveniu príspevku."}
        return jsonify(result)

    elif request.method == 'DELETE': # O
        post_get = request.get_json()
        post_query = Post.query.filter_by(id = id).first()

        if post_query is None:
            result = {"Chyba": f"Príspevok >>{post_get}<< nie je v databáze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"Úspech": f"Príspevok >>{id}<< bol úspešne odstránený."}
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
