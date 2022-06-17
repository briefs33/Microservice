
from dataclasses import field
from email.policy import strict
from turtle import title
from flask import Flask, redirect, render_template, request, jsonify
import requests
import json
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
# import os


# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])
# 16.6 1:15PM - 2:45PM (1h 30min) [pridanie zobrazenia príspevkov podla uzivatela]
# 16.6 6:00PM - 7:15 (1h 15 min)
# 17.6 8:00AM - 11:30 (3h 30min +- 30min)
# 17.6 12:30PM - 
#
#
#
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
#
#
#
# """


# Init app
app = Flask(__name__)
# basedir = os.path.abspath(os.path.dirname(__file__))
posts_objekt_json, users_objekt_json = [], []
api_url = 'https://mockend.com/briefs33/Microservice'
posts_objekt_json = requests.get(api_url + '/posts')
users_objekt_json = requests.get(api_url + '/users')
# for x, y in objekt_json.items():
#     print(x, y)
# posts_dict = objekt_json.json()
posts_dict = posts_objekt_json.json()
users_dict = users_objekt_json.json()

# id = int(users_dict[-1]['id'])
# thisdict = {
#     "id": id,
#     "title": "post101",
#     "body": "pridaný post101",
# }
# # posts_dict += ', {}'.format(thisdict) # posts_dict.append(thisdict)

# posts_dict.append(thisdict)

# for d in posts_dict:
# # #     # for a, b in x.items():
# # #     #     print(a, b)
#     print({'id': d['id'], 'title': d['title'], 'body': d['body']})
# for d in users_dict:
# # #     # for a, b in x.items():
# # #     #     print(a, b)
#     print({'id': d['id'], 'name': d['name']})

# #     print({'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']})
#     print(d['id'], int(d['id']), 5)
#     if int(d['id']) == 98:
#         print('.....Toto!')

# Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
# db = SQLAlchemy(app)

# Init ma
# ma = Marshmallow(app)

# # Post Class/Model
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     title = db.Column(db.String(120))
#     body = db.Column(db.String(600))
#     userId = db.Column(db.Integer, foreign_key = True)

#     def __init__(self) -> None:
#         super().__init__()
#     # def __init__(self, title, body, userId)
#         # self.title = title
#         # self.body = body
#         # self.userId = userId

# # User Class/Model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(60))

# # Post Schema
# class PostSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'title', 'body', 'userId')

# # Init schema
# post_schema = PostSchema(strict = True)
# posts_schema = PostSchema(many = True, strict = True)
# """
# python cls:
#     >>> from app import db
#     >>> db.create_all()
# """


# Run Server
# if __name__ == '__main__':
#     app.run(debug = True)




@app.route('/')
def index():
    """ Domovská stránka """
    message = request.args.get("message", "None")
    # if not message:
    #     message = "None"
    return render_template("index.html", message = message)


@app.route('/posts', methods = ['GET'])
def get_posts():
    """ Zobrazenie príspevkov
    - na základe id alebo userId """
    # output = {}
    # output['posts'] = posts_dict
    # return output
    return {'posts': posts_dict}
    # posts = Post.query.all()
    # result = posts_schema.dump(all_posts)
    # return jsonify(result.data)


@app.route('/posts/<id>', methods = ['GET'])
def get_post(id):
    """ Zobrazenie príspevku
    - na základe id
    - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
      (platné iba pre vyhľadávanie pomocou id príspevku) """
    # output = {}
    # for d in posts_dict:
    #     if int(d['id']) == int(id):
    #         output['post{}'.format(d['id'])] = {'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']}
    # return output
    for d in posts_dict:
        if int(d['id']) == int(id):
            return d
            # return {'post{}'.format(d['id']): {'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']}}

    # post = Post.query.get(id)
    # return post_schema.jsonify(post)
    return {'Chyba': 404}


@app.route('/users/<userId>/posts', methods = ['GET'])
def get_user_posts(userId):
    """ Zobrazenie príspevku
    - na základe userId
    - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
      (platné iba pre vyhľadávanie pomocou id príspevku) """
    # userId = request.args.get("userId")
    output = {}
    for d in posts_dict:
        if int(d['userId']) == int(userId): # upravuje poradie príspevkov
             output['post{}'.format(d['id'])] = d

    # posts = Post.query.get(userId)
    # result = posts_schema.dump(posts)
    # return jsonify(result.data)
    return output


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

    if not title or not body:
       return render_template("failure.html")

    # new_post = Post(title, body, userId)
    #
    # db.session.add(new_post)
    # db.session.commit()
    # 
    # return post_schema.jsonify(new_post)

    posts_dict.append(thisdict)
    return redirect("/posts")


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
    post = get_post(id)
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
