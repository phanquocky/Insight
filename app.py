import json
from flask import Flask, render_template, request, flash, url_for, session, redirect, abort, jsonify, make_response
from datetime import datetime, timedelta
from mongodb_ver2 import *
from config import SECRECT_KEY
from Keypair.sign_verify import *
from Keypair.generation import *
from forms import *
from bson.json_util import dumps, loads
from api_link_create import *
from flask_cors import CORS
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRECT_KEY 
app.config['SESSION_COOKIE_SECURE'] = True

room_data_storage = {}

def generate_unique_identifier():
    return str(uuid.uuid4())
# Simulate a database or storage for large data

# Initialize CORS with your Flask app
cors = CORS(app, resources={r"/*": {"origins": "*"}})
@app.before_request
def before_request():
  session.permanent = True
  app.permanent_session_lifetime = timedelta(minutes = 30) #Phiên làm việc sẽ tự động xóa sau 30p nếu không có thêm bất cứ request nào lên server.


# Error Page 
@app.errorhandler(403)
def error_forbidden(e):
    static_url = app.static_url_path
    css_url = f"{static_url}/403.css"
    return render_template('403.html', css_url = css_url), 403

@app.errorhandler(404)
def page_not_found(e):
    static_url = app.static_url_path
    css_url = f"{static_url}/404.css"
    return render_template('404.html', css_url = css_url), 404


@app.route('/')
def main():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    username = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']
    return render_template("base.html", username = username, metamask_id = metamask_id)

@app.route('/mail', methods=['GET', 'POST'])
def mail():
    username = None
    if 'username' in session:
        username = session['username']
    return render_template("mail.html", username = username)

@app.route('/send-mail', methods=['GET', 'POST'])
def send_email():
    username = None
    if 'username' in session:
        username = session['username']
    if request.method == 'POST':
            From = query_users_by_username(username)
            To = request.form['To']
            subject = request.form['subject']
            message = request.form['message']
            expire_time = 3
            send_mail_to_user(From, To, subject, message, expire_time)
            return render_template("mail.html", username = username)
    
@app.route('/notification', methods=['GET', 'POST'])
def notify():
    username = None
    #NOTE!!!:
    #I have not yet tested with database, so if you wanna test with database,
    #remove the comments below and of course, comment my static mails[]

    #receiver = request.args.get('addr_to')
    #quantity = int(request.args.get('quantity'))
    #response = query_mail_by_addrto(receiver, quantity)
    #mails = json.loads(response)

    mails = [{
                "addr_from": "huongtran@gmail.com",
                "addr_to": "hieunt.wk@gmail.com",
                "content": "Good morning, my dear!",
                "date_send": "2023-10-10T10:30:00.000Z",
                "date_end": "2023-10-15",
                "is_read": False
            },
            {
                "addr_from": "thangngocdinh@gmail.com",
                "addr_to": "hieunt.wk@gmail.com",
                "content": "Hi, nice to meet you!",
                "date_send": "2023-10-11T11:45:00.000Z",
                "date_end": "2023-10-16",
                "is_read": True
            }]
    if 'username' in session:
        username = session['username']

    if username is not None:
        user = query_users_by_username(username)
        # print("user receive mail = ", user)
        mails = query_mail_by_addrto(user['public_key'], 10)
        mails = loads(mails)

    # print("mails = ", mails)
    return render_template('notification.html', mails=mails, username=username)

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

@app.route("/upload_file_render", methods=['GET'])
def render_room():
    return render_template('upload_file_render.html')

