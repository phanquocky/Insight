import json
from flask import Flask, render_template, request, flash, url_for, session, redirect, abort, jsonify, make_response
from datetime import datetime, timedelta
from mongodb import *
from config import SECRECT_KEY
from Keypair.sign_verify import *
from Keypair.generation import *
from forms import *
from bson.json_util import dumps, loads
from api_link_create import *

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
    public_key = None
    if 'username' in session:
        username = session['username']
        public_key = session['public_key']
        metamask_id = session['metamask_id']
    return render_template("base.html", username = username, public_key = public_key, metamask_id = metamask_id)

@app.route('/mail', methods=['GET', 'POST'])
def mail():
    username = None
    if 'username' in session:
        username = session['username']
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
        print("user receive mail = ", user)
        mails = query_mail_by_addrto(user['public_key'], 10)
        mails = loads(mails)

    print("mails = ", mails)
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

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if  'username' in session:
        return render_template("base.html", username = session['username'])

    if request.form.get('signup-submit'):
        form = SignupForm(request.form)  
        if form.validate():
            new_user = User(name = form.username.data, username = form.username.data, password = form.password.data.encode('utf-8'), public_key = form.public_key.data)
            new_user.addToDB()
            flash('Signed up successfully.', category='success')
        return render_template('signup.html', form=form)
    
    elif request.form.get('login-submit'):
        form = LoginForm(request.form)
        if form.validate():
            session['username'] = form.username.data
            session['metamask_id'] = form.metamask_id.data
            session['public_key'] = query_users_by_username(session['username'])['public_key']
            update_user_metamask(session['username'], form.metamask_id.data)

            flash('Logged in successfully.', category='success')
            return redirect(url_for('home'))
        return render_template('signup.html', form=form, login = True)
    
    return render_template('signup.html')

@app.route('/generateKey', methods = ['POST'])
def generateKey():
    text = request.json
    private_key, public_key = generate_key_pair_from_user_pw(text['username'].encode('utf-8'), text['password'].encode('utf-8'))

    while query_user_by_public_key(public_key) is not None:
        private_key, public_key = generate_key_pair_from_user_pw(text['username'].encode('utf-8'), text['password'].encode('utf-8'))

    data = {
        'private_key': private_key,
        'public_key': public_key
    }

    return json.dumps(data)

@app.route('/logout')
def logout():
    # Xóa thông tin đăng nhập khỏi session để người dùng đăng xuất
    session.pop('username', None)
    session.pop('public_key', None)
    session.pop('metamask_id', None)
    return redirect(url_for('home'))

@app.route('/contest', methods=['GET','POST'])
def contest():
    min_score = request.form.get('min_score')
    max_score = request.form.get('max_score')

    min_score = int(min_score) if min_score else 0
    max_score = int(max_score) if max_score else 100

    username = None
    user = None
    if 'username' in session:
        username = session['username']
        user = query_users_by_username(username)
        print("user join contest", user)

    mentors = query_users_by_score(min_score=min_score, max_score=max_score)
    # print("mentors in contest: ", mentors)
    return render_template('contest.html', 
                           mentors = mentors,
                           min_score = min_score,
                           max_score = max_score,
                           username = username,
                           data = json.dumps(mentors),
                           user = json.dumps(user))

