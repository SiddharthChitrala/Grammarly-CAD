import json
from flask import Flask, render_template, request, session, url_for, redirect, flash
import ibm_db
import re
import os
import requests
# use here textblob for checking proofreading, grammar
# using textblob
from textblob import TextBlob


app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA (1).crt;UID=vts47207;PWD=g4O8mWodzytk1wMD", '', '')
print("connected")


@app.route('/home')
def Home():
    return render_template("index.html")


@app.route('/')
@app.route('/login', methods=["POST", "GET"])
def Login():
    msg = ' '

    if request.method == 'POST':
        USERNAME = request.form['username']
        PASSWORD = request.form['password']
        sql = "SELECT * FROM SIGNUP WHERE USERNAME = ? AND PASSWORD = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            session['Loggedin'] = True
            session['USERID'] = account['USERID']
            session['USERNAME'] = account['USERNAME']
            session['PASSWORD'] = account['PASSWORD']
            msg = "Logged in successfully!"
            return render_template("index.html")
        else:
            msg = "Incorrect username / Password !"
        return render_template("loginpage.html")
    return render_template("loginpage.html")


@app.route('/register', methods=['GET', 'POST'])
def Register():
    msg = ' '

    if request.method == 'POST':
        USERNAME = request.form['username']
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        sql = "SELECT * FROM SIGNUP WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists! '
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = ' Invalid email address! '
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = ' username must contain only characters and numbers! '
        else:
            sql2 = "SELECT count(*) FROM SIGNUP"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = "INSERT INTO SIGNUP VALUES(?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, USERNAME)
            ibm_db.bind_param(prep_stmt, 3, EMAIL)
            ibm_db.bind_param(prep_stmt, 4, PASSWORD)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template("loginpage.html", msg=msg)
    return render_template("register.html", msg=msg)


@app.route('/grammar', methods=['POST','GET'])
def GrammarCheck():
    if request.method == 'POST':
        text = request.form['text']
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        noun_phrases = blob.noun_phrases
        text_noun_phrases = "\n".join(noun_phrases)
        print(text_noun_phrases)
        print(sentiment)
        print(noun_phrases)
     
        insert_sql = "INSERT INTO GRAMMAR VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, text)
        ibm_db.bind_param(prep_stmt, 2, blob)
        ibm_db.bind_param(prep_stmt, 3, sentiment)
        ibm_db.bind_param(prep_stmt, 4, noun_phrases)
        ibm_db.execute(prep_stmt)
        return render_template('Grammarcheck.html', sentiment=sentiment, noun_phrases=noun_phrases)
    return render_template('Grammarcheck.html')


@app.route('/summarise', methods=['POST','GET'])
def summarise():

    if request.method == 'POST':
        text = request.form['text']
        num_sentences = int(request.form['num_sentences'])

        url = "https://gpt-summarization.p.rapidapi.com/summarize"

        payload = {
            "text": text,
            "num_sentences": num_sentences
        }

        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "ad8dd9e205msh1b46ee7d2f5246fp145c0bjsn4f9d4d717193",
            "X-RapidAPI-Host": "gpt-summarization.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)
        summary = response.json()
        print(summary)
        insert_sql = "INSERT INTO SUMMARY VALUES (?,?,?)"
        stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(stmt, 1, text)
        ibm_db.bind_param(stmt, 2, num_sentences)
        ibm_db.bind_param(stmt, 3, summary)
        ibm_db.execute(stmt)
        return render_template("Summarise.html", summary=summary)
    return render_template("Summarise.html")


@app.route('/Spell', methods=['POST','GET'])
def Spelling():

    if request.method == 'POST':

        fieldvalues = request.form['fieldvalues']
        url = "https://jspell-checker.p.rapidapi.com/check"

        payload = {
            "language": "enUS",
            "fieldvalues": fieldvalues,
            "config": {
                "forceUpperCase": False,
                "ignoreIrregularCaps": False,
                "ignoreFirstCaps": True,
                "ignoreNumbers": True,
                "ignoreUpper": False,
                "ignoreDouble": False,
                "ignoreWordsWithNumbers": True
            }
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "ad8dd9e205msh1b46ee7d2f5246fp145c0bjsn4f9d4d717193",
            "X-RapidAPI-Host": "jspell-checker.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        response_dict = response.json()
        print(response_dict)
        
        spelling_error_count = response_dict['spellingErrorCount']

        if spelling_error_count == 0:
            return render_template("Spellcheck.html",fieldvalues=fieldvalues,spelling_error_count=spelling_error_count)
        else:
            elements = response_dict['elements']
            error_list = []
            for element in elements:
                error = element['errors'][0]
                word = error['word']
                position = error['position']
                suggestions = error['suggestions']
                error_list.append((word, position, suggestions))
        
        insert_sql = "INSERT INTO SPELLINGCHECKER VALUES (?,?,?,?)"
        stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(stmt, 1, word)
        ibm_db.bind_param(stmt, 2, spelling_error_count)
        ibm_db.bind_param(stmt, 3, position)
        ibm_db.bind_param(stmt, 4, suggestions)
        ibm_db.execute(stmt)
  
        return render_template("Spellcheck.html",response_dict=response_dict)
    else:
        return render_template("Spellcheck.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)
