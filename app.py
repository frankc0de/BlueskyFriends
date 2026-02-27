<<<<<<< HEAD
import os
#import atproto
from flask import Flask, session, \
                render_template, \
                abort, redirect, url_for, request, json , jsonify


from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, \
                               jwt_required , set_access_cookies, set_refresh_cookies, unset_jwt_cookies

from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')
app.config["JWT_SECRET_KEY"] = app.secret_key 
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(usuario):
    app.logger.debug('usuario')
    app.logger.debug(usuario)
    app.logger.debug('fin usuario')
    return usuario

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        username = request.form['username'] #request.json.get('username')
        password = request.form['password'] #request.json.get('password')
        app.logger.debug(f'hola con nombre de test {username}' )

        return 'eee'
    elif request.method == 'GET':
        token = request.cookies.get("access_token_cookie")
        if not token:
            resp = render_template('index.html')
            #unset_jwt_cookies(resp)    
            return resp
        else:
            resp = redirect('/home')
            return resp

        #ver si tenemos un token valido si lo tenemos y no a caducado pa lante si no a index borrando el token
        #return render_template('index.html')

@app.route('/hello/<name>')
@jwt_required()
def hello(name=None):
    app.logger.debug('hola con nombre de test')
    return render_template('index.html', person=name)

@app.route('/logout')
@jwt_required()
def logout():
    resp = redirect('/')
    unset_jwt_cookies(resp)
    return resp



@app.route('/home')
@jwt_required()
def home():
    kk = localStorage.getItem('token')
    return "dentro"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'] #request.json.get('username')
        password = request.form['password'] #request.json.get('password')
    
        # Input validation
        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400
    
        # Check if user already exists
        #if username in users:
        #    return jsonify({"msg": "User already exists"}), 400
    
        # Store user
        #users[username] = password
        #token = create_access_token(identity='{"username":"'+request.form['username']+'","password":'+request.form['password']+'}')
        #token = create_access_token(identity='{"username":"'+request.form['username']+'","password":'+request.form['password']+'}')
        access_token = create_access_token(identity=username, fresh=True)
        #refresh_token = create_refresh_token(identity=username)
        resp = redirect('/home')
        set_access_cookies(resp, access_token)
        #set_access_cookies(resp, refresh_token)
        return resp
    return '''
        <form method="post">
            <p><input type=text name=username value="frank000.bsky.social">
            <p><input type=password name=password value="wefiwuoifuwoifuwoifo">
            <p><input type=submit value=Login>
        </form>
    '''

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
=======
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
>>>>>>> 12145520cdc8db2ac62b794e87d4b77b0d2cbb0e
