import json
from flask import Flask, render_template, request
from mongodb import createUser
from datetime import datetime
from mongodb import query_users_by_name
from mongodb import query_users_by_score
from mongodb import find_examiner_above
from mongodb import find_room_with_mentor_and_challenger
from mongodb import createRoom
from mongodb import update_room_with_examiners


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
        # update to mongodb
        return "OK"
    elif request.method == 'GET':
        challenger_name = request.args.get('challenger')
        mentor_name = request.args.get('mentor')
        mentor = query_users_by_name(mentor_name)
        score = mentor[0]['score']

        # room = find_room_with_mentor_and_challenger(mentor_name, challenger_name)
        
        # if(room == None):
        #     createRoom(mentor_publickey, challenger_publickey)

        # examiners = room['examiners']
        # if examiners.is_empty():
        #     find_examiner_above(int(score) if score else 0)

        # # Update examiners to mongodb
        # update_room_with_examiners(room['id'], examiners)

        examiners = find_examiner_above(int(score) if score else 0)
        if not examiners:
            examiners.append(mentor[0])
        
        return render_template('challenge.html', 
                                mentor = mentor[0],
                                examiners = examiners)

if __name__ == '__main__':
    app.run()
