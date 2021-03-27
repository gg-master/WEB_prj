from datetime import datetime

from requests import get, put, post, delete
import pprint

# print(pprint.pprint(post('http://localhost:5000/api/films', json={
#     'title': '123', 'actors': 'asda', 'producer': '123', 'duration': 111,
#     'genres': ['путин', 'ТРАМП']}).json()))
# pprint.pprint(get('http://localhost:5000/api/films').json())
data = get('http://localhost:5000/api/film_sessions/1').json()
data['film_sess']['price'] = 200
pprint.pprint(data)
pprint.pprint(put('http://localhost:5000/api/film_sessions/1',
              json=data['film_sess']).json())
# print(post('http://localhost:5000/api/film_sessions', json={'film_id': 1,
#                                                             'hall_id': 1,
#                                                             'places': '01' * 25,
#                                                             'price': 250}).json())
# pprint.pprint(get('http://localhost:5000/api/film_sessions').json())
# pprint.pprint(get('http://localhost:5000/api/film_sessions/1').json())
# pprint.pprint(delete('http://localhost:5000/api/film_sessions/2').json())
# print(datetime.now().month)
