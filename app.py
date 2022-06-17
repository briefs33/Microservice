
from dataclasses import field
from email.policy import strict
from turtle import title
from flask import Flask, render_template, request, jsonify
import requests
import json
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
# import os


# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])
# 16.6 1:15PM - 2:45PM (1h 30min) [pridanie zobrazenia príspevkov podla uzivatela]
# 16.6 6:00PM - 7:15 (1h 15 min)
# 17.6 8:00AM - ()
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

api_url = 'https://mockend.com/briefs33/Microservice/posts'
objekt_json = requests.get(api_url)
# for x, y in objekt_json.items():
#     print(x, y)
posts_dict = objekt_json.json()
# posts_dict = objekt_json['Posts'].json()
# users_dict = objekt_json['Users'].json()
for d in posts_dict:
# #     # for a, b in x.items():
# #     #     print(a, b)
    print({'id': d['id'], 'title': d['title'], 'body': d['body']})
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
    - na základe id alebo userId
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
    return {'Chyba': 404}
    # post = Post.query.get(id)
    # return post_schema.jsonify(post)


@app.route('/users/<userId>/posts', methods = ['GET'])
def get_user_posts(userId):
    """ Zobrazenie príspevku
    - na základe id alebo userId
    - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť
      (platné iba pre vyhľadávanie pomocou id príspevku) """
    output = {}
    for d in posts_dict:
        if int(d['userId']) == int(userId): # upravuje poradie príspevkov
             output['post{}'.format(d['id'])] = {'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']}
    return output
    # posts = Post.query.get(userId)
    # result = posts_schema.dump(posts)
    # return jsonify(result.data)


@app.route('/posts', methods=['POST'])
def add_post(title, body, userId):
# def add_post():
    """ Pridanie príspevku - potrebné validovať userID pomocou externej API """
    # post = Post(title=request.json['title'], body=request.json['body'], userId=request.json['userId'])
    id = int(posts_dict[-1]['id']) + 1
    thisdict = {
        "id": id,
        "title": title,
        "body": body,
        "userId": userId
    }
    # title = request.json['title']
    # body = request.json['body']
    # userId = request.json['userId']
    #
    # new_post = Post(title, body, userId)
    #
    # db.session.add(new_post)
    # db.session.commit()
    # 
    # return post_schema.jsonify(new_post)
    # 
    posts_dict += ', {}'.format(thisdict) # posts_dict.append(thisdict)
    return ({'id': id}, thisdict, {"Správa": "Príspevok bol pridaný."})


@app.route('/users/register', methods=['POST'])
def add_user(name):
# def add_post():
    """ Pridanie príspevku - potrebné validovať userID pomocou externej API """
    # post = Post(title=request.json['title'], body=request.json['body'], userId=request.json['userId'])
    id = int(users_dict[-1]['id']) + 1
    thisdict = {
        "id": id,
        "name": name
    }
    # name = request.json['name']
    #
    # new_user = User(name)
    #
    # db.session.add(new_user)
    # db.session.commit()
    # 
    # return user_schema.jsonify(new_user)
    # 
    users_dict += ', {}'.format(thisdict) # users_dict.append(thisdict)
    return ({'id': id}, thisdict, {"Správa": "Užívateľ bol pridaný."})


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
    return {'Chyba': "Príspevok som nenašiel!"}
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
    # 

# @app.route('/posts/<id>', methods=['PATCH'])
# def patch_post(id, title, body):
#     """ Upravenie príspevku - možnosť meniť title a body """
#     for d in posts_dict:
#         if int(d['id']) == int(id):
#             d["title"] = title
#             d["body"] = body
#             return (d, {"Správa": "Príspevok bol upravený."})
#     return {'Chyba': "Príspevok som nenašiel!"}


@app.route('/posts/<id>', methods=['DELETE'])
def delete_post(id):
    """ Odstránenie príspevku """
    post = get_post(id)
    if post == {'Chyba': 404}:
        return {'Chyba': "Príspevok som nenašiel!"}
    posts_dict.pop(id) # put_post -> for d in posts_dict: if int(d['id']) == int(id):
    return {"Správa": "Príspevok bol odstránený."}
    # post = Post.query.get(id)
    # db.session.delete(post)
    # db.session.commit()
    #
    # return post_schema.jsonify(post)







# get_post(5)

# print(data)

# def detailny_vypis_JSON():
#     # print(objekt_json, "\n")
#     for i in json.loads(objekt_json):
#         print(type(i), "\u001b[33m", json.dumps(i), "\u001b[0m", "=>", "\u001b[32;1m", i, "\u001b[0m")
#     print()
# detailny_vypis_JSON()

