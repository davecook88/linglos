from flask import render_template, flash, redirect
from app import app, db
from app.forms import LoginForm, RegistrationForm, \
	EditProfileForm, PostForm, ResetPasswordRequestForm, \
	ResetPasswordForm, AddNewWordForm
from app.models import User, Post, Word, UserWordList
from app.email import send_password_reset_email
from app.OED_query import add_new_word, in_list_already
from app.study import set_points
from flask_login import current_user, login_user, logout_user, login_required
from flask import Flask, url_for, request
from werkzeug.urls import url_parse
from werkzeug.datastructures import ImmutableOrderedMultiDict
from datetime import datetime
from threading import Thread
from pymysql import escape_string as thwart
import sys
import json
import random
from app import study


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
	form = AddNewWordForm()
	if form.validate_on_submit():
		if current_user.max_calls_reached():
			now = datetime.now()
			if current_user.last_call == None:
				current_user.last_call = now
				db.session.add(current_user)
				db.sesson.commit()
			if (now - current_user.last_call).days > 30:
				current_user.reset_calls()
			else:
				flash('You have reached your limit for adding words this month. Go to payment to add more.')
				return redirect(url_for('index'))
		word = thwart(form.word.data.lower().strip())
		db_word = Word.query.filter_by(body=word).first()
		langs = [current_user.native_language, current_user.target_language, current_user.id]
		if db_word is None:
			try:
				add_new_word(word,langs)
				#Thread(target=add_new_word,args=(app,word,langs)).start()
				flash('Word added to database.')
				current_user.last_call = datetime.now()
				return redirect(url_for('index'))
				#db_word = Word.query.filter_by(body=word).first()
			except Exception as e:
				print(e)
				flash(str(e))
				return redirect(url_for('index'))
		if in_list_already(word, current_user):
			flash('Word already in list')
			return redirect(url_for('index'))
		# new_word = UserWordList(user_id=current_user.id, word_id=db_word.id)
		# db.session.add(new_word)
		# db.session.commit()
		flash('Word added to list')
		return redirect(url_for('index'))
	page = request.args.get('page',1,type=int)
	return render_template('index.html', title='home', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('index.html', title='Sign In', form=form, login=True)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(
			username=thwart(form.username.data),
			email= thwart(form.email.data),
			native_language=thwart(form.native_language.data),
			target_language=thwart(form.target_language.data))
		user.set_password(thwart(form.password.data))
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form=ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(thwart(form.password.data))
		db.session.commit()
		flash('Your password has been reset')
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form, user=user)

@app.route('/test')
@login_required
def test():
	oJson = study.create_json()
	return render_template('game.html', user=current_user, oJson = oJson)

@app.route('/game')
@login_required
def game():
	if len(current_user.get_wordlist_objects().all()) < 6:
		flash("You don't have enough words in your list to study yet! Add some below.")
		return redirect(url_for('index'))
	oJson = study.create_json()
	#randomly set flip - True or False
	oJson[0]["flip"] = random.getrandbits(1)
	current_user.studied_this_session.append(oJson[1]['word_id'])
	print('-----------------studied_this_session-----------------')
	print(current_user.studied_this_session)
	try:
		return render_template('game.html', user=current_user, oJson = oJson)
	except e as Exception:
		flash(e)
		return render_template('index.html', title='home', form=form)

@app.route('/game-win', methods=['POST'])
@login_required
def game_win():
	print("----------game-win-------------")
	last_word_id = thwart(request.form['id'])
	game_type = request.form['game_type']
	game_result = request.form['result']
	print("----------request---------------")
	print("Last word id: {}, Game type:{}, Game result:{}".format(last_word_id,game_type,game_result))
	points = -1 if game_result == 'lose' else set_points(game_type)
	UWL = UserWordList.query.filter_by(id=last_word_id).first()
	if UWL is not None:
		UWL.level_up(points, game_type)
		db.session.commit()
	return str(points * 10)
	#oJson = study.create_json()
	#return render_template('game.html', user=current_user, oJson = oJson)
@app.route('/add', methods=['POST'])
@login_required
def add():
	word = thwart(request.form['word'])
	langs = [current_user.native_language, current_user.target_language, current_user.id]
	try:
		add_new_word(word,langs)
		flash("{} added to database".format(word))
		return "Word added to database"
	except:
		flash("There was a problem adding {}".format(word))
		return "There was a problem adding this word"

@app.route('/word/<word_id>', methods=['GET'])
@login_required
def word(word_id):
	form = AddNewWordForm()
	oWord = Word.query.filter_by(id=word_id).first()
	oUWL = UserWordList.query.filter_by(word_id=word_id).filter_by(user_id=current_user.id).first()
	if form.validate_on_submit():
		translation = thwart(form.word.data)
		try:
			oUWL.user_translations = oUWL.user_translations + "#" + translation
			db.session.add(oUWL)
			db.session.commit()
		except Exception as e:
			flash(e)
	return render_template('word.html', word=oWord, UserWordList=oUWL, form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page',1,type=int)
	posts = current_user.get_wordlist().all()
	# next_url=url_for('user',username=user.username,page=posts.next_num) \
	# 	if posts.has_next else None
	# prev_url=url_for('user',username=user.username,page=posts.prev_num) \
	# 	if posts.has_prev else None
	return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit profile', form=form)

@app.route('/payment')
@login_required
def payment():
	try:
		return render_template('payment.html', title='Upgrade your account', user=current_user)
	except Exception as e:
		return(str(e))

@app.route('/success')
@login_required
def success():
	try:
		return render_template("success.html")
	except Exception as e:
		return(str(e))

@app.route('/ipn/', methods=['POST'])
@login_required
def ipn():
	try:
		arg=''
		request.parameter_storage_class = ImmutableOrderedMultiDict
		values=request.form
		for x,y in values.iteritems():
			arg +='&{x}={y}'.format(x=x,y=y)

		validate_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_notify-validate{arg}' \
			.format(arg=arg)
		r = requests.get(validate_url)
		if r.text == 'VERIFIED':
			try:
				payer_email = thwart(request.form.get('payer_email'))
				unix = int(time.time())
				payment_date = thwart(request.form.get('payment_date'))
				username = thwart(request.form.get('custom'))
				last_name = thwart(request.form.get('last_name'))
				payment_gross = thwart(request.form.get('payment_gross'))
				payment_fee = thwart(request.form.get('payment_fee'))
				payment_net = float(payment_gross) - float(payment_fee)
				payment_status = thwart(request.form.get('payment_status'))
				txn_id = thwart(request.form.get('txn_id'))
			except Exception as e:
				with open('/tmp/ipnout.txt','a') as f:
					data = 'ERROR WITH IPN DATA \n'+str(values)+'\n'
					f.write(data)

			with open('/tmp/ipnout.txt','a') as f:
				data = 'SUCCESS \n'+str(values)+'\n'
				f.write(data)

			u = current_user
			p = Payment(
				unix=unix,
				payment_date=payment_date,
				payment_gross=payment_gross,
				payment_fee=payment_fee,
				payment_net=payment_net,
				payment_status=payment_status,
				txn_id=txn_id
			)
			db.session.add(p)
			db.session.commit()

	except Exception as e:
		return str(e)


@app.route('/follow/<username>')
@login_required
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} is not found.'.format(username))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user',username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}.'.format(username))
	return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You can\'t unfollow yourself.')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}'.format(user))
	return redirect(url_for('user',username=username))

@app.route('/explore')
@login_required
def explore():
	page = request.args.get('page',1,type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page,app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore',page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore',page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',
		title='Explore', posts=posts.items, next_url = next_url, prev_url=prev_url)

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
