from flask.ext.login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from .__init__ import db
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
import hashlib


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    #users=db.relationship('User',backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles={'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.MODERATE_COMMENTS,False),'Administrator':(0xff,False)}
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    name=db.Column(db.String(64))
    about_me=db.Column(db.Text())
    #role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    posts=db.relationship('Post',backref='author',lazy='dynamic')
    comments=db.relationship('Comment',backref='author',lazy='dynamic')
    avatar_hash=db.Column(db.String(32))

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email==current_app.config['FLASKY_ADMIN']:
                self.role=Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def can(self,permissions):
        return self.role is not None and \
               (self.role.permissions&permissions)==permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)




class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False


class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.Text)
    body=db.Column(db.Text)
    body_html = db.Column(db.Text)
    #timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id=db.Column(db.Integer,db.ForeignKey('user,id'))
    comments = db.relationship('Comment', backref='author', lazy='dynamic')


class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    disabled=db.Column(db.Boolean)
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr','acronym', 'b','code', 'em','i', 'strong']
        #target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))