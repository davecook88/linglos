from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, app
from hashlib import md5
from time import time
from sqlalchemy.schema import UniqueConstraint
import jwt

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
	)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	unix = db.Column(db.Integer)
	payment_date = db.Column(db.DateTime, default=datetime.utcnow)
	username = db.Column(db.String(64), db.ForeignKey('user.username'))
	last_name = db.Column(db.String(30))
	payment_gross = db.Column(db.Float)
	payment_fee = db.Column(db.Float)
	payment_net = db.Column(db.Float)
	payment_status = db.Column(db.String(15))
	txn_id = db.Column(db.String(25))


class Word(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(25))
	word_type = db.Column(db.String(15))
	definitions = db.relationship('Definitions', backref='word', lazy='dynamic')
	sentences = db.relationship('Sentences', backref='word', lazy='dynamic')
	synonyms = db.relationship('Synonyms', backref='word', lazy='dynamic')
	translations = db.relationship('Translations', backref='word', lazy='dynamic')
	language_pair = db.Column(db.String(4))

	def get_everything_as_dict(self):
		defs = db.session.query(Definitions.body).filter(Definitions.word_id == self.id).all()
		sents = db.session.query(Sentences.body).filter(Sentences.word_id == self.id).all()
		trans = db.session.query(Translations.body).filter(Translations.word_id == self.id).all()
		syns = db.session.query(Synonyms.body).filter(Synonyms.word_id == self.id).all()
		e={
			'translations':trans,
			'sentences':sents,
			'synonyms':syns,
			'definitions':defs
		}
		return e

class UserWordList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
	last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	level = db.Column(db.Integer, default=0)
	__table_args__ = (UniqueConstraint('user_id', 'word_id', name='_user_word_uc'),
                     )
	last_exercise = db.Column(db.String(10))
	user_translations = db.Column(db.String(200	))

	def level_up(self, points, game_type):
		self.level = self.level + points
		self.last_seen = datetime.utcnow()
		self.last_exercise = game_type

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Sentences(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(500))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
	region = db.Column(db.String(25))

class Definitions(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(500))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
	domain = db.Column(db.String(25))
	register = db.Column(db.String(25))

class Synonyms(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))

class Translations(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
	body = db.Column(db.String(25))
	language = db.Column(db.String(2))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
	)
	points = db.Column(db.Integer)
	native_language = db.Column(db.String(2))
	target_language = db.Column(db.String(2))
	calls_this_month = db.Column(db.Integer)
	max_calls_per_month = db.Column(db.Integer, default=50)
	last_call = db.Column(db.DateTime)

	studied_this_session = []

	def max_calls_reached(self):
		if calls_this_month >= max_calls_per_month:
			return True
		return False

	def increment_max_calls(self, calls):
		self.max_calls_per_month += calls

	def reset_calls(self):
		self.calls_this_month = 0

	#THIS NEEDS WORKING OUT. Both of the above attributes should be represented by the function below
	def get_wordlist(self):
		l = (db.session.query(
			Word.id,Word.body,UserWordList.last_seen,UserWordList.level)
			.join(UserWordList, Word.id == UserWordList.word_id)
			.filter(UserWordList.user_id == self.id))
		return l

	def get_wordlist_objects(self):
		l = (db.session.query(Word,UserWordList)
			.filter(Word.id == UserWordList.word_id)
			.filter(UserWordList.user_id == self.id))
		return l

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

	def avatar(self,size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self,user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
		{'reset_password':self.id, 'exp':time() + expires_in},
		app.config['SECRET_KEY'],algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id=jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

	def add_word_to_study_list(self, word):
		new_word = UserWordList(user_id=self.id,word_id=word.id,level=0)
		db.session.add(new_word)
		db.session.commit()
