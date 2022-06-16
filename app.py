
from flask import Flask
import requests
import json


# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])

app = Flask(__name__)

@app.route('/')
def index():
    return 'Python!'

api_url = 'https://mockend.com/briefs33/Microservice/posts'
objekt_json = requests.get(api_url)
# for x, y in objekt_json.items():
#     print(x, y)
posts_dict = objekt_json.json()
# for d in posts_dict:
# #     # for a, b in x.items():
# #     #     print(a, b)
# #     # print({'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']})
# #     print({'id': d['id'], 'title': d['title'], 'body': d['body'], 'userId': d['userId']})
#     print(d['id'], int(d['id']), 5)
#     if int(d['id']) == 98:
#         print('.....Toto!')

@app.route('/posts')
def get_posts(id = '', user_id = ''):
    # output = {}
    # output['posts'] = posts_dict
    # return output
    return {'posts': posts_dict}

@app.route('/posts/<id>')
def get_post(id = '', user_id = ''):
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

# get_post(5)

# print(data)

# def detailny_vypis_JSON():
#     # print(objekt_json, "\n")
#     for i in json.loads(objekt_json):
#         print(type(i), "\u001b[33m", json.dumps(i), "\u001b[0m", "=>", "\u001b[32;1m", i, "\u001b[0m")
#     print()
# detailny_vypis_JSON()

