import app
import requests
import json
from app.models import User, Word, Sentences, Synonyms, Translations, Definitions, UserWordList
from app import db
from flask_login import current_user
from flask import flash


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

def add_new_word(app,text, languages):
	global native_language;
	global target_language;
	global user_id;
	native_language = languages[0]
	target_language = languages[1]
	user_id = languages[2]
	with app.app_context():
		#word = Word.query.filter_by(body=text).first()
		word = Word(body=text)
		db.session.add(word)
		db.session.commit()
		word = Word.query.filter_by(body=text).first()
		b1=add_sentences(word)
		b2=add_definitions(word)
		b3=add_translations(word)
		b4=add_synonyms(word)
		if b1 or b2 or b3 or b4:
			print('{} has been successfully added to database. Add to list now.'.format(text))
		else:
			print('{} is not available in the dictionary.'.format(text))
		new_word = UserWordList(user_id=user_id, word_id=word.id)
		db.session.add(new_word)
		db.session.commit()

def Call_API(search_term, **kwargs):
	print("------------call_api---------------------")
	extra_parameter = kwargs.get("extra_parameter", "")
	if extra_parameter != "":
		extra_parameter = "/" + extra_parameter
	baseURL = "https://od-api.oxforddictionaries.com/api/v1/entries/%s/%s%s" % (target_language,search_term,extra_parameter)
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

def add_sentences(word):
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

def add_definitions(word):
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

def add_synonyms(word):
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

def add_translations(word):
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
