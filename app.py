import os
from flask import Flask, redirect, render_template, request, jsonify
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
user_session = {"json": "false", "userId": "", "name": ""}


# GET Routes
@app.route('/', methods = ['GET'])
def index():
    """ Vráti domovskú stránku. """
    message = user_session.get("json")
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


@app.route('/users/<userId>', methods = ['GET'])
def get_user(userId):
    """ Vráti užívateľa na základe userId. """
    user = User.query.filter_by(id = userId).first()
    return render_template("user.html", user = user)


@app.route('/posts', methods = ['GET'])
def get_posts():
    """ Vráti zoznam všetkých príspevkov. """
    posts = Post.query.all()
    result = posts_schema.dump(posts)
    return render_template("posts.html", posts = result)


@app.route('/posts/<id>', methods = ['GET'])
def get_post(id):
    """ Vráti príspevok na základe id. """
    post = Post.query.get(id)
    return render_template("post.html", post = post)


@app.route('/users/<userId>/posts', methods = ['GET'])
def get_user_posts(userId):
    """ Vráti zoznam všetkých príspevkov na základe userId. """
    posts = Post.query.filter_by(userId = userId).all()
    result = posts_schema.dump(posts)
    return render_template("posts.html", posts = result)


@app.route('/users/<userId>/new_post', methods=['GET'])
def new_post(userId):
    """ Vráti formulár pre napísanie nového článku. """
    return render_template("new_post.html", userId = userId)


@app.route('/users/<userId>/delete', methods=['GET'])
def del_user(userId):
    """ Zavolá funkciu pre odstránenie užívateľa a jeho článkov. """
    return delete_user(userId)


@app.route('/posts/<id>/delete', methods=['GET'])
def del_post(id):
    """ Zavolá funkciu pre odstránenie príspevku. """
    return delete_post(id)


# POST Routes
@app.route('/', methods = ['POST'])
def signin():
    """ Po úspešnom prihlásení užívateľa vráti domovskú stránku. """
    name = request.form.get("name", "None")
    user = User.query.filter_by(name = name).first()

    if user is not None:
        user_session['name'] = user.name
        user_session['userId'] = user.id
    else:
        user_session['name'] = ""
        user_session['userId'] = ""
    return render_template("index.html", message = user_session)


@app.route('/register', methods=['POST'])
def add_user():
    """ Pridá nového užívateľa do databázy """
    name = request.form.get("name")
    if not name:
        return render_template("registration.html?chyba=no_name")

    new_user = User(name = name)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<userId>/posts', methods=['POST'])
def add_post(userId):
    """ Pridá nový článok do databázy """
    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body or not userId:
       return render_template("new_post.html?chyba=no_title_or_body_or_who_you_are")

    new_post = Post(title = title, body = body, userId = userId)

    db.session.add(new_post)
    db.session.commit()

    return redirect("/posts")


@app.route('/users/<userId>', methods=['POST'])
def update_user(userId):
    """ Zavolá funkciu na zmenu užívateľských údajov. """
    name = request.form.get("name")

    return patch_user(userId, name)


@app.route('/posts/<id>', methods=['POST'])
def update_post(id):
    """ Zavolá funkciu pre odstránenie príspevku. """
    title = request.form.get("title")
    body = request.form.get("body")
    userId = request.form.get("userId")

    return patch_post(id, title, body, userId)


# PATCH Routes
@app.route('/users/<userId>', methods=['PATCH'])
def patch_user(userId, name = None):
    """ Upravenie užívateľa """
    user = User.query.filter_by(id = userId).first()

    user.name = name

    db.session.commit()

    return redirect(f"/users/{userId}")


@app.route('/posts/<id>', methods=['PATCH'])
def patch_post(id, title = None, body = None, userId = None):
    """ Upravenie príspevku """
    post = Post.query.filter_by(id = id).first()

    if title is not None:
        post.title = title
    if body is not None:
        post.body = body
    if userId is not None:
        post.userId = userId

    db.session.commit()

    return redirect(f"/posts/{id}")


# DELETE Routes
@app.route('/users/<userId>', methods=['DELETE'])
def delete_user(userId):
    """ Odstráni užívateľa ale nie jeho články. """
    user = User.query.filter_by(id = userId).first()

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route('/posts/<id>', methods=['DELETE'])
def delete_post(id):
    """ Odstráni príspevok. """
    post = Post.query.filter_by(id = id).first()

    db.session.delete(post)
    db.session.commit()

    return redirect("/posts")


# Run Server
if __name__ == '__main__':
    app.run(debug = False)
