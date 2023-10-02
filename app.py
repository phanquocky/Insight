from flask import Flask, render_template, request
from mongodb import createUser
from datetime import datetime
from mongodb import query_users_by_name

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

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

if __name__ == '__main__':
    app.run()
