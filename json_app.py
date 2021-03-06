import os
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy


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
    """ Vyu????va met??dy:
    'GET': Vr??ti domovsk?? str??nku a vyp????e user_session.
    'POST': Upravuje user_session. Prihl??senie a odhl??senie u????vate??a.
    """
    if request.method == 'GET':
        result = user_session
        return jsonify(result)

    elif request.method == 'POST':
        result_get = request.get_json()
        try:
            result_get['json']
        except:
            user_session['json'] = True
        else:
            user_session['json'] = result_get['json']

        try:
            result_get['name']
        except:
            user_session['name'] = ""
        else:
            user_session['name'] = result_get['name']

        if result_get['name']:
            user_query = User.query.filter_by(name = user_session['name']).first()

            if user_query is None:
                user_session['prihlaseny'] = False
                user_session['userId'] = ""
                user_session['name'] = ""

                result = {"Chyba prihl??senia": f"{result_get['name']}. Teba nepozn??m, najprv sa zaregistruj!"}
                return jsonify(result)

            user_session['prihlaseny'] = True
            user_session['userId'] = user_query.id
            user_session['name'] = user_query.name

            result = (user_session, f"Vitaj {user_session['name']}")
            return jsonify(result)

        user_session['prihlaseny'] = False
        user_session['userId'] = ""
        user_session['name'] = ""

        result = (user_session, f"Odhl??senie")
        return jsonify(result)