@app.route('/former/sign_up', methods = ['GET', 'POST'])
def former_sign_up():
    if  'username' in session:
        return redirect(url_for('home'))

    if request.form.get('signup-submit'):
        form = SignupForm(request.form)  
        if form.validate():
            new_user = User( username = form.username.data, 
                            metamask_id = form.metamask_id.data,
                            score = form.score.data,
                            former = True)
            print(new_user)
            new_user.addToDB()
            flash('Signed up successfully.', category='success')
        return render_template('former_sign_up.html', form=form, former = True)
    
    elif request.form.get('login-submit'):
        form = LoginForm(request.form)
        if form.validate():
            session['username'] = form.username.data
            session['metamask_id'] = form.metamask_id.data

            flash('Logged in successfully.', category='success')
            return redirect(url_for('home'))
        return render_template('former_sign_up.html', form=form, former = True)
    
    return render_template('former_sign_up.html', former = True)

@app.route('/sign_up', methods = ['GET', 'POST'])
def signup():
    if  'username' in session:
        return redirect(url_for('home'))
    
    username = request.args.get('username', default = None, type = str)
    score = request.args.get('score', default = None, type = int)

    if not username or username == None or username == "None":
        username = request.form.get("username", default = None, type = str)
        score = request.form.get("score", default = None, type = int)

    if request.form.get('signup-submit'):
        form = SignupForm(request.form)  
        if form.validate():
            new_user = User(username = form.username.data, 
                            metamask_id = form.metamask_id.data,
                            score = score)
            new_user.addToDB()
            flash('Signed up successfully.', category='success')
            return render_template('signup.html', username_login = username, score = score)
        return render_template('signup.html', form=form, username_signup = username, score = score)
    
    elif request.form.get('login-submit'):
        form = LoginForm(request.form)
        if form.validate():
            session['username'] = form.username.data
            session['metamask_id'] = form.metamask_id.data
            if score is not None:
                update_user_score(form.username.data, score)

            flash('Logged in successfully.', category='success')
            return redirect(url_for('home'))
        return render_template('signup.html', form=form, username_login = username, score = score)
    
    if query_user_by_username(username):
        return render_template('signup.html', username_login = username, score = score)
    else:
        return render_template('signup.html', username_signup = username, score = score)

@app.route('/generateKey', methods = ['POST'])
def generateKey():
    text = request.json
    private_key, public_key = generate_key_pair_from_user_pw(text['username'].encode('utf-8'), text['password'].encode('utf-8'))

    data = {
        'private_key': private_key,
        'public_key': public_key
    }

    return dumps(data)

@app.route('/logout')
def logout():
    # Xóa thông tin đăng nhập khỏi session để người dùng đăng xuất
    session.pop('username', None)
    session.pop('metamask_id', None)
    return redirect(url_for('home'))

@app.route('/contest', methods=['GET','POST'])
def contest():
    min_score = request.form.get('min_score')
    max_score = request.form.get('max_score')

    min_score = int(min_score) if min_score else 0
    max_score = int(max_score) if max_score else 100

    new_score = request.args.get('new_score')
    print(new_score)

    username = None
    user = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        user = query_user_by_username(username)
        metamask_id = session['metamask_id']

    mentors = query_users_by_score(min_score=min_score, max_score=max_score)
    return render_template('contest.html', 
                           mentors = mentors,
                           min_score = min_score,
                           max_score = max_score,
                           new_score = new_score,
                           username = username,
                           user = user,
                           user_json = dumps(user),
                           metamask_id = metamask_id)

@app.route('/challenge', methods=['POST'])
def challenge():
    if request.method == 'POST':
        data = request.json
        print("data = ", data)
        challenger_id = data['challenger_id']
        score = data['score']
        new_score = data['new_score']

        # print("challenger_id: ", challenger_id)
        challenger = find_users({"_id": ObjectId(challenger_id['$oid'])})[0]

        # Find 5 mentors
        mentors = find_examiner(score, new_score)
        if len(mentors) == 0:
            return jsonify({'status':'failed', 'message': 'No mentor found'})

        # Create room
        room = create_room_2(challenger, mentors, prev_score=score, want_score=new_score)

        return  jsonify({'status':'success', 'data': room})

