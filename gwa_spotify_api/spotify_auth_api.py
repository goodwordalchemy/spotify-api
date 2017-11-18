import json
import os
import pickle

from rauth import OAuth2Service

from spotify_api import SpotifyAPI


class SpotifyAuthAPI(SpotifyAPI):

    def __init__(self, token=None, config=None):
        SpotifyAPI.__init__(self, config)
        if token is not None:
            self.token = token
        else:
           self.assign_token()

    scope = " ".join([
        'user-library-read',
        'user-read-birthdate',
        'playlist-read-private',
        'user-read-private',
        'user-read-email',
        'playlist-modify-public',
        'playlist-modify-private',
        'user-follow-read'
    ])

    def assign_token(self):
        try:
            self.token = pickle.load(open('data/spotify-token.pickle','rb'))
        except:
            self.get_token_flow()


    def get_token_flow(self):
        callback_url = self.config.get(
            'SPOTIFY_CALLBACK_URL',
            os.environ.get('SPOTIFY_CALLBACK_URL')
        )
        client_id = self.config.get(
            'SPOTIFY_CLIENT_ID',
            os.environ.get('SPOTIFY_CLIENT_ID')
        )
        client_secret = self.config.get(
            'SPOTIFY_CLIENT_SECRET',
            os.environ.get('SPOTIFY_CLIENT_SECRET')
        )
        self.service = OAuth2Service(
            name='spotify',
            client_id=client_id,
            client_secret=client_secret,
            authorize_url='https://accounts.spotify.com/authorize',
            access_token_url='https://accounts.spotify.com/api/token',
            base_url='https://accounts.spotify.com')

        params = dict(
            scope=self.scope,
            response_type='code',
            redirect_uri=callback_url)

        url = self.service.get_authorize_url(**params)
        print("visit this link and copy the code parameter:\n{}".format(url))

        auth_code = input("\n:")

        token = self.service.get_access_token(
            data={
                'code':auth_code,
                'grant_type':'authorization_code',
                'redirect_uri':callback_url
            },
            method='POST',
            headers={'Authorization': 'Basic ' + self._get_authorization_string(client_id, client_secret)},
            decoder=json.loads)
        pickle.dump(token, open('data/spotify-token.pickle','wb'))
        self.token = token

if __name__ == '__main__':
    # test Auth API
    api = SpotifyAuthAPI()
    api.assign_token()
    print(api.get('me'))
