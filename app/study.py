from app.models import User, Word, UserWordList, Translations, Synonyms
from flask_login import current_user
from app import db
from sqlalchemy import asc,desc, func
from app.OED_query import print_to_file
import datetime
import random
import json

def choose_word_game(options_list):
    correct_answer = options_list[0]


def choose_lowest_level_word():
    #word_list = current_user.words_learned_list.order_by(desc(UserWordList.level))
    #----------DELETE-------------------------------------------------------
    u = current_user#User.query.filter_by(id=1).first()
    twenty_minutes_ago=datetime.datetime.utcnow() - datetime.timedelta(minutes=20)
    word_list = u.get_wordlist_objects().filter(UserWordList.last_seen < twenty_minutes_ago).order_by(asc(UserWordList.level))
    if len(word_list.all()) < 1:
        word_list = u.get_wordlist_objects().order_by(asc(UserWordList.level))
    #---------------------------------------------------------------------
    return word_list.first()

def make_list_for_question(UWL_obj, num_of_options):
    options_list = [UWL_obj]
    u = current_user#User.query.filter_by(id=1).first()
    word_list = u.get_wordlist_objects().all()
    word_list.remove(UWL_obj)
    for i in range(num_of_options - 1):
        r = random.randint(0,len(word_list) - 1)
        new_word = word_list[r]
        options_list.append(new_word)
        word_list.remove(new_word)
    return options_list

def create_json(**kwargs):
    if not 'n' in kwargs:
        n = 4
    json_result = {}

    w = choose_lowest_level_word()
    game_type = choose_game_type(w)[0]
    n = choose_game_type(w)[1]
    l = make_list_for_question(w,n)
    json_result[0] = {}
    json_result[0]['game_type'] = game_type
    for i in range(n):
        json_result[i + 1]={}

    for i, item in enumerate(l):
        oWord = item[0]
        oUWL = item[1]

        json_result[i + 1]['word_id']=oWord.id
        json_result[i + 1]['body']=oWord.body
        json_result[i + 1]['UWL_id']=oUWL.id

        json_result[i + 1]['sentences']=[]
        for j,sentence in enumerate(oWord.sentences.all()):
            s = sentence.body
            w = oWord.body
            if " " in w:
                a = w.split()
            else:
                a = [w]
            for x in a:
                s = s.replace(x, "________")
            if s.count("________") == len(a):
                json_result[i + 1]['sentences'].append(s)

        json_result[i + 1]['definitions']=[]
        for j,definition in enumerate(oWord.definitions.all()):
            json_result[i + 1]['definitions'].append(definition.body)

        json_result[i + 1]['translations']=[]
        for j,translation in enumerate(oWord.translations.all()):
            json_result[i + 1]['translations'].append(translation.body)

        json_result[i + 1]['synonyms']=[]
        for j,synonym in enumerate(oWord.synonyms.all()):
            json_result[i + 1]['synonyms'].append(synonym.body)

    print_to_file(json_result)
    return json_result

def choose_game_type(oWord):
    game_type = 'translations'
    options = 4
    word = oWord[0]
    last_exercise= oWord[1].last_exercise
    word_level = oWord[1].level
    games = [
    'translations']

    if word_level < 8:
        game_type = 'translations'
        options = 4
    elif word_level < 15:
        game_type = 'translations'
        options = 6
    elif word_level < 20:
        game_type = 'definitions'
        options = 4
        games = [
        'translations',
        'definitions']
    elif word_level < 25:
        game_type = 'synonyms'
        options = 4
        games = [
        'translations',
        'definitions',
        'synonyms']
    else:
        game_type = "sentences"
        games = [
        'translations',
        'definitions',
        'synonyms',
        'sentences']

    if game_type == last_exercise and len(games) > 1:
        rand_num = random.randint(0,len(games) - 1)
        game_type = games[rand_num]
        options = random.randint(4,8)

    return [game_type, options]


    print(oWord_list)
    print(word.body, word_points)
    return game_type

#
# #
# # #---------------------------------------------------------
# #delete all below if JSON works out
# #---------------------------------------------------------
# def word_ids_for_questions(**kwargs):
#     if not 'n' in kwargs:
#         n = 4
#     result = []
#     w = choose_lowest_level_word()
#     l = make_list_for_question(w,n)
#     for r in l:
#         result.append(r[0].id)
#     return result
#
#
# def translation_game_data():
#     list = word_ids_for_questions()
#     print(list)
#     d = (db.session.query(Word.id, Word.body,Translations.body,UserWordList.id)
#         .filter(Word.id.in_(list))
#         .filter(Word.id == Translations.word_id)
#         .filter(Word.id == UserWordList.word_id))
#     unsorted = d.order_by(func.min(Translations.id)).group_by(Word.id)
#     results=[]
#     for n in list:
#         results.append(unsorted.filter(Word.id==n).first())
#     return results
#
# def synonym_game_data():
#     list = word_ids_for_questions()
#     print(list)
#     d = (db.session.query(Word.id, Word.body,Translations.body,UserWordList.id)
#         .filter(Word.id.in_(list))
#         .filter(Word.id == Translations.word_id)
#         .filter(Word.id == UserWordList.word_id))
#     unsorted = d.order_by(func.min(Translations.id)).group_by(Word.id)
#     results=[]
#     for n in list:
#         results.append(unsorted.filter(Word.id==n).first())
#     return results
