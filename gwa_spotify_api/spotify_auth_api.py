import json
import os
import pickle

from rauth import OAuth2Service

from gwa_spotify_api.spotify_api import SpotifyAPI


TOKEN_PICKLE_FILENAME = 'spotify-token.pickle'

SPOTIFY_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_ACCESS_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://accounts.spotify.com'

class SpotifyAuthAPI(SpotifyAPI):

    def __init__(self, assign_token=True, config=None, scopes_list=None):
        SpotifyAPI.__init__(self, assign_token=False, config=config)

        self.callback_url = self.config.get(
            'SPOTIFY_CALLBACK_URL',
            os.environ.get('SPOTIFY_CALLBACK_URL')
        )

        self.client_id = self.config.get(
            'SPOTIFY_CLIENT_ID',
            os.environ.get('SPOTIFY_CLIENT_ID')
        )

        self.client_secret = self.config.get(
            'SPOTIFY_CLIENT_SECRET',
            os.environ.get('SPOTIFY_CLIENT_SECRET')
        )

        if scopes_list is None:
            scopes_list = [
                'user-top-read',
                'user-library-read',
                'user-read-birthdate',
                'playlist-read-private',
                'user-read-private',
                'user-read-email',
                'playlist-modify-public',
                'playlist-modify-private',
                'user-follow-read'
            ]

        self.scope = ' '.join(scopes_list)

        self.service = OAuth2Service(
            name='spotify',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url=SPOTIFY_AUTHORIZE_URL,
            access_token_url=SPOTIFY_ACCESS_TOKEN_URL,
            base_url=SPOTIFY_API_BASE_URL)

        if assign_token:
           self.assign_token()

    def assign_token(self, token=None):
        if token is not None:
            self.token = token
        else:
            try:
                self.token = pickle.load(open(TOKEN_PICKLE_FILENAME,'rb'))
            except:
                self.get_token_flow()

    def get_authorize_url(self):
        params = dict(
            scope=self.scope,
            response_type='code',
            redirect_uri=self.callback_url)

        url = self.service.get_authorize_url(**params)

        return url

    def get_access_token(self, auth_code):
        token = self.service.get_access_token(
            data={
                'code':auth_code,
                'grant_type':'authorization_code',
                'redirect_uri':self.callback_url
            },
            method='POST',
            headers={'Authorization': 'Basic ' + self._get_authorization_string(client_id, client_secret)},
            decoder=json.loads)

        self.token = token

        return token


    def get_token_flow(self):
        '''use from terminal'''
        authorize_url = self.get_authorize_url()

        message = (
            '\nvisit the following url and enter the "code" parameter from the url you are redirected to here.'
            '\n\n{}\n'
            '\n--->'
        )
        message = message.format(authorize_url)

        auth_code = input(message)

        token = self.get_access_token(self, auth_code)

        pickle.dump(token, open(TOKEN_PICKLE_FILENAME,'wb'))

if __name__ == '__main__':
    # test Auth API
    api = SpotifyAuthAPI()
    api.assign_token()
    print(api.get('me'))
