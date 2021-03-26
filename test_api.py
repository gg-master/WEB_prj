from datetime import datetime

from requests import get, put, post, delete
import pprint

# print(pprint.pprint(post('http://localhost:5000/api/films', json={
#     'title': '123', 'actors': 'asda', 'producer': '123', 'duration': 111,
#     'genres': ['путин', 'ТРАМП']}).json()))
# pprint.pprint(get('http://localhost:5000/api/films').json())
data = get('http://localhost:5000/api/films/2').json()
data['film']['duration'] = 189
pprint.pprint(data)
pprint.pprint(put('http://localhost:5000/api/films/2',
              json=data['film']).json())
# print(datetime.now().month)
