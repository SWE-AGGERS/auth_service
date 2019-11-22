import datetime

from auth_service.database import User

def restart_db_tables(db, app):
    with app.app_context():
        db.init_app(app)
        db.drop_all(app=app)
        db.create_all(app=app)

        example = User()
        example.firstname = 'Admin'
        example.lastname = 'Admin'
        example.email = 'example@example.com'
        example.dateofbirth = datetime.datetime(2020, 10, 5)
        example.is_admin = True
        example.set_password('admin')
        db.session.add(example)
        db.session.commit()


def delete_all_db(db, app):
    with app.app_context():
        db.init_app(app)
        db.drop_all(app=app)
        db.create_all(app=app)