@app.route('/challenge_request', methods=['GET'])
def challenge_request():
    username = None
    if 'username' in session:
        username = session['username']
        public_key = session['public_key']

    rooms = find_rooms({"mentor": public_key, "status": 0})
    if(len(rooms) > 0):
        for room in rooms:
            user = query_user_by_public_key(room['contestant'])
            room['contestant_info'] = user
            room['json'] = dumps(room)

    return render_template('challenge_request.html', username = username, 
                                                     rooms = rooms)

@app.route('/update_room_state', methods=['PATCH'])
def update_room_state():
    try:
        data = request.json
        room_id = data['room_id']
        state = data['state']
        update_room_status_by_id(room_id, state)
        return jsonify({'status': 200})
    except Exception as e:
        print(e)
        abort(400, "Invalid data")

@app.route('/sign', methods=['GET','POST'])
def sign_route():
    username = None
    metamask_id = None
    public_key = None
    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']
        public_key = session['public_key']

    if request.method == 'POST':
        data = request.json
        try:
            message = data['message']   
            private_key_hex = data['private_key']

            message = message.replace("0x", "")
            private_key_hex = private_key_hex.replace("0x", "")
        except Exception as e:
            print(e)
            abort(400, "message, private_key are required!")

        try:
            private_key = hex_string_to_private_key(private_key_hex)
            signature, private_key = sign(hex_string_to_bytes(message), private_key)
            signature_hex = signature.hex()
            signature_hex = "0x" + signature_hex
            return dumps({'signature': signature_hex})
        except Exception as e:
            print(e)
            abort(400, "Invalid data")
    elif request.method == 'GET':
        message = request.args.get('message')
        if(message == None):
            message = ""
        return render_template('sign.html', message = message, 
                                            username = username,
                                            metamask_id = metamask_id,
                                            public_key = public_key)

@app.route('/verify', methods=['GET','POST'])
def verify_route():
    username = None
    public_key = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        public_key = session['public_key']
        metamask_id = session['metamask_id']

    public_key = message = signature = None
    alert_message = ""

    if request.method == 'POST':
        data = request.json
        try:
            public_key = data['public_key'] 
            message = data['message']
            signature = data['signature']

            public_key = public_key.replace("0x", "")
            message = message.replace("0x", "")
            signature = signature.replace("0x", "")

            print("public_key: ", public_key)
            print("message: ", message)
            print("signature: ", signature)
        except Exception as e:
            print(e)
            abort(400, "public_key, message, signature are required!")

        try:
            is_verified = None
            is_verified = verify(hex_string_to_bytes(message), hex_string_to_bytes(signature),  hex_string_to_public_key(public_key))
            return dumps({'is_verified': is_verified})        
        except Exception as e:
            print(e)
            abort(400, "Invalid data")
    
    elif request.method == 'GET':
        public_key = request.args.get('public_key')
        message = request.args.get('message')
        signature = request.args.get('signature')

        print("public_key:", public_key)
        print("message:", message)
        print("signature:", signature)

        if(public_key == None or message == None or signature == None):
            return render_template('verify.html', username = username, metamask_id = metamask_id, public_key = public_key)
        else:
            public_key = str(public_key)
            message = str(message)
            signature = str(signature)

            public_key = public_key.replace("0x", "")
            message = message.replace("0x", "")
            signature = signature.replace("0x", "")

            print("public_key:", public_key, len(public_key))
            print("message:", message, len(message))
            print("signature:", signature, len(signature))
            try:
                is_verified = None
                is_verified = verify(hex_string_to_bytes(message), hex_string_to_bytes(signature),  hex_string_to_public_key(public_key))
                if(is_verified):
                    alert_message = "alert-success"
                else:
                    alert_message = "alert-danger"
                return render_template('verify.html', alert_message = alert_message, public_key = public_key, metamask_id = metamask_id, message = message, signature = signature, username = username)
            except Exception as e:
                print(e)
                alert_message = "alert-danger"
                return render_template('verify.html', public_key = public_key, message = message, signature = signature, alert_message = alert_message, username = username)

