from flask import Flask
from flask import render_template

app = Flask(__name__)

#@app.route('/')
#def hello_world():
#    return 'Hello, World!'


# seguir tambien
# seguir
# sois amigos
posts = [
    {'nick':'@frank000.bsky.social','estado':'No te sigue'},
    {'nick':'@frank000.bsky.social','estado':'Te sigue'},
    {'nick':'@frank000.bsky.social','estado':'No te sigue'},
         ]

@app.route("/")
def index():
    return render_template("index.html", num_posts=len(posts), posts=posts)
