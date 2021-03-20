import flask
import requests
from flask import jsonify, request

from data import db_session
from data.users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=(
                    'name', 'about', 'home_city', 'email', 'hashed_password'))
                    for item in users]
        }
    )


@blueprint.route('/api/users/<users_id>', methods=['GET'])
def get_one_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict(only=(
                'name', 'about', 'home_city', 'email', 'hashed_password'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'name', 'about', 'home_city', 'email',
                  'hashed_password']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()

    user = User(
        name=request.json['name'],
        about=request.json['about'],
        home_city=request.json['home_city'],
        email=request.json['email']
    )
    user.set_password(request.json['password'])
    if db_sess.query(User).filter(User.id == user.id).first():
        return jsonify({'error': 'Id already exists'})
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<users_id>', methods=['DELETE'])
def delete_users(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<users_id>', methods=['PUT'])
def edit_users(users_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'about', 'home_city', 'email',
                  'hashed_password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    user.name = request.json['name'],
    user.about = request.json['about'],
    user.home_city = request.json['home_city'],
    user.email = request.json['email']
    user.hashed_password = request.json['hashed_password']
    db_sess.commit()
    return jsonify({'success': 'OK'})

