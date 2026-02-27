import os
import time
import datetime
from atproto import AtUri, Client, models, IdResolver
from flask import Flask, session, \
                render_template, \
                abort, redirect, url_for, request, json , jsonify


from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, \
                               jwt_required , set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt

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




def GetFollowers(handle, client, limit):
        lista = []
        Cursor = None
        Salir = False
        while not Salir:
            followers:models.AppBskyGraphGetFollowers.Response = client.get_followers(actor=handle,
                                                cursor=Cursor,
                                                limit=limit)
            
            for follower in followers.followers:
                lista.append(follower)
            
            Cursor = followers.cursor
            if Cursor is None:
                Salir = True
        return lista

def GetFollows(handle, client, limit):
        Cursor = None
        Salir = False
        lista = []
        while not Salir:

            error = True
            while error is True:
                reintentos = 0
                try:
                    follows = client.get_follows(actor=handle,
                                                    cursor=Cursor,
                                                    limit=limit)
                    error = False
                except:
                    error = True
                    time.sleep(5)
                    reintentos += 1

            for follow in follows.follows:
                lista.append(follow)

            Cursor = follows.cursor
            if Cursor is None:
                Salir = True
        return lista

# crea el token con los datos del usuario logado en bluesky
def autenticacionBlueSky(username, password):
    client = Client()
    client.login(username, password)
    session_string = client.export_session_string()
    did = client.me.did
    access_token = create_access_token(identity=did,
                                        additional_claims={
                                            "session_string": session_string
                                            }, fresh=True)


    return access_token


def ListadoCuentas():
    retorno = []
    retornoseguidores = []
    
    app.logger.debug('saca el usuario del token')
    claims = get_jwt()
    session_string = claims["session_string"]      # identity
      
    client = Client()
    client.login(session_string=session_string)
    limit = 100
    for cuenta in GetFollowers(handle=client.me.handle, client=client, limit=limit):
        did = cuenta['did']
        handle = cuenta['handle']
        avatar = cuenta['avatar']
        display_name = cuenta['display_name']
        if display_name is None:
            display_name = handle 
        following = False
        profile_url = f'https://bsky.app/profile/' + handle.replace('@','')
        retornoseguidores.append({'did':did,'display_name':display_name,'handle':handle,'avatar':avatar,'following':following,'profile_url':profile_url,})
    
    retorno = retornoseguidores
    #seguidos
    for cuenta in GetFollows(handle=client.me.handle, client=client, limit=limit):

        #buscar si existe como seguidor y si es asi
        esSeguidor = False
        for ind in range(0, len(retornoseguidores)-1):
            UsuarioQueSiguo = retornoseguidores[ind]
            #
            # si me sigue y coincide con que yo le siguo es amigo
            # si me sigue y no lo encuentro se queda en false

            if not esSeguidor:
                esSeguidor = UsuarioQueSiguo['did'] == cuenta['did']
            

        #si ya lo encuentro como siguiendo y lo siguo tengo que marcarlo como follow
        #si no lo encuentro lo añado como dejar de seguir

        if not esSeguidor:
            did = cuenta['did']
            handle = cuenta['handle']
            avatar = cuenta['avatar']
            display_name = cuenta['display_name']
            if display_name is None:
                display_name = handle 
            following = False
            profile_url = f'https://bsky.app/profile/' + handle.replace('@','')
            retorno.append({'did':did,'display_name':display_name,'handle':handle,'avatar':avatar,'following':following,'profile_url':profile_url,})
        else:
            UsuarioQueSiguo['following'] = True
        
    
    
    return retorno



@jwt.user_identity_loader
def user_identity_lookup(usuario):
    app.logger.debug('usuario')
    app.logger.debug(usuario)
    app.logger.debug('fin usuario')
    return usuario

@app.route('/', methods=['GET', 'POST'])
def inicio():
    app.logger.debug(f'raiz' )
    if request.method == 'POST':
        app.logger.debug(f'post 1' )
        username = request.form['username'] #request.json.get('username')
        password = request.form['password'] #request.json.get('password')
        app.logger.debug(f'hola con nombre de test {username}' )

        app.logger.debug(f'get principal3' )


        jwtbsk = autenticacionBlueSky(username=username, password=password)
        #el original que ya no sirve


        #refresh_token = create_refresh_token(identity=username)
        resp = redirect('/home')
        set_access_cookies(resp, jwtbsk)
        #set_access_cookies(resp, refresh_token)
        return resp

    elif request.method == 'GET':
        app.logger.debug(f'get principal' )
        token = request.cookies.get("access_token_cookie")
        app.logger.debug(f'get principal1' )
        if not token:
            app.logger.debug(f'get principal2' )
            resp = render_template('login.html')
            #unset_jwt_cookies(resp)    
            return resp
        else:
            app.logger.debug(f'get principal3' )
            resp = redirect('/home')
            return resp

        #ver si tenemos un token valido si lo tenemos y no a caducado pa lante si no a index borrando el token
        #return render_template('index.html')

@app.route('/hello/<name>')
@jwt_required()
def hello(name=None):
    return render_template('index.html', person=name)

@app.route('/logout')
def logout():
    resp = redirect('/')
    unset_jwt_cookies(resp)
    return resp



@app.route('/home')
@jwt_required()
def home():
    accounts = ListadoCuentas()
    app.logger.debug(accounts)
    return render_template("listado.html", accounts=accounts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
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
            <p><input type=text name=username value="">
            <p><input type=password name=password value="">
            <p><input type=submit value=Login>
        </form>
    '''

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
