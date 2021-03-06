from flask import Flask
from flask_mail import Mail, Message

app =Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'flasktester123@gmail.com'
app.config['MAIL_PASSWORD'] = '123flask'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
   msg = Message('Hello', sender = 'flasktester123@gmail.com', recipients = ['davecook@hotmail.co.uk'])
   msg.body = "Hello Flask message sent from Flask-Mail"
   mail.send(msg)
   return "Sent", app.config['MAIL_PORT']

if __name__ == '__main__':
   app.run(debug = True)
