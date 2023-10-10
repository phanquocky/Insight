import json
from flask import Flask, render_template, request, flash, url_for, session, redirect, abort
from datetime import datetime, timedelta
from mongodb import *
from config import SECRECT_KEY
from Keypair.sign_verify import *
from forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRECT_KEY 
app.config['SESSION_COOKIE_SECURE'] = True

@app.before_request
def before_request():
  session.permanent = True
  app.permanent_session_lifetime = timedelta(minutes = 15) #Phiên làm việc sẽ tự động xóa sau 15p nếu không có thêm bất cứ request nào lên server.

@app.route('/')
def main():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    username = None
    if 'username' in session:
        username = session['username']
    return render_template("base.html", username = username)

@app.route("/search", methods=['GET', 'POST'])
def search():
    name = str(request.form.get('search'))
    username = None
    if 'username' in session:
        username = session['username']
    return render_template("search.html", 
                           users = query_users_by_name(name), 
                           request_name = name,
                           username = username)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if  'username' in session:
        return render_template("base.html", username = session['username'])

    if request.form.get('signup-submit'):
        form = SignupForm(request.form)
        if form.validate():
            new_user = User(username = form.username.data, password = form.password.data.encode('utf-8'))
            new_user.addToDB()
            flash('Signed up successfully.', category='success')
            return redirect(url_for('home'))
        return render_template('signup.html', form=form)
    
    elif request.form.get('login-submit'):
        form = LoginForm(request.form)
        if form.validate():
            session['username'] = form.username.data
            flash('Logged in successfully.', category='success')
            return redirect(url_for('home'))
        return render_template('signup.html', form=form, login = True)
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Xóa thông tin đăng nhập khỏi session để người dùng đăng xuất
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/contest', methods=['GET','POST'])
def contest():
    min_score = request.form.get('min_score')
    max_score = request.form.get('max_score')

    min_score = int(min_score) if min_score else 0
    max_score = int(max_score) if max_score else 100
    print(type (min_score), type (max_score))

    username = None
    if 'username' in session:
        username = session['username']
    return render_template('contest.html', 
                           users = query_users_by_score(min_score=min_score, max_score=max_score),
                           min_score = min_score,
                           max_score = max_score,
                           username = username)

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
        mentor = query_users_by_name(mentor_name, 1)
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
        
        username = None
        if 'username' in session:
            username = session['username']
        return render_template('challenge.html', 
                                mentor = mentor[0],
                                examiners = examiners,
                                username = username)

@app.route('/sign', methods=['GET','POST'])
def sign_route():
    username = None
    if 'username' in session:
        username = session['username']

    if request.method == 'POST':
        data = request.json
        try:
            message = data['message']   
            private_key_hex = data['private_key']
        except Exception as e:
            print(e)
            abort(400, "message, private_key are required!")

        try:
            print("private_key_hex: ", private_key_hex)
            private_key = hex_string_to_private_key(private_key_hex)
            print("private_key: ", private_key)
            signature, private_key = sign(hex_string_to_bytes(message), private_key)
            signature_hex = signature.hex()
            print("signature_hex: ", signature_hex)
            return json.dumps({'signature': signature_hex})
        except Exception as e:
            print(e)
            abort(400, "Invalid data")
    elif request.method == 'GET':
        message = request.args.get('message')
        if(message == None):
            message = ""
        return render_template('sign.html', message = message, username = username)

@app.route('/verify', methods=['GET','POST'])
def verify_route():
    username = None
    if 'username' in session:
        username = session['username']
    public_key = message = signature = None
    alert_message = ""

    if request.method == 'POST':
        data = request.json
        try:
            public_key = data['public_key']
            message = data['message']
            signature = data['signature']
        except Exception as e:
            print(e)
            abort(400, "pubblic_key, message, signature are required!")

        try:
            is_verified = None
            is_verified = verify(hex_string_to_bytes(message), hex_string_to_bytes(signature),  hex_string_to_public_key(public_key))
            return json.dumps({'is_verified': is_verified})        
        except Exception as e:
            print(e)
            abort(400, "Invalid data")
    
    elif request.method == 'GET':
        public_key = request.args.get('public_key')
        message = request.args.get('message')
        signature = request.args.get('signature')

        if(public_key == None or message == None or signature == None):
            return render_template('verify.html', username = username)
        else:
            public_key = str(public_key)
            message = str(message)
            signature = str(signature)
            print("public_key: ", public_key)
            print("message: ", message)
            print("signature: ", signature)
            try:
                is_verified = None
                is_verified = verify(hex_string_to_bytes(message), hex_string_to_bytes(signature),  hex_string_to_public_key(public_key))
                if(is_verified):
                    alert_message = "alert-success"
                else:
                    alert_message = "alert-danger"
                return render_template('verify.html', alert_message = alert_message, public_key = public_key, message = message, signature = signature, username = username)
            except Exception as e:
                print(e)
                alert_message = "alert-danger"
                return render_template('verify.html', public_key = public_key, message = message, signature = signature, alert_message = alert_message, username = username)


@app.route('/login')
def index():
    username = None
    if 'username' in session:
        username = session['username']
    return render_template('index.html', username = username)

@app.route('/get_metamask_address', methods=['POST'])
def get_metamask_address():
    metamask_address = request.form['metamaskAddress']
    print(metamask_address)
    
    # You can do something with the Metamask address here (e.g., authenticate the user)
    # You can send a response back to the client if needed
    return f"Metamask Address: {metamask_address}"

@app.route('/send', methods=['POST'])
def send_mail():
    data = request.form
    try:
        addr_from = data['addr_from']
        addr_to = data['addr_to']
        content = data['content']
        date_end = data['date_end']
    except Exception as e:
        print(e)
        abort(400, "addr_from, addr_to, content, date_end are required!")
    
    id = createMail(addr_from, addr_to, content, date_end)
    respone = query_mail_by_id(id)
    return respone

@app.route('/receive', methods=['GET'])
def receive_mail():
    receiver = request.args['addr_to']
    quantity = request.args['quantity']
    respone = query_mail_by_addrto(receiver, int(quantity))
    return respone

if __name__ == '__main__':
    app.run()