@app.route('/users', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def users():
    """ Vyu????va met??dy:
    'GET': Vr??ti zoznam u????vate??ov.
    'POST': Prid?? u????vate??a do datab??zy. Registr??cia u????vate??a.
        Ak je {name: true} => '1',
        ak je {name: false} => '0',
        ak je {name: "true"} => 'true',
        ak je {name: "false"} => 'false'
    'PUT': Zmen?? meno u????vate??a.
    'DELETE': Odstr??ni u????vate??a z datab??zy.
    """
    if request.method == 'GET':
        users_query = User.query.all()
        result = users_schema.dump(users_query)
        return jsonify(result)

    elif request.method == 'POST':
        user_get = request.get_json()
        try:
            user_get['name']
        except:
            result = {"Chyba": "Ch??ba 'name' u????vate??a."}
            return jsonify(result)
        else:
            user_get_name = user_get['name']

        if user_get_name:
            user_query = User.query.filter_by(name = user_get_name).first()

            if user_query is None and user_get_name:
                user_query = User(name = user_get_name)

                db.session.add(user_query)
                db.session.commit()

                result = {"??spech": f"U????vate?? >>{user_query.name}<< bol registrovan??."}
                return jsonify(result)

            result = {"Chyba": f"U????vate?? >>{user_query.name}<< u?? existuje."}
            return jsonify(result)

        result = {"Chyba": "Meno u????vate??a je pr??zdne."}
        return jsonify(result)

    elif request.method == 'PUT':
        user_get = request.get_json()
        try:
            user_get['id']
            user_get['name']
        except:
            result = {"Chyba": "Ch??ba 'id' alebo 'name' u????vate??a."}
            return jsonify(result)
        else:
            user_get_id = user_get['id']
            user_get_name = user_get['name']

        user_query = User.query.filter_by(name = user_get_name).first()

        if user_query is None:
            user_query = User.query.filter_by(id = user_get_id).first()

            user_query.name = user_get_name

            db.session.commit()

            user_query = User.query.filter_by(id = user_get_id).first()
            return user_schema.jsonify(user_query)

        result = {"Chyba": f"U????vate?? s menom >>{user_get_name}<< u?? je v datab??ze."}
        return jsonify(result)

    elif request.method == 'DELETE':
        user_get = request.get_json()
        try:
            user_get['id']
        except:
            result = {"Chyba": "Ch??ba 'id' u????vate??a."}
            return jsonify(result)
        else:
            user_get_id = user_get['id']

        user_query = User.query.filter_by(id = user_get_id).first()

        if user_query is None:
            result = {"Chyba": f"U????vate?? >>{user_get}<< nie je v datab??ze."}
            return jsonify(result)

        db.session.delete(user_query)
        db.session.commit()

        result = {"??spech": f"U????vate?? >>{user_query.name}<< bol ??spe??ne odstr??nen??."}
        return jsonify(result)


@app.route('/posts', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def posts():
    """ Vyu????va met??dy:
    'GET': Vr??ti zoznam pr??spevkov.
    'POST': Prid?? nov?? pr??spevok.
    'PUT': Uprav?? ak??ko??vek pr??spevok na z??klade id pr??spevku.
    'PATCH': Hromadne uprav?? ak??ko??vek pr??spevok.
    'DELETE': Odstr??ni ak??ko??vek pr??spevok.
    """
    if request.method == 'GET':
        posts_query = Post.query.all()
        result = posts_schema.dump(posts_query)
        return jsonify(result)

    elif request.method == 'POST':
        post_get = request.get_json()
        try:
            post_get['title']
            post_get['body']
            post_get['userId']
        except:
            result = {"Chyba": "Ch??ba 'title', 'body' alebo 'userId' pr??spevku."}
            return jsonify(result)
        else:
            post_get_title = post_get['title']
            post_get_body = post_get['body']
            post_get_userId = post_get['userId']

        if post_get_title and post_get_userId:
            post_query = Post(title = post_get_title, body = post_get_body, userId = post_get_userId)

            db.session.add(post_query)
            db.session.commit()

            result = {"??spech": f"??l??nok >>{post_get_title}<< bol pridan??."}
            return jsonify(result)

        result = {"Chyba": "Bu?? je autor nezn??my, alebo titulok ??l??nku je pr??zdny."}
        return jsonify(result)

    elif request.method == 'PUT':
        post_get = request.get_json()
        try:
            post_get['id']
            post_get['title']
            post_get['body']
            post_get['userId']
        except:
            result = {"Chyba": "Ch??ba 'id', 'title', 'body' alebo 'userId' pr??spevku, m????e by?? aj '' alebo 0."}
            return jsonify(result)
        else:
            post_get_id = post_get['id']
            post_get_title = post_get['title']
            post_get_body = post_get['body']
            post_get_userId = post_get['userId']

        if post_get_id:
            post_query = Post.query.filter_by(id = post_get_id).first()

            if post_get_title:
                post_query.title = post_get_title

            if post_get_body:
                post_query.body = post_get_body

            if post_get_userId:
                post_query.userId = post_get_userId

            db.session.commit()

            post_query = Post.query.filter_by(id = post_get_id).first()
            return post_schema.jsonify(post_query)

        result = {"Chyba": "Neviem ktor?? pr??spevok m??m upravi??, zadaj 'id' pr??spevku."}
        return jsonify(result)

    elif request.method == 'PATCH': # AttributeError: 'list' object has no attribute 'title' -> prida?? cyklus
        post_get = request.get_json()
        try:
            post_get['what']
            post_get['from']
            post_get['to']
        except:
            result = {"Chyba: Ch??ba 'what' => ('id', 'title', 'body', 'userId'), 'from' => (z ??oho) alebo 'to' => (na ??o) pr??spevku."}
            return jsonify(result)
        else:
            post_get_what = post_get['what']
            post_get_from = post_get['from']
            post_get_to = post_get['to']
            print(post_get_what)
            print(post_get_from)
            print(post_get_to)

        # if post_get_what and post_get_from and post_get_to:
        #     if post_get_what == 'id':
        #         posts_query = Post.query.filter_by(id = post_get_from).all()
        #         posts_query.id = post_get_to

        #         db.session.commit()

        #         posts_query = Post.query.filter_by(id = post_get_to).all()
        #         result = posts_schema.dump(posts_query)
        #         return jsonify(result)

        #     elif post_get_what == 'title':
        #         posts_query = Post.query.filter_by(title = post_get_from).all()
        #         posts_query.title = post_get_to

        #         db.session.commit()

        #         posts_query = Post.query.filter_by(title = post_get_to).all()
        #         result = posts_schema.dump(posts_query)
        #         return jsonify(result)

        #     elif post_get_what == 'body':
        #         posts_query = Post.query.filter_by(body = post_get_from).all()
        #         posts_query.body = post_get_to

        #         db.session.commit()

        #         posts_query = Post.query.filter_by(body = post_get_to).all()
        #         result = posts_schema.dump(posts_query)
        #         return jsonify(result)

        #     elif post_get_what == 'userId':
        #         posts_query = Post.query.filter_by(userId = post_get_from).all()
        #         posts_query.userId = post_get_to

        #         db.session.commit()

        #         posts_query = Post.query.filter_by(userId = post_get_to).all()
        #         result = posts_schema.dump(posts_query)
        #         return jsonify(result)

        result = {"Chyba": "Ch??ba 'what' => ('id', 'title', 'body', 'userId'), 'from' => (z ??oho) alebo 'to' => (na ??o) pr??spevku."}
        return jsonify(result)

    elif request.method == 'DELETE':
        post_get = request.get_json()
        try:
            post_get['id']
        except:
            result = {"Chyba: Ch??ba 'id' pr??spevku."}
            return jsonify(result)
        else:
            post_get_id = post_get['id']

        post_query = Post.query.filter_by(id = post_get_id).first()

        if post_query is None:
            result = {"Chyba": f"Pr??spevok >>{post_get}<< nie je v datab??ze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"??spech": f"Pr??spevok >>{post_query.title}<< bol ??spe??ne odstr??nen??."}
        return jsonify(result)


@app.route('/users/<userId>', methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def user(userId):
    """ Vyu????va met??dy:
    'GET': Vr??ti u????vate??a na z??klade userId.
    'POST': Zavol?? funkciu na zmenu u????vate??sk??ch ??dajov pre HTML.
    'PUT': Uprav?? ??daje u????vate??a.
    'PATCH': Uprav?? ??daje u????vate??a.
    'DELETE': Odstr??ni u????vate??a ale nie jeho ??l??nky.
    """
    if request.method == 'GET':
        user_query = User.query.filter_by(id = userId).first()
        return user_schema.jsonify(user_query)

    elif request.method == 'POST':
        result = {"Info": "Met??da zatia?? nie je definovan??."}
        return jsonify(result)

    elif request.method == 'PUT':
        user_get = request.get_json()
        try:
            user_get['name']
        except:
            result = {"Chyba: Ch??ba 'name' u????vate??a."}
            return jsonify(result)
        else:
            user_get_name = user_get['name']

        user_query = User.query.filter_by(name = user_get_name).first()

        if user_query is None and userId:
            user_query = User.query.filter_by(id = userId).first()
            if user_query:
                user_query.name = user_get_name

                db.session.commit()

            user_query = User.query.filter_by(id = userId).first()
            return user_schema.jsonify(user_query)

        result = {"Chyba": f"Meno u????vate??a >>{user_get_name}<< u?? je v datab??ze."}
        return jsonify(result)

    elif request.method == 'PATCH':
        result = {"Info": "Met??da zatia?? nie je definovan??."}
        return jsonify(result)

    elif request.method == 'DELETE':
        user_query = User.query.filter_by(id = userId).first()

        if user_query is None:
            result = {"Chyba": f"U????vate?? >>{userId}<< nie je v datab??ze."}
            return jsonify(result)

        db.session.delete(user_query)
        db.session.commit()

        result = {"??spech": f"U????vate?? >>{user_query.name}<< bol ??spe??ne odstr??nen??."}
        return jsonify(result)


@app.route('/users/<userId>/posts', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def user_posts(userId):
    """ Vyu????va met??dy:
    'GET': Vr??ti zoznam v??etk??ch pr??spevkov na z??klade userId.
    'POST': Prid?? nov?? pr??spevok do datab??zy a vr??ti titulok pr??spevku. Titulok mus?? by?? vyplnen??!
    'PUT': Uprav?? pr??spevok u????vate??a.
    'DELETE': Odstr??ni pr??spevok u????vate??a.
    """
    if request.method == 'GET':
        posts_query = Post.query.filter_by(userId = userId).all()
        result = posts_schema.dump(posts_query)
        return jsonify(result)

    elif request.method == 'POST':
        post_get = request.get_json()
        try:
            post_get['title']
            post_get['body']
        except:
            result = {"Chyba": "Ch??ba 'title' alebo 'body' pr??spevku."}
            return jsonify(result)
        else:
            post_get_title = post_get['title']
            post_get_body = post_get['body']

        post_query = Post(title = post_get_title, body = post_get_body, userId = userId)

        db.session.add(post_query)
        db.session.commit()

        result = {"??spech": f"??l??nok >>{post_get_title}<< bol pridan??."}
        return jsonify(result)

    elif request.method == 'PUT':
        post_get = request.get_json()
        try:
            post_get['id']
            post_get['title']
            post_get['body']
        except:
            result = {"Chyba: Ch??ba 'id', 'title' alebo 'body' pr??spevku."}
            return jsonify(result)
        else:
            post_get_id = post_get['id']
            post_get_title = post_get['title']
            post_get_body = post_get['body']

        post_query = Post.query.filter_by(id = post_get_id, userId = userId).first()

        if post_query is None:
            result = {"Chyba": f"V repozit??ri u????vate??a >>{userId}<< sa nenach??dza pr??spevok s identifik??torom >>{post_get_id}<<."}
            return jsonify(result)

        if post_get_title:
            post_query.title = post_get_title

        if post_get_body:
            post_query.body = post_get_body

        db.session.commit()

        post_query = Post.query.filter_by(id = post_get_id).first()
        return post_schema.jsonify(post_query)

    elif request.method == 'DELETE':
        post_get = request.get_json()
        try:
            post_get['id']
        except:
            result = {"Chyba: Ch??ba id pr??spevku."}
            return jsonify(result)
        else:
            post_get_id = post_get['id']

        post_query = Post.query.filter_by(id = post_get_id, userId = userId).first()

        if post_query is None:
            result = {"Chyba": f"Pr??spevok >>{post_get}<< nepatr?? u????vate??ovi >>{userId}<< alebo nie je v datab??ze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"??spech": f"Pr??spevok >>{post_get_id}<< bol ??spe??ne odstr??nen??."}
        return jsonify(result)


@app.route('/posts/<id>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def post(id):
    """ Vyu????va met??dy:
    'GET': Vr??ti pr??spevok na z??klade id.
    'POST': Met??da zatia?? nie je definovan??.
    'PUT': Uprav?? pr??spevok na z??klade id.
    'DELETE': Odstr??ni pr??spevok.
    """
    if request.method == 'GET':
        post = Post.query.get(id)
        return post_schema.jsonify(post)

    elif request.method == 'POST':
        result = {"Info": "Met??da zatia?? nie je definovan??."}
        return jsonify(result)

    elif request.method == 'PUT':
        post_get = request.get_json()
        try:
            post_get['title']
            post_get['body']
            post_get['userId']
        except:
            result = {"Chyba: Ch??ba 'title', 'body' alebo 'userId' pr??spevku."}
            return jsonify(result)
        else:
            post_get_title = post_get['title']
            post_get_body = post_get['body']
            post_get_userId = post_get['userId']

        post_query = Post.query.filter_by(id = id).first()

        if post_get_title:
            post_query.title = post_get_title

        if post_get_body:
            post_query.body = post_get_body

        if post_get_userId:
            post_query.userId = post_get_userId

        db.session.commit()

        post_query = Post.query.filter_by(id = id).first()
        return post_schema.jsonify(post_query)

    elif request.method == 'DELETE':
        post_query = Post.query.filter_by(id = id).first()

        if post_query is None:
            result = {"Chyba": f"Pr??spevok >>{id}<< nie je v datab??ze."}
            return jsonify(result)

        db.session.delete(post_query)
        db.session.commit()

        result = {"??spech": f"Pr??spevok >>{post_query.title}<< bol ??spe??ne odstr??nen??."}
        return jsonify(result)


# Run Server
if __name__ == '__main__':
    app.run(debug = False)