@app.route('/<username_search>',  methods=['GET', 'PATCH'])
def user_profile(username_search):
    username = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']

    if request.method == 'GET':
        user = query_user_by_username(username_search)
        print('<username_search>: user = ', user)
        if user == None:
            return jsonify({"error": "Error: Invalid username"}), 404

        CertificateRoom = query_certificate_2_by_username(username_search)
        certificates = None
        if CertificateRoom:
            certificates = CertificateRoom['certificates']

        return render_template("user_profile.html", user = user, 
                                                    certificates = certificates,
                                                    username = username, 
                                                    metamask_id = metamask_id)
    else:
        data = request.json
        user = query_user_by_username(username)
        print("user = ", user)
        if user == None:
            abort(404, "Invalid username")
        
        if 'judge_state' in data:
            if('judge_state' not in user or user['judge_state'] != data['judge_state']):
                user['judge_state'] = data['judge_state']
                update_user_judge_state(username, data['judge_state'])

        return dumps({'message': 'success', 'user': user})

@app.route('/send', methods=['POST'])
def send_mail():
    data = request.form
    try:
        addr_from = data['addr_from']
        addr_to = data['addr_to']
        subject = data['subject']
        content = data['content']
        date_end = '10'
        if('date_end' in data):
            date_end = data['date_end']
    except Exception as e:
        print(e)
        abort(400, "addr_from, addr_to, content are required!")
    
    id = createMail(addr_from, addr_to, subject, content, int(date_end))
    response = query_mail_by_id(id)
    return response

@app.route('/receive', methods=['GET'])
def receive_mail():
    receiver = request.args['addr_to']
    quantity = request.args['quantity']
    response = query_mail_by_addrto(receiver, int(quantity))
    return response

# example: http://127.0.0.1:5000/mentor_confirm?mentor=1432&contestant=123
@app.route('/mentor_confirm', methods=['GET'])
def mentor_confirm():
    if request.method == 'GET':
        mentor_public_key = request.args.get('mentor')
        contestant = request.args.get('contestant')

        if mentor_public_key is None or contestant is None:
            return jsonify({"error": "Error: Both Mentor Public Key and Contestant are required."}), 400

        # Call the update_mentor function with mentor_public_key and contestant as arguments
        confirmation_result = update_mentor(mentor_public_key, contestant)

        if confirmation_result:
            success_message = f"Successfully confirmed mentor with Public Key '{mentor_public_key}' for contestant '{contestant}'."
            return jsonify({"message": success_message}), 200
        else:
            error_message = f"Error: Unable to confirm mentor with Public Key '{mentor_public_key}' for contestant '{contestant}'."
            return jsonify({"error": error_message}), 400

@app.route('/mentor', methods=['POST', 'GET'])
def mentor():
    # Lấy dữ liệu từ MongoDB
    username = None
    # public_key = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        # public_key = session['public_key']
        metamask_id = session['metamask_id']

    # if request.method == 'POST':
    #     room_id = request.form['room_id']
    #     print("room_id: ", room_id)
    #     uploaded_file = request.files['file']
    #     save_test_to_db(room_id, uploaded_file)
    #     return redirect('/mentor')

    mentor_rooms = query_mentor_rooms2(username)
    # mentor_rooms = query_mentor_rooms(public_key)

    if request.method == 'POST':
        room_id = request.form['room_id']
        uploaded_file = request.files['file']
        mentor_id = request.form['mentor_id']
        upload_test_to_db(room_id, uploaded_file, mentor_id)
        return redirect('/mentor')

    # for room in mentor_rooms:
    #     contestant_user = query_user_by_public_key(room['contestant'])
    #     # print("contestant_user: ", contestant_user)
    #     room['contestant'] = contestant_user['name'] if contestant_user['name'] else contestant_user['username']
    #     if(room['status'] == 0):
    #         room['status'] = "waiting..."
    #     else:
    #         room['status'] = "accepted"
    # print(mentor_rooms)

    return render_template('mentor.html', mentor_rooms=mentor_rooms, 
                                            username=username,
                                            metamask_id=metamask_id)

