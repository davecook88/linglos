from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, Form
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Required, NoneOf
from app.models import User, Word
from flask_login import current_user

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	native_language = SelectField('Native Language',
		choices = [("en","English"),("es","Spanish"),("de","German"),("fr","French"),("pt", "Portuguese")],
		validators = [Required()])
	target_language = SelectField('What language are you studying?',
		choices = [("en","English"),("es","Spanish"),("de","German"),("fr","French"),("pt", "Portuguese")],
		validators = [Required()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different Username')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address')

class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	submit = SubmitField('Request password reset')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Request password reset')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
	submit = SubmitField('Submit')

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm,super).__init__(*args,**kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username'	)

class PostForm(FlaskForm):
	post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
	submit = SubmitField('Submit')

class AddNewWordForm(FlaskForm):
	word = StringField('Add a new word to your list', validators=[DataRequired()])
	submit = SubmitField('Add')

	#def validate_word(self,word):
		#print(self.word.data)
		#w = current_user.words_learned_list.filter(Word.body == self.word.data).first()
		#if w is not None:
			#raise ValidationError('Word already in learning list')
