import requests
import json
from flask import Flask


class MyRequests():
    def __init__(self) -> None:
        self.api_url = 'https://mockend.com/briefs33/Microservice/posts'

    def get(self, id = '', user_id = ''):
        """ Retrieve data - Zobrazenie príspevku
   - na základe id alebo userId
   - ak sa príspevok nenájde v systéme, je potrebné ho dohľadať pomocou externej API a uložiť (platné iba pre vyhľadávanie pomocou id príspevku) """
        if id != '':
            id = '/{}'.format(id)
        response = requests.get(self.api_url + id)
        # print(response.json())
        for data in response.json():#['posts']
            print(data['body'])
        return response.status_code















# myRequests = MyRequests()

# print(
#     myRequests.get(),

# )


app = Flask(__name__)

@app.route('/')
def index():
    return 'Python!'

