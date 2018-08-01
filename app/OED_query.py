import app
import requests
import json
from config import Config
from app.models import User, Word, Sentences, Synonyms, Translations, Definitions, UserWordList
from app import app, db
from flask_login import current_user
from flask import flash
from threading import Thread


OED_ID = '15c382c3'
OED_KEY = '2f9b49469c209430a038ae9239d19c6d'
native_language = ""
target_language = ""
user_id = 0

def in_list_already(word_body, user):
	word_id = Word.query.filter_by(body=word_body).first().id
	UWL = UserWordList.query.filter_by(word_id=word_id).filter_by(user_id = user.id).first()
	if UWL is None:
		return False
	return True

def add_word_to_UWL(word_id):
	new_word = UserWordList(user_id=user_id, word_id=word_id)
	db.session.add(new_word)
	db.session.commit()

def add_new_word(textArray, languages): #removed app from args
	if Config.CALLS_THIS_MONTH > 2999:
		flash('Linglos has reached the limit of dictionary calls this month. Please donate to help us keep going.')
		return
	global native_language;
	global target_language;
	global user_id;
	native_language = languages[0]
	target_language = languages[1]
	user_id = languages[2]
	#with app.app_context():
		#word = Word.query.filter_by(body=text).first()
	if type(textArray) == str:
		textArray = [textArray]

	for w in textArray:
		word = Word(body=w)
		db.session.add(word)
		db.session.commit()
		word = Word.query.filter_by(body=w).first()
		t1 = Thread(target=add_sentences,args=(app,word))
		t2 = Thread(target=add_definitions,args=(app,word))
		if native_language != "ot":
			t3 = Thread(target=add_translations,args=(app,word))
			t3.start()
		t4 = Thread(target=add_synonyms,args=(app,word))
		t1.start()
		t2.start()
		t4.start()
		#b2=add_definitions(word)
		# if native_language != "ot":
		# 	b3=add_translations(word)
		# b4=add_synonyms(word)
		# if b1 or b2 or b3 or b4:
		# 	print('{} has been successfully added to database. Add to list now.'.format(text))
		# else:
		# 	print('{} is not available in the dictionary.'.format(text))
		t1.join()
		t2.join()
		t4.join()
		if native_language != "ot":
			t3.join()
		trans = word.translations.all()
		syns = word.synonyms.all()
		sents = word.sentences.all()
		defs = word.definitions.all()

		if len(trans) < 1 and len(syns) < 1 and len(defs) < 1 and len(sents) < 1:
			db.session.delete(word)
			db.session.commit()
			flash("{} not found in the dictionary".format(word.body))
			return

		print(trans,syns,sents,defs)

		if user_id != 0:
			add_word_to_UWL(word.id)
			# new_word = UserWordList(user_id=user_id, word_id=word.id)
			# db.session.add(new_word)
			# db.session.commit()

def Call_API(search_term, **kwargs):
	print("------------call_api---------------------")
	extra_parameter = kwargs.get("extra_parameter", "")
	if extra_parameter != "":
		extra_parameter = "/" + extra_parameter
	baseURL = "https://od-api.oxforddictionaries.com/api/v1/entries/%s/%s%s" % (target_language,search_term,extra_parameter)
	Config.CALLS_THIS_MONTH += 1
	print(native_language,target_language)
	print(baseURL)
	try:
		auth = {"app_id":OED_ID,"app_key":OED_KEY}
		r = requests.get(baseURL, headers=auth)
	except Exception as e:
		print(e)
	finally:
		print("Finished")

	try:
		json_result = r.json()
		print_to_file(json_result)
		return json_result
	except:
		print("No entry for {}".format(extra_parameter))
		return False

def add_sentences(app,word):
	with app.app_context():
		sentences = sentences_list(word.body)
		if sentences is None or sentences == False:
			print("---------------No sentences available-------------")
			return False
		if len(sentences) > 0:
			for s in sentences:
				sentence = Sentences(body=s['body'], region=s['region'], word_id=word.id)
				db.session.add(sentence)
				db.session.commit()
		return True

def add_definitions(app,word):
	with app.app_context():
		definitions = definitions_list(word)
		if definitions is None or definitions == False:
			print("---------------No defintions available-------------")
			return False
		if len(definitions) > 0:
			for d in definitions:
				definition = Definitions(body=d['body'],domain=d['domain'], register=d['domain'], word_id=word.id)
				db.session.add(definition)
			db.session.commit()
			return True

