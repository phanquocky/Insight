import smtplib
from config import PASSWORD_GMAIL

#password là pass app sau khi bật xác thực 2 lớp
password = PASSWORD_GMAIL

#thêm mail người gửi và nhận
sender   = ''
receiver = ''

def send_invitaion(sender, receiver):
    msg = ("From: %s\r\nTo: %s\r\nsubject: test\n\r\nTest" % (sender, receiver))
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(sender, password)
    smtpObj.sendmail(sender, receiver, msg) 
    print("successfull") 

# send_invitaion(sender, receiver)