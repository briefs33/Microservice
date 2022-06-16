
from flask import Flask
import requests
import json


# 16.6 11:00AM - 12:45 (1h 45min -15min[obed])
# 16.6 1:15PM - 2:45PM (1h 30min) [pridanie zobrazenia príspevkov podla uzivatela]
# """ Zdroje:
# https://www.youtube.com/watch?v=qbLc5a9jdXo&ab_channel=CalebCurry
# https://www.w3schools.com/





# """

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
    """ Zobrazenie príspevkov
    - na základe id alebo userId """
    # output = {}
    # output['posts'] = posts_dict
    # return output
    return {'posts': posts_dict}

@app.route('/posts/<id>')
def get_post(id = '', user_id = ''):
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

@app.route('/users/<userId>/posts')
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

# """ --------------------------------------------------------------------------------------------- """
# @app.route('/posts', methods=['POST'])
# def add_post(title, body, userId):
#     """ Pridanie príspevku - potrebné validovať userID pomocou externej API """
#     # post = Post(title=request.json['title'], body=request.json['body'], userId=request.json['userId'])
#     id = int(posts_dict[-1]['id']) + 1
#     thisdict = {
#         "id": id,
#         "title": title,
#         "body": body,
#         "userId": userId
#     }
#     posts_dict += ', {}'.format(thisdict)
#     return ({'id': id}, thisdict, {"Správa": "Príspevok bol pridaný."})

# @app.route('/posts/<id>', methods=['PUT'])
# def put_post(id, title, body, userId):
#     """ Upravenie príspevku - potrebné validovať userID pomocou externej API """
#     for d in posts_dict:
#         if int(d['id']) == int(id):
#             d["title"] = title
#             d["body"] = body
#             d["userId"] = userId
#             return (d, {"Správa": "Príspevok bol upravený."})
#     return {'Chyba': "Príspevok som nenašiel!"}

# @app.route('/posts/<id>', methods=['PATCH'])
# def patch_post(id, title, body):
#     """ Upravenie príspevku - možnosť meniť title a body """
#     for d in posts_dict:
#         if int(d['id']) == int(id):
#             d["title"] = title
#             d["body"] = body
#             return (d, {"Správa": "Príspevok bol upravený."})
#     return {'Chyba': "Príspevok som nenašiel!"}

# @app.route('/posts/<id>', methods=['DELETE'])
# def delete_post(id):
#     """ Odstránenie príspevku """
#     post = get_post(id)
#     if post == {'Chyba': 404}:
#         return {'Chyba': "Príspevok som nenašiel!"}
#     posts_dict.delete(id)
#     return {"Správa": "Príspevok bol odstránený."}








# get_post(5)

# print(data)

# def detailny_vypis_JSON():
#     # print(objekt_json, "\n")
#     for i in json.loads(objekt_json):
#         print(type(i), "\u001b[33m", json.dumps(i), "\u001b[0m", "=>", "\u001b[32;1m", i, "\u001b[0m")
#     print()
# detailny_vypis_JSON()