def add_synonyms(app,word):
	with app.app_context():
		synonyms = synonyms_antonyms_list(word)
		if synonyms is None or synonyms == False:
			print("---------------No synonyms available-------------")
			return False
		if len(synonyms) > 0:
			for s in synonyms:
				body = s['body'].replace("_", " ")
				synonym = Synonyms(body=body, word_id=word.id)
				db.session.add(synonym)
			db.session.commit()
			return True

def add_translations(app,word):
	with app.app_context():
		translations = translations_list(word, native_language)
		if translations is None or translations == False:
			print("---------------No translations available-------------")
			return False
		if len(translations) > 0:
			for t in translations:
				translation = Translations(body=t['body'],language=target_language,word_id=word.id)
				db.session.add(translation)
			db.session.commit()
			return True

def sentences_list(word):
	result = []
	print("Beginning sentences_list")
	try:
		json_result = Call_API(word, extra_parameter = "sentences")
		if json_result == False:
			return False
		lexical_entries = json_result['results'][0]['lexicalEntries'][0]['sentences']
		for lexical_entry in lexical_entries:
			sentence = lexical_entry['text']
			region = lexical_entry['regions'][0]
			result.append({
				'body' : sentence,
				'region' : region
				})
			region, sentence = "",""
		return result
	except Exception as e:
		print(e)
		return

def definitions_list(word):
	result = []
	print("Beginning definitions_list")
	json_result = Call_API(word.body)
	if json_result == False:
		return False
	set_word_type(word,json_result)
	try:
		lexical_entries = json_result['results'][0]['lexicalEntries'][0]['entries']
		for entry in lexical_entries:
			definitions = entry['senses']
			definition, domain, register = "","",""
			for sense in definitions:
				try:
					for subsense in sense['subsenses'][0]:
						definition = str(subsense['definitions'][0])
						try:
							domain = str(subsense['domains'][0])
						except:
							pass
						try:
							register = str(subsense['registers'][0])
						except:
							pass

				except:
					definition = str(sense['definitions'][0])

				try:
					domain = str(sense['domains'][0])
				except:
					pass
				try:
					register = str(sense['register'][0])
				except:
					pass
				result.append({
					'body':definition,
					'domain':domain,
					'register':register
				})
				definition, domain, register = "","",""
		return result
	except Exception as e:
		print(e)

def set_word_type(word, json):
	word_type = json['results'][0]['lexicalEntries'][0]['lexicalCategory']
	word.word_type = word_type
	db.session.commit()

def synonyms_antonyms_list(word):
	syn_ant = 'synonyms'
	json_result = Call_API(word.body, extra_parameter=syn_ant)
	if json_result == False:
		return False
	result = []
	try :
		synonyms = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]["subsenses"][0][syn_ant]
	except:
		synonyms = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0][syn_ant]
	for synonym in synonyms:
		result.append({'body':synonym['id']})
	return result

def translations_list(word, target_language):
	extra_parameter = 'translations=' + target_language
	json_result = Call_API(word.body, extra_parameter=extra_parameter)
	if json_result == False:
		return False
	print_to_file(json_result)
	result = []
	try:
		translations = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['subsenses']#(1)("translations")(count + 1)("text")
		for translation in translations:
			if 'translations' in translation:
				senses = translation['translations']
				for sense in senses:
					result.append({'body':sense['text']})
	except:
		translations = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
		for translation in translations:
			if 'translations' in translation:
				senses = translation['translations']
				for sense in senses:
					result.append({'body':sense['text']})
	return result


def print_to_file(json_result):
	file = open('json.txt','w')
	file.write(json.dumps(json_result))
	file.close()

def t():
	word = input("word")
	target_language = 'es'
	translations = t2(word, target_language)
	if len(translations) > 0:
		for t in translations:
			print(t)
			translation = Translations(body=t['body'],language=target_language)
			db.session.add(translation)
		db.session.commit()

def t2(word, target_language):
	extra_parameter = 'translations=' + target_language
	json_result = Call_API(word, extra_parameter=extra_parameter)
	print_to_file(json_result)
	result = []
	try:
		translations = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['subsenses']#(1)("translations")(count + 1)("text")
		for translation in translations:
			if 'translations' in translation:
				senses = translation['translations']
				for sense in senses:
					result.append({'body':sense['text']})
			else:
				print(translation)
	except:
		translations = json_result['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
		for translation in translations:
			if 'translations' in translation:
				senses = translation['translations']
				for sense in senses:
					result.append({'body':sense['text']})
			else:
				print(translation)
	return result

def add_word_to_study_list(oWord, user_id):
	user = User.query.filter_by(id=user_id).first_or_404()
