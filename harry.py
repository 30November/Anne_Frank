from flask import Flask,render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key ="abc@123"

class Note(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    id = db.Column(db.Integer,default=0)
    title = db.Column(db.String(50),nullable=False)
    desp = db.Column(db.String(200),nullable=False)
    date = db.Column(db.Date,default=date.today())


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(50),nullable=False)


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
        return redirect('/') #very important ... confirm sub gets data added
    
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

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=="POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        db.session.add(User(username=user,password=pwd))
        db.session.commit()
        return redirect("/")
    
    return render_template("register.html")
    

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)