@app.route('/former/view', methods=['GET'])
def former_view():
    username = None
    if 'username' in session:
        username = session['username']
    if not username:
        abort(403)
    if query_user_by_username(username)['former'] == False:
        abort(403)

    rooms = find_room_is_finished()
    print(rooms)
    return render_template('former_view.html', 
                           rooms = rooms,
                           username = session['username'], 
                           metamask_id = session['metamask_id'])


@app.route('/public/room/<room_id>', methods=['GET'])
def view_public_room(room_id):
    username = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']

    room = find_room_2_by_id(room_id)
    if(room is None):
        abort(404, "Invalid room id")

    for test in room['tests']:
        for mentor in room['mentors']:
            if(mentor['id'] == test['mentor_id']):
                test['mentor_name'] = mentor['username']
                break

    return render_template('render_room.html', room=room, 
                                                username=username,
                                                metamask_id=metamask_id)

# Description:
# Get:
    # Hiện giao diện bình thường thôi. Có 1 chỗ để người dùng up load file .bin (file binary)
    # Sau khi người dùng upload file và nhấn vào button <render room>, 
    # Thì thực hiện Post vào đường link này với content là nội dung của file ở dạng mảng byte
@app.route('/public/room', methods=['GET', 'POST'])
def view_room():
    username = None
    metamask_id = None
    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']

    room = None
    if request.method == 'GET':
        identifier = request.args.get('identifier')
        if identifier in room_data_storage:
            room = loads(room_data_storage[identifier])
        else:
            abort(404, "Invalid identifier")
        
        if not isinstance(room, Room2):
            jsonify({"error": "Error: Invalid room data"}), 400
        
        for test in room['tests']:
            for mentor in room['mentors']:
                if(mentor['id'] == test['mentor_id']):
                    test['mentor_name'] = mentor['username']
                    break
        
        return render_template('render_room.html', room=room,
                                                    username=username,
                                                    metamask_id=metamask_id)    

    if request.method == 'POST':
        #Get the file
        uploaded_file = request.files['file']

        room_bytes = uploaded_file.read()
     
        identifier = generate_unique_identifier()
        room_data_storage[identifier] = room_bytes
        return redirect(url_for('view_room', identifier=identifier))

@app.route('/room/mentor/sign', methods=['POST'])
def update_mentor_sign():
    try:
        data = request.json
        room_id = data['room_id']
        mentor_id = data['mentor_id']
        signature = data['signature']

        update_room_2_mentor_sign(room_id, mentor_id, signature)
        print("update_mentor_sign: successfully")
        return jsonify({'status': 200})
    except Exception as e:
        print(e)
        return jsonify({'status': 400, "message": "Invalid data"})

@app.route('/room/mentor/test_signature', methods=['GET'])
def view_signature():
    room_id = request.args.get('room_id')
    mentor_id = request.args.get('mentor_id')
    room = find_room_2_by_id(room_id)
    if(room is None):
        return jsonify({'status': 404, 'message': 'Invalid room id'})
    
    tests = room['tests']
    for test in tests:
        if(test['mentor_id'] == ObjectId(mentor_id)):
            if('test_sign' not in test ) or (test['test_sign'] is None):
                return jsonify({'status': 404, 'message': 'Have not signed yet'})
            else :
                return jsonify({'status': 200, 'signature': test['test_sign']})
    return jsonify({'status': 404, 'message': 'Invalid mentor id'})

