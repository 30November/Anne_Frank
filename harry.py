from flask import Flask,render_template,request,redirect,session,url_for, flash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import date
import smtplib

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key ="abcxyz@123890"
serializer = URLSafeTimedSerializer(app.secret_key)

class Note(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    id = db.Column(db.Integer,default=0)
    title = db.Column(db.String(50),nullable=False)
    desp = db.Column(db.String(200),nullable=False)
    date = db.Column(db.Date,default=date.today())


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True)
    mail = db.Column(db.String(50))
    password = db.Column(db.String(50))


#mail
def send_email(to_email, subject, body):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("backenddeveloperformyprojectus@gmail.com","jvim gusx hbsy jszz")  # Use secure storage!
    message = f"Subject: {subject}\n\n{body}"
    server.sendmail("backenddeveloperformyprojectus@gmail.com", to_email, message)
    server.quit()


@app.route("/",methods=["POST","GET"])
def main():
    if request.method=="POST":
        title = request.form["title"]
        desp = request.form["desp"]
        todo = Note(title=title, desp=desp)
        if session:
            todo.id = session["id"]
        db.session.add(todo)
        db.session.commit()
        return redirect('/') 
    
    id = session.get("id",0)
    return render_template("harry.html",MyTodo=Note.query.filter_by(id=id).all(),user = User.query.get(id))

@app.route("/delete/<int:sno>")
def delete(sno):
    fetch = Note.query.filter_by(sno=sno).first()
    db.session.delete(fetch)
    db.session.commit()
    return redirect("/")

@app.route("/update/<int:sno>",methods=["POST","GET"])
def update(sno):
    if request.method=="POST": #when button hit
        todo = Note.query.filter_by(sno=sno).first()
        todo.title = request.form["title"]
        todo.desp = request.form["desp"]
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    
    todo = Note.query.filter_by(sno=sno).first()
    return render_template("update.html",todo=todo)

@app.route("/login",methods=["POST","GET"])
def login():
    error = None
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        info = User.query.filter_by(username=user).first()
        if info:
            if info.password == pwd:
                session["id"] = info.id
                return redirect('/')
            else:
                error = "Wrong password"
        else:
            error = "No user Found!"

    return render_template("login.html",error=error)

@app.route("/logout")
def logout():
    session.pop("id",None)
    return redirect("/")

@app.route('/fp', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.filter_by(username=user_id).first()
        if user:
            email = user.mail
            token = serializer.dumps(user_id, salt='fp')
            reset_link = url_for('reset_password', token=token, _external=True)
            body = f"Click the link to reset your password (valid for 5 mins): {reset_link}"
            send_email(email, "Password Reset", body)
            return "Reset link sent to your email."
        else:
            flash("User ID not found.")
    return '''
        <form method="post">
            User ID: <input name="user_id">
            <input type="submit">
        </form>
    '''

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        user_id = serializer.loads(token, salt='fp', max_age=300) # 5 minutes
    except SignatureExpired:
        return "The password reset link has expired."
    except BadSignature:
        return "Invalid token!"
    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(username=user_id).first()
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return "Password updated successfully!"
    
    return '''
        <form method="post">
            New Password: <input name="password" type="password">
            <input type="submit">
        </form>
    '''

    

@app.route("/register",methods=["POST","GET"])
def register():
    error = ""
    if request.method=="POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        mail = request.form["mail"]
        db.session.add(User(username=user,password=pwd,mail=mail))
        try:
            db.session.commit()
            session["id"] = User.query.filter_by(username=user).first().id
            return redirect("/")
        except:
            error = "User already exist"
            
    return render_template("register.html",error=error)
    

if __name__=="__main__":
    app.run(debug=True)