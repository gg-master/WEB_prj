# WEB_prj
Вся информация анонимизирована.
<h3>Вступление</h3>

"FilmCenter" - сайт на Flask от 3-х creative developers.

Перед нами стояла цель разработать сайт в сети интернет, 
который предоставит пользователю возможность ознакомиться с фильмами, 
которые находятся в прокате кинотеатра, а также оформить бронь одного 
или нескольких мест на сеанс выбранного фильма.

<h5>ТЗ:</h5>
1) Написать сайт с использованием Flask и RESTful-api.
2) Реализовать RESTful-api для проекта
3) Реализовать юзер и админ части проекта.

<i>Ознакомиться с подробным описанием нашего проекта, 
а также его технической составляющей можно в пояснительный записке к проекту ****
(см. файл PZ_web.docx).</i>

<h3>Запуск</h3>
<h6><a href='http://film-center-prj.herokuapp.com/'>Ознакомиться с сайтом на Heroku</a></h6>

<h5>Запуск из кода</h5>
Все необходимые библиотеки описаны в requirements.txt. <br><br>

<i><b>Чтобы запустить сайт необходимо запустить файл app.py в корне проекта.</b></i>

<i><b>Перед запуском проверьте .env файл:
1) Замените PASSWORD_EMAIL на пароль к почте, с которой будут отправляться письма
2) Замените EMAIL на email той почты, с которой будут отправляться письма</b></i> 

<small>Данный вариант нашего проекта использует бд типа SQLITE с небольшим количеством тестовых данный. 
Однако версия, которая работает на Heroku использует POSTGRESQL бд, что обусловлено 
техническими ограничениями платформы Heroku. Но несмотря на это, все функции работают стабильно.</small>

Для того, чтобы зайти в админку, необходимо ввести: логин - admin, пароль - admin.

<h3><a href='https://drive.google.com/file/d/1Mmy5mVYOe4CZ60eZ7nnObOy0k8Jy3q4p/view?usp=sharing'>Видео демонстрация работы сайта.</a></h3>