@app.route('/room/mentor/score_signature', methods=['GET', 'POST'])
def view_score_signature():
    if request.method == 'GET':
        room_id = request.args.get('room_id')
        mentor_id = request.args.get('mentor_id')
        room = find_room_2_by_id(room_id)
        if(room is None):
            return jsonify({'status': 404, 'message': 'Invalid room id'})
        
        tests = room['tests']
        for test in tests:
            if(test['mentor_id'] == ObjectId(mentor_id)):
                if('score_sign' not in test ) or (test['score_sign'] is None):
                    return jsonify({'status': 404, 'message': 'Have not signed yet'})
                else :
                    return jsonify({'status': 200, 'signature': test['score_sign']})
        return jsonify({'status': 404, 'message': 'Invalid mentor id'})
    
    elif request.method == 'POST':
        data = request.json
        print("room/mentor/score_signature: data = ", data)
        room_id = data['room_id']
        mentor_id = data['mentor_id']
        signature = data['signature']


        update_room_2_score_sign(room_id, mentor_id, signature)
        print("update_mentor_sign: successfully")
        return jsonify({'status': 200})        

@app.route('/room/contestant/sign', methods=['POST'])
def update_contestant_sign():
    try:
        data = request.json
        room_id = data['room_id']
        mentor_id = data['mentor_id']
        signature = data['signature']

        update_room_2_contestant_sign(room_id, mentor_id, signature)
        print("update_mentor_sign: successfully")
        return jsonify({'status': 200})
    except Exception as e:
        print(e)
        return jsonify({'status': 400, "message": "Invalid data"})

@app.route('/room/contestant/submission_signature', methods=['GET'])
def view_submission_signature():
    room_id = request.args.get('room_id')
    mentor_id = request.args.get('mentor_id')

    room = find_room_2_by_id(room_id) 

    if(room is None):
        return jsonify({'status': 404, 'message': 'Invalid room id'})

    tests = room['tests']
    for test in tests:
        if(test['mentor_id'] == ObjectId(mentor_id)):
            if('submission_sign' not in test ) or (test['submission_sign'] is None):
                return jsonify({'status': 404, 'message': 'Have not signed yet'})
            else :
                return jsonify({'status': 200, 'signature': test['test_sign']})
    return jsonify({'status': 404, 'message': 'Invalid mentor id'})

