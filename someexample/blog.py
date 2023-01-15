from flask import Flask,render_template

app=Flask(__name__)

@app.route("/")
def index():
    #to send variable to the html page
    # number=10
    # article={}
    # article["title"]="sport"
    # article["body"]="Football"
    # return render_template("index.html",number=number,article=article)
    # <p>{{number}}</p>
    # <p>{{article}}</p>
    # <p>{{article.body}}</p>
    # <p>{{article["body"]}}</p>
    return render_template("index.html")

@app.route("/about")
def about():
    return"About"

if __name__=="__main__": #If it try to to run in this page if cond true if you call as a module False
    app.run(debug=True) # to see mistakes