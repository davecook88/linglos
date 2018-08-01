import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') #or \
	#'sqlite:///' + os.path.join(basedir,'app.db') + '?check_same_thread=False'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = 'smtp.gmail.com' #os.environ.get('MAIL_SERVER')
	MAIL_PORT = 465 #int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = False #os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USE_SSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	OED_ID = '15c382c3'
	OED_KEY = '2f9b49469c209430a038ae9239d19c6d'
	ADMINS = ['flasktester@gmail.com']
	POSTS_PER_PAGE = 3
	LANGUAGES = ['en','es']
	CALLS_THIS_MONTH = 0
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
