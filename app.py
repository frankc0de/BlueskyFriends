import os
import time
import datetime

from flask import Flask, session, \
                render_template, \
                abort, redirect, url_for, request, json , jsonify

from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, \
                               jwt_required , set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt

from Bluesky import cbluesky 

from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

app = Flask(__name__)

app.secret_key = os.getenv('secret_key')
app.config["JWT_SECRET_KEY"] = app.secret_key 
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config["JWT_ACCESS_COOKIE_NAME"] = 'access_token_cookie'
jwt = JWTManager(app)
bluesky = cbluesky()


def ListadoCuentas():
    claims = get_jwt()
    session_string = claims["session_string"] # identity
    bluesky.iniciaSessionSessionString(session_string=session_string)
    
    retorno = []
    retornoseguidores = []
    
    # todos a los que seguimos tienen que tener el boton de dejar de seguir
    # me hace falta algo que me diga que me sigue pero que no le siguo
    # os seguis mutuamente

    seguimiento = ''


    for cuenta in bluesky.GetFollowers(handle=bluesky.client.me.handle):
        did = cuenta['did']
        handle = cuenta['handle']
        avatar = cuenta['avatar']
        display_name = cuenta['display_name']
        description = cuenta['description']
        if description is None:
            description = ''
        if display_name is None:
            display_name = handle 
        following = False
        seguimiento = 'te sigue pero tu no le sigues'
        profile_url = f'https://bsky.app/profile/' + handle.replace('@','')
        retornoseguidores.append({'did':did,
                                  'display_name':display_name,
                                  'handle':handle,
                                  'avatar':avatar,
                                  'following':following,
                                  'profile_url':profile_url,
                                  'seguimiento':seguimiento,
                                  'description':description,})
    
    retorno = retornoseguidores
    #seguidos
    for cuenta in bluesky.GetFollows(handle=bluesky.client.me.handle):

        #buscar si existe como seguidor y si es asi
        esSeguidor = False
        for ind in range(0, len(retornoseguidores)-1):
            UsuarioQueSiguo = retornoseguidores[ind]
            #
            # si me sigue y coincide con que yo le siguo es amigo
            # si me sigue y no lo encuentro se queda en false

            if not esSeguidor:
                esSeguidor = UsuarioQueSiguo['did'] == cuenta['did']

            if UsuarioQueSiguo['did'] == cuenta['did']:
                retorno[ind]['seguimiento'] = 'os seguis mutuamente'


            if retorno[ind]['seguimiento'] == 'le sigues pero no te sigue':
                retorno[ind]['following'] = True
            elif retorno[ind]['seguimiento'] == 'te sigue pero tu no le sigues':
                retorno[ind]['following'] = False
            elif retorno[ind]['seguimiento'] == 'os seguis mutuamente':
                retorno[ind]['following'] = True


            

        #si ya lo encuentro como siguiendo y lo siguo tengo que marcarlo como follow
        #si no lo encuentro lo añado como dejar de seguir

        if not esSeguidor:
            seguimiento = 'le sigues pero no te sigue'
            


        if not esSeguidor:
            did = cuenta['did']
            handle = cuenta['handle']
            avatar = cuenta['avatar']
            display_name = cuenta['display_name']
            description = cuenta['description']
            if description is None:
                description = ''
            if display_name is None:
                display_name = handle


            if seguimiento == 'le sigues pero no te sigue':
                following = True
            elif seguimiento == 'te sigue pero tu no le sigues':
                following = False
            elif seguimiento == 'os seguis mutuamente':
                following = True

            profile_url = f'https://bsky.app/profile/' + handle.replace('@','')
            retorno.append({'did':did,
                            'display_name':display_name,
                            'handle':handle,
                            'avatar':avatar,
                            'following':following,
                            'profile_url':profile_url,
                            'seguimiento':seguimiento,
                            'description':description,})
        else:
            UsuarioQueSiguo['following'] = True
        
    
    
    return retorno



