from data import db_session


def create_admin():
    from data.admins import AdminRole
    with db_session.create_session() as db_sess:
        ad = AdminRole()
        ad.login = 'login'
        ad.password = 'password'
        db_sess.add(ad)
        db_sess.commit()
