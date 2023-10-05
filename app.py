import json
from flask import Flask, render_template, request
from mongodb import createUser
from datetime import datetime
from mongodb import query_users_by_name
from mongodb import query_users_by_score


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("base.html")

@app.route("/search", methods=['GET', 'POST'])
def search():
    name = str(request.form.get('search'))
    print(name)
    return render_template("search.html", 
                           users = query_users_by_name(name), 
                           request_name = name)

@app.route('/signUp')
def signUp():
    return render_template('signup.html')

@app.route('/contest', methods=['GET','POST'])
def contest():
    min_score = request.form.get('min_score')
    max_score = request.form.get('max_score')

    min_score = int(min_score) if min_score else 0
    max_score = int(max_score) if max_score else 100
    print(type (min_score), type (max_score))
    return render_template('contest.html', 
                           users = query_users_by_score(min_score=min_score, max_score=max_score),
                           min_score = min_score,
                           max_score = max_score)

@app.route('/challenge', methods=['GET','POST'])
def challenge():
    if request.method == 'POST':
        user = request.json
        print(user)
        return "OK"
    elif request.method == 'GET':
        return render_template('challenge.html')


if __name__ == '__main__':
    app.run()