'''@bluesky.jwt.user_identity_loader
def user_identity_lookup(usuario):
    app.logger.debug('usuario')
    app.logger.debug(usuario)
    app.logger.debug('fin usuario')
    return usuario'''

# recupera la cookie el token existente aunque este o no caducado
def RecuperaCookie():
    return request.cookies.get("access_token_cookie")

# si existe o no la cookie
def ExisteCookie():
    return RecuperaCookie() is not None

# resp es la respuesta de la redireccion
# usuario y clave las credenciales 
'''def RecuperaToken(resp, username:str, password:str):
    if ExisteCookie():
        jwttoken = RecuperaCookie()
    else:
        jwttoken = bluesky.utenticacionBlueSky(username=username, password=password)
        # si no existe la cookie hay que generarla con los datos de las credenciales
        bluesky.set_access_cookies(resp, jwttoken)'''


def CreaToken():
    session_string = bluesky.client.export_session_string()
    did = bluesky.client.me.did
    access_token = create_access_token(identity=did,
                                        additional_claims={
                                            "session_string": session_string
                                            }, fresh=True)
    return access_token

# pagina inicial raiz
@jwt_required(optional=True)
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    
    if request.method == 'POST':
        username = request.form['username'] #request.json.get('username')
        password = request.form['password'] #request.json.get('password')
        #app.logger.debug(f'hola con nombre de test {username}' )

        #lanzamos el metodo de logar en bluesky
        bluesky.iniciaSessionUsernamePassord(username=username, password=password)
        access_token = CreaToken()


        #jwtbsk = bluesky.autenticacionBlueSky(username=username, password=password)
        #refresh_token = create_refresh_token(identity=username)
        resp = redirect('/home')
        set_access_cookies(resp, access_token)

        #RecuperaToken(resp=resp,username=username, password=password)
        #bluesky.set_access_cookies(resp, jwtbsk)
        #set_access_cookies(resp, refresh_token)
        return resp

    elif request.method == 'GET':
        # si no existe la cookie lo manda a la pagina de introducir las credenciales
        # si existe lo envia a home
        # ojo falta checkear si es valido aun el token de bluesky y si no lo es lanzar un refresh
        if not ExisteCookie():
            resp = render_template('login.html')  
            return resp
        else:
            resp = redirect('/home')
            #app.logger.debug('iniciamos client bluesky con session string')
            claims = get_jwt()
            session_string = claims["session_string"] # identity
            bluesky.iniciaSessionSessionString(session_string=session_string)
            return resp

        #ver si tenemos un token valido si lo tenemos y no a caducado pa lante si no a index borrando el token
        #return render_template('index.html')

'''@app.route('/hello/<name>')
@jwt_required()
def hello(name=None):
    return render_template('index.html', person=name)'''

@app.route('/logout')
def logout():
    resp = redirect('/')
    unset_jwt_cookies(resp)
    return resp

@app.route('/followers')
@jwt_required()
def followers():
    #no tengo el client?

    accounts = ListadoCuentas()
    #app.logger.debug(accounts)
    return render_template("listado.html", accounts=accounts)

# este seria el menu principal con las opciones
@app.route('/home')
#pendiete de activar @jwt_required()
def home():
    return render_template("menu.html")



'''@app.route('/register', methods=['GET', 'POST'])
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
        #access_token = bluesky.create_access_token(identity=username, fresh=True)
        #refresh_token = create_refresh_token(identity=username)
        resp = redirect('/home')
        #bluesky.set_access_cookies(resp, access_token)
        #set_access_cookies(resp, refresh_token)
        return resp
    return 'v''
        <form method="post">
            <p><input type=text name=username value="">
            <p><input type=password name=password value="">
            <p><input type=submit value=Login>
        </form>
    'v''
'''
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# + Seguir 
# Siguiendo
