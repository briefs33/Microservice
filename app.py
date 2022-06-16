
from flask import Flask
import requests


app = Flask(__name__)

@app.route('/')
def index():
    return 'Python!'

api_url = 'https://mockend.com/briefs33/Microservice/posts'

# posts = requests.get(api_url)

@app.route('/posts')
def get_posts(id = '', user_id = ''):
    posts = requests.get(api_url + id)
    output = []
    for post in posts.json():
            data = {'title': post['title'], 'body': post['body']}
            output.append(data)
    return {"posts": output}

@app.route('/posts/<id>')
def get_post(id = '', user_id = ''):
    id = '/{}'.format(id)
    posts = requests.get(api_url + id)
    return {"post": {'title': posts.json()['title'], 'body': posts.json()['body']}}



# get_post(5)