@app.route('/challenge', methods=['GET','POST'])
def challenge():
    if request.method == 'POST':
        data = request.json
        challenger = data['challenger']
        mentor = data['mentor']

        print("challenger: ", challenger)
        print("mentor: ", mentor)

        find_room_condition = {
            "contestant": challenger['public_key'],
            "status": {'$gte': 1}
        }

        # Check if challenger is in another room (Join another contest)
        if(len(find_rooms(find_room_condition)) > 0):
            return jsonify({'result':'failed', 'message': 'Challenger is in another room'})

        # Gui request ve mentor nhieu lan
        if(len(find_rooms({
            "mentor": mentor['public_key'],
            "contestant": challenger['public_key']
        })) > 0):
            return jsonify({'result':'success', 'message': 'Request is already', 
                            'challenger': challenger['public_key'],
                            'mentor': mentor['public_key']})

        examiners = find_examiner_above(mentor['score'] if 'score' in mentor else 0)
        if not examiners:
            examiners.append(mentor['public_key'])

        examiners_public_key = [examiner['public_key'] for examiner in examiners]      
        print("create room: ", mentor['public_key'], challenger['public_key'])
        room = create_room(mentor = mentor['public_key'], challenger = challenger['public_key'],examiners = examiners_public_key)
        
        time_expire = 3 
        api_link = mentor_confirm_link(mentor['public_key'], challenger['public_key'])
        print("api_link: ", api_link)
        send_mail_to_user(challenger['public_key'], 
                         mentor['public_key'], 
                          "You have a new challenge", 
                          "You have a new challenge from " + challenger['public_key'] + ". Click this link to accept it or it will be expired after {} days. ({})".format(time_expire, api_link), 
                          time_expire)

        return  jsonify({'result':'success', 
                         'message': 'Room is create',
                         'challenger': challenger['public_key'],
                         'mentor': mentor['public_key']})
    
    elif request.method == 'GET':
        challenger_pubkey = request.args.get('challenger')
        mentor_pubkey = request.args.get('mentor')

        rooms = find_rooms({"mentor": mentor_pubkey, "contestant": challenger_pubkey})
        if(rooms == None or len(rooms) == 0):
            abort(404, {"message": "Room not found"})
        
        examiners_public_key = rooms[0]['judges']
        examiners = [find_users({"public_key": examiner})[0] for examiner in examiners_public_key]
    
        username = None
        if 'username' in session:
            username = session['username']
        return render_template('challenge.html', 
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
            abort(400, "public_key, message, signature are required!")

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

@app.route('/<username>',  methods=['GET', 'PATCH'])
def user_profile(username):
    if request.method == 'GET':
        user = query_users_by_username(username)
        if user == None:
            abort(404)

        return render_template("user_profile.html", user = user, 
                                                    username = username, 
                                                    data=json.dumps(user))
    else:
        data = request.json
        user = query_users_by_username(username)
        print("user = ", user)
        if user == None:
            abort(404, "Invalid username")
        
        if 'judge_state' in data:
            if('judge_state' not in user or user['judge_state'] != data['judge_state']):
                user['judge_state'] = data['judge_state']
                update_user_judge_state(username, data['judge_state'])

        return json.dumps({'message': 'success', 'user': user})

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
    public_key = None
    if 'username' in session:
        username = session['username']
        public_key = session['public_key']

    if request.method == 'POST':
        room_id = request.form['room_id']
        uploaded_file = request.files['file']
        save_test_to_db(room_id, uploaded_file)
        return redirect('/mentor')  # Chuyển hướng người dùng sau khi tải lên thành công

    mentor_rooms = query_mentor_rooms(public_key)
    return render_template('mentor.html', mentor_rooms=mentor_rooms, username=username)

# Đoạn này làm để trả tải về máy
# @app.route('/view_test/<room_id>', methods=['GET'])
# def view_test(room_id):
#     # Truy vấn cơ sở dữ liệu để lấy nội dung của file Test dựa trên room_id
#     room_content = get_test_from_db(room_id)
#
#     # Kiểm tra xem room_content có tồn tại không
#     if room_content is None:
#         return "Test not found", 404
#
#     # Tạo tạm thời một file PDF từ dãy binary
#     temp_pdf_path = f'test_{room_id}.pdf'
#     with open(temp_pdf_path, 'wb') as temp_pdf:
#         temp_pdf.write(room_content)
#
#     # Trả về file PDF dưới dạng response
#     return send_file(temp_pdf_path, as_attachment=True, download_name=f'test_{room_id}.pdf')

@app.route('/view_test/<room_id>', methods=['GET'])
def view_test(room_id):
    # Truy vấn cơ sở dữ liệu để lấy nội dung của file Test dựa trên room_id
    room_content = get_test_from_db(room_id)

    # Kiểm tra xem room_content có tồn tại không
    if room_content is None:
        return "Test not found", 404

    # Trả về nội dung của file Test dưới dạng response PDF
    response = make_response(room_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=test_{room_id}.pdf'
    return response


if __name__ == '__main__':
    app.run()
