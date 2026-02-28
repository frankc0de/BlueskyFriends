from atproto import AtUri, Client, models, IdResolver
import time
'''from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, \
                               jwt_required , set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt'''

class cbluesky():
    def __init__(self, client=None, limit:int=100):
        self.client = client
        self.limit = limit
   

    def iniciaSessionUsernamePassord( self, username:str, password:str):
        self.client = Client()
        self.client.login(username, password)

    def iniciaSessionSessionString( self, session_string:str):
        
        self.client = Client()
        self.client.login(session_string=session_string)

    # autenticamos en bluesky
    # buscamos la coookie y si existe recuperamos los datos JWT de session
    # si no existe autenticamos en bluesky y generamos token, creamos la cookie
    # en caso de error al usar el token de la cookie tenemos que lanzar el refresco y guardar en la cookie los datos 
    # retornamos el cliente
    # 
    '''def BlueSkyAuth(self):
        claims = get_jwt()
        session_string = claims["session_string"]      # identity
        client = Client()
        client.login(session_string=session_string)'''


    def GetFollowers(self, handle):
            lista = []
            Cursor = None
            Salir = False
            while not Salir:
                followers:models.AppBskyGraphGetFollowers.Response = self.client.get_followers(actor=handle,
                                                    cursor=Cursor,
                                                    limit=self.limit)
                
                for follower in followers.followers:
                    lista.append(follower)
                
                Cursor = followers.cursor
                if Cursor is None:
                    Salir = True
            return lista

    def GetFollows(self, handle):
            Cursor = None
            Salir = False
            lista = []
            while not Salir:

                error = True
                while error is True:
                    reintentos = 0
                    try:
                        follows = self.client.get_follows(actor=handle,
                                                        cursor=Cursor,
                                                        limit=self.limit)
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
'''def autenticacionBlueSky(self, username, password):
    client = Client()
    client.login(username, password)
    session_string = client.export_session_string()
    did = client.me.did
    access_token = create_access_token(identity=did,
                                        additional_claims={
                                            "session_string": session_string
                                            }, fresh=True)


    return access_token'''

'''app.logger.debug('saca el usuario del token')
claims = get_jwt()
session_string = claims["session_string"]      # identity
    
client = cbluesky.Client()
client.login(session_string=session_string)
limit = 100'''

