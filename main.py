"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, render_template, url_for, Response, redirect, make_response, request, jsonify, abort
# import requests failed miserably!
import logging
import urllib2
import random
import requests

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
global g_GuessedWord
global g_GuessedWordState
global g_CountDownToLost
global g_MaxLostNum
global g_CounterOfLose
global g_CounterOfWin
g_CountDownToLost = 0
g_GuessedWord = ''
g_GuessedWordState = []
g_MaxLostNum = 8
g_CounterOfLose = 0
g_CounterOfWin = 0

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def getNewGame():
	global g_GuessedWord
	global g_GuessedWordState
	global g_CountDownToLost
	del g_GuessedWordState[:]
	g_CountDownToLost = 0
	zeSiteRequest = urllib2.urlopen('https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain')
	zeListOfWords = zeSiteRequest.read().rsplit('\n')
	zeRandNum = random.randint(0, len(zeListOfWords))
	g_GuessedWord = zeListOfWords[zeRandNum]
	g_GuessedWord = g_GuessedWord.upper()
	logging.info("g_GuessedWord: " + g_GuessedWord)
	for num in range(0,len(g_GuessedWord)):
		g_GuessedWordState.append("_")
	return jsonify(word_length=len(g_GuessedWord))
	
@app.route('/check_letter',methods=['POST', 'GET'])
def checkLetter():
	if request.method == 'GET':
		# return redirect('https://http.cat/400', 302)
		abort(400)
	global g_GuessedWord
	global g_GuessedWordState
	global g_CountDownToLost
	global g_MaxLostNum
	zeRequestJson = request.get_json()
	zeGuessLetter = zeRequestJson.get('guess')
	zeState = "ONGOING"
	if zeGuessLetter is None or (not isinstance(zeGuessLetter,basestring)) or len(zeGuessLetter) > 1 or not zeGuessLetter.isalpha():
		abort(400)
	zeCheckWhetherIsTrue = False
	logging.info("zeGuessLetter: " + zeGuessLetter)
	for num in range(0,len(g_GuessedWord)):
		if (zeGuessLetter == g_GuessedWord[num]):
			g_GuessedWordState[num] = zeGuessLetter
			zeCheckWhetherIsTrue = True
	zeGuessWordState = "".join(g_GuessedWordState)
	logging.info("Ze GuessWordState: " + zeGuessWordState)
	if zeCheckWhetherIsTrue == False:
		g_CountDownToLost += 1
		if g_CountDownToLost == g_MaxLostNum:
			zeState = "LOSE"
	elif (g_GuessedWord == zeGuessWordState):
		zeState = 'WIN'
	
	if zeState == 'WIN':
		global g_CounterOfWin
		g_CounterOfWin += 1
		return jsonify(game_state=zeState,word_state=zeGuessWordState)
	elif zeState == 'LOSE':
		global g_CounterOfLose
		g_CounterOfLose += 1
		return jsonify(game_state=zeState,word_state=zeGuessWordState,answer=g_GuessedWord)
	else:
		return jsonify(game_state=zeState,word_state=zeGuessWordState,bad_guesses=g_CountDownToLost)

@app.route('/score',methods=['GET'])
def getScore():
	global g_CounterOfLose
	global g_CounterOfWin
	return jsonify(games_won=g_CounterOfWin, games_lost=g_CounterOfLose)

@app.route('/score',methods=['DELETE'])
def resetScore():
	global g_CounterOfLose
	global g_CounterOfWin
	g_CounterOfLose = 0
	g_CounterOfWin = 0
	return getScore()

@app.errorhandler(404)
def page_not_found(e):
	return redirect('https://http.cat/404')

@app.errorhandler(400)
def page_forbidden(e):
	return redirect('https://http.cat/400')

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error because I messed up: {}'.format(e), 500
