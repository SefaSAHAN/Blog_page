from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

#User Register Form
class RegisterForm(Form):
    name=StringField("Name Surname",validators=[validators.length(min=4,max=25)])
    username=StringField("User Name",validators=[validators.length(min=5,max=25)])
    email=StringField("Email adress",validators=[validators.Email(message="Please write valid email adress")])
    password=PasswordField("Password:",validators=[
        validators.DataRequired(message="Please write a password"),
        validators.EqualTo(fieldname="confirm",message="Password does not match")
    ])
    confirm=PasswordField("Same Password")

class LoginForm(Form):
    username=StringField("Username")
    password=PasswordField("Password")

app=Flask(__name__)
app.secret_key="bp"  #this is for flash messages
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="bp"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

#user log in decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Please log in to see this page", "danger")
            return redirect(url_for("login"))
    return decorated_function

#register
@app.route("/register",methods=["GET", "POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password=sha256_crypt.encrypt(form.password.data)
        cursor=mysql.connection.cursor()
        query="INSERT into users(name,email,username,password) VALUES(%s,%s,%s,%s)" 
        cursor.execute(query,(name,email,username,password))
        mysql.connection.commit()
        cursor.close() 
        flash(f"{username} registered succesfully", "success")      
        return redirect(url_for('login'))
    else:
        return render_template("register.html",form=form)

#Log in
@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password=form.password.data
        cursor=mysql.connection.cursor()
        query=f"Select username,password from users where username='{username}' "
        result=cursor.execute(query)
        if result>0:
            data=cursor.fetchone()
            print(data)
            real_password=data["password"]
            if sha256_crypt.verify(password,real_password):
                flash(f"{username} login succesfully", "success") 
                session["logged_in"]=True     
                session["username"]=username     
                return redirect(url_for('index'))
            else:
                flash(f"Check your password please...", "danger")
                return redirect(url_for('login'))

        else:
            flash(f"Check username please. There is no such username...", "danger")
            return redirect(url_for('login'))

    return render_template("login.html",form=form)

#log out
@app.route("/logout")
def logout():
    session.clear()
    flash(f" log out succesfully", "success")
    return redirect(url_for('index'))

#control panel
@app.route("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    query=f"select * from articles where author='{session['username']}'" 
    result=cursor.execute(query)
    if result>0:
        articles=cursor.fetchall()
        cursor.close() 
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")
    

#add article
@app.route("/addarticle",methods=["GET","POST"])
@login_required
def addarticle():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.title.data
        content=form.content.data
        cursor=mysql.connection.cursor()
        query=f"INSERT into articles(title,author,content) VALUES('{title}','{session['username']}','{content}')" 
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close() 
        flash(f"Article created succesfully", "success")      
        return redirect(url_for('dashboard'))
    else:
        return render_template("addarticle.html",form=form)

#delete article
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    query=f"select * from articles where author='{session['username']}' and id={id}"
    result=cursor.execute(query)
    if result>0:
        query=f"delete from articles where id={id}"
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close() 
        return redirect(url_for("dashboard"))
    else:
        flash("There is no such article or you dont have authority to delete","danger")
        return redirect(url_for("index"))

#update article
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def update(id):
    if request.method=="GET":
        cursor=mysql.connection.cursor()
        query=f"select * from articles where author='{session['username']}' and id={id}"
        result=cursor.execute(query)
        if result>0:
            article=cursor.fetchone()
            form=ArticleForm()
            form.title.data=article["title"]
            form.content.data=article["content"]
            return render_template("update.html",form=form)
        else:
            flash("There is no such article or you dont have authority to edit","danger")
            return redirect(url_for("index"))
    else:
        #Post Request
        form=ArticleForm(request.form)
        new_title=form.title.data
        new_content=form.content.data
        query=f"update articles set title='{new_title}',content='{new_content}' where id={id}"
        cursor=mysql.connection.cursor()
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()
        flash("Article updated successfully","success")
        return redirect(url_for("dashboard")) 

    



#Articles Page
@app.route("/articles")
def articles():
    cursor=mysql.connection.cursor()
    query="select * from articles" 
    result=cursor.execute(query)
    if result>0:
        articles=cursor.fetchall()
        cursor.close() 
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")

#Article page
@app.route("/article/<string:id>")
def article(id):
    cursor=mysql.connection.cursor()
    query=f"select * from articles where id='{id}'"
    result=cursor.execute(query)
    if result>0:
        article=cursor.fetchone()
        cursor.close() 
        return render_template("article.html",article=article)
    else:    
        return render_template("article.html")
   

#article form
class ArticleForm(Form):
    title=StringField("Title",validators=[validators.length(min=5,max=100)])
    content=TextAreaField('Content ')


if __name__=="__main__": 
    app.run(debug=True) 
