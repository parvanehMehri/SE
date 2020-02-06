from hashlib import md5
from datetime import datetime
from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin , db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    img_url = db.Column(db.String(140))
    friends = db.Column(db.String(140)) # we can split friend's ids with ',' to achieve user's friends
    enrollments = db.relationship('Enrollment', backref='related_user', lazy='dynamic')
    posts = db.relationship('Post', backref='user_for_post', lazy='dynamic')  #all posets that this user send or receive are here

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def add_friend(self , id):
        self.friends = self.friends + str(id) + ','

    def get_friend(self ):
        frnds = self.friends.split(',')
        frnds.remove(frnds[len(frnds) - 1])
        int_frnds = []
        for f in frnds:
            int_frnds.append(int(f))
        return int_frnds  # return a list of user's friends's ids

    def set_img_url(self):
        if self.email is not None:
            self.img_url = 'https://www.gravatar.com/avatar/'+md5(self.email.encode()).hexdigest()+'?d=identicon'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    send_receive = db.Column(db.Boolean, index=True, default=True)  #True for receiver and False for sender
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    description = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    img_url = db.Column(db.String(140))
    enrollments = db.relationship('Enrollment', backref='related_course', lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.name)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    state = db.Column(db.Boolean)  # True for enroll(User Courses) and False for read later(User Goals)

    def __repr__(self):
        return '<Enrollment {}>'.format(self.course_id , self.user_id , self.state)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))