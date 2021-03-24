from datetime import datetime

from requests import get, put, post, delete
import pprint

# print(pprint.pprint(post('http://localhost:5000/api/films', json={
#     'title': '123', 'actors': 'asda', 'producer': '123', 'duration': 111,
#     'genres': ['путин', 'ТРАМП']}).json()))
pprint.pprint(get('http://localhost:5000/api/films').json())
# print(datetime.now().month)