@app.route('/view_test/<room_id>', methods=['GET'])
def view_test(room_id):
    mentor_id = request.args.get('mentor_id')
    # Truy vấn cơ sở dữ liệu để lấy nội dung của file Test dựa trên room_id
    room_content = get_test_from_room_2(room_id, mentor_id)

    # Kiểm tra xem room_content có tồn tại không
    if room_content is None:
        return "Test not found", 404

    # Trả về nội dung của file Test dưới dạng response PDF
    response = make_response(room_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=test_{room_id}_{mentor_id}.pdf'
    return response

@app.route('/contestant')
def contestant_room():
    username = None
    metamask_id = None

    if 'username' in session:
        username = session['username']
        # public_key = session['public_key']
        metamask_id = session['metamask_id']

    # if request.method == 'POST':
    #     room_id = request.form['room_id']
    #     uploaded_file = request.files['file']
    #     save_submit_to_db(room_id, uploaded_file)
    #     return redirect('/contestant')  # Chuyển hướng người dùng sau khi tải lên thành công

    # contestant_rooms = query_contestant_rooms(public_key)
    # for room in contestant_rooms:
    #     room['mentor'] = query_user_by_public_key(room['mentor'])['username']
    # return render_template('contestant.html', contestant_rooms=contestant_rooms,
    #                                             username=username,
    #                                             metamask_id=metamask_id)

    contestant_rooms = query_contestant_room2(username)

    count = [0] * len(contestant_rooms)
    i = 0
    # print(len(contestant_rooms))
    for room in contestant_rooms:
        for tests in room['tests']:
            if tests['submission'] is not None:
                count[i] += 1
        i += 1
    # print(count)

    return render_template('contestant_ver2.html', contestant_rooms=contestant_rooms,
                           username=username,
                           metamask_id=metamask_id, count_test_complete=count)

@app.route('/contestant/<room_id>', methods = ['GET','POST'])
def contestant_a_room_detail(room_id):
    username = None
    metamask_id = None

    if 'username' in session:
        username = session['username']
        metamask_id = session['metamask_id']

    if request.method == 'POST':
        # print('Hi ae')
        room_id = request.form['room_id']
        mentor_id = request.form['mentor_id']
        uploaded_file = request.files['file']
        save_submit_to_db(room_id, uploaded_file, mentor_id)
        return jsonify({'Status': 200}), 200

    room_detail = query_contestant_room_by_roomid(room_id)
    return render_template('contestant_room_detail.html', room_detail=room_detail,
                           username=username, metamask_id=metamask_id)

@app.route('/view_submit/<room_id>', methods=['GET'])
def view_submit(room_id):
    mentor_id = request.args.get('mentor_id')

    # Truy vấn cơ sở dữ liệu để lấy nội dung của file Test dựa trên room_id
    room_content = get_submit_from_room_2(room_id, mentor_id)

    # Kiểm tra xem room_content có tồn tại không
    if room_content is None:
        return "Test not found", 404

    # Trả về nội dung của file Test dưới dạng response PDF
    response = make_response(room_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=test_{room_id}.pdf'
    return response

@app.route('/former/get_byte/<room_id>', methods=['POST'])
def former_sign(room_id):
    data = request.json
    username = data['username']
    if username == None:
        return jsonify({'status': 400, 'message': 'username is required to validate you are former!'})

    user = query_user_by_username(username)
    if user == None:
        return jsonify({'status': 400, 'message': 'Invalid username!'})
    
    if user['former'] == False:
        jsonify({'status': 400, 'message': 'You are not a former!'})

    if request.method == 'POST':
        room_byte = encode_to_byte_room_2(room_id)
        return jsonify({'status': 200, 'room_byte': room_byte})

@app.route('/former/send_certificate', methods=['POST'])
def former_send_certificate():
    data = request.json
    print("/former/send_ceritificate: data = ", data)
    username = data['username']
    if username == None:
        return jsonify({'status': 400, 'message': 'username is required to validate you are former!'})
    
    user = query_user_by_username(username)
    if user['former'] == False:
        jsonify({'status': 400, 'message': 'You are not a former!'})

    if request.method == 'POST':
        room_id   = data['room_id']
        signature = data['signature']
        room_hash = data['room_hash']
        room_byte = encode_to_byte_room_2(room_id)

        room = find_room_2_by_id(room_id)
        if room is None:
            return jsonify({'status': 404, 'message': 'Invalid room id!'})

        certificate = create_certificate(room['prev_score'], room['updated_score'], room_byte, room_hash, signature)
        if certificate is None:
            return jsonify({'status': 400, 'message': 'Failed to create certificate!'})
        print("certificate: ", certificate.__dict__)
        add_certificate_2_by_userid(room['contestant']['id'], certificate)
        print("add_certificate: successfully")

        contestant_username = room['contestant']['username']
        update_score = str(room['updated_score'])
        update_user_score(contestant_username, update_score)
        print("update_user_score: successfully")
        apiLink = 'http://127.0.0.1:8000/done_exam?username='+contestant_username+'&score='+update_score+'&community=1'
        return redirect(apiLink)

@app.route('/save_grade/<room_id>', methods=['GET', 'POST'])
def save_grade(room_id):
    # Nhận dữ liệu từ yêu cầu POST
    data = request.json
    print(data)
    # Lấy thông tin từ dữ liệu nhận được
    mentor_id = data.get('mentorID')
    score = data.get('score')

    response = update_score_by_room_id_and_mentor_id(room_id ,mentor_id,score)

    return jsonify(response)

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = query_all_users()
    return jsonify(users)

if __name__ == '__main__':
    app.run()
