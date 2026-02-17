from flask import Flask
from flask import render_template

app = Flask(__name__)

#@app.route('/')
#def hello_world():
#    return 'Hello, World!'

posts = ['aaaaa','bbbbb','cccccc']

@app.route("/")
def index():
    return render_template("index.html", num_posts=len(posts), posts=posts)