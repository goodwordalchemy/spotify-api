import requests, base64, datetime, types, time, json, pickle, os

from exceptions import (
    SpotifyTimeoutError, SpotifyAuthenticationError,
    SpotifyNotFoundError, SpotifyInvalidRequestError,
)

MY_SPOTIFY_ID = os.environ.get('MY_SPOTIFY_ID')


def handle_http_errors(f):
    def wrapped_f(*args, **kwargs):
        for i in range(5):
            try:
                response = f(*args, **kwargs)
                return response
            except SpotifyTimeoutError as e:
                retry_after = e.wait()
                time.sleep(retry_after)
            except SpotifyAuthenticationError as e:
                pass
            except (SpotifyNotFoundError, SpotifyInvalidRequestError) as e:
                raise e
        raise SpotifyException(response.json())
    return wrapped_f


class SpotifyAPI(object):
    """API for making request for public data from spotify api ("Client Flow" Authentication style)

    Note: In to get private data, need to use SpotifyAuthAPI class.

    Must have the following environment variables set:

        SPOTIFY_CLIENT_ID
        SPOTIFY_CLIENT_SECRET

    Or you can pass a dictionary with those keys.
    """
    def __init__(self, config=None, use_default=False):

        self.request_epoch = time.time()
        self.time_between_requests = 1
        self.most_recent_request_address = None

        if config is not None:
            self.config = config
        else:
            self.config = {}
            self.config['SPOTIFY_CLIENT_ID'] = os.environ.get('SPOTIFY_CLIENT_ID')
            self.config['SPOTIFY_CLIENT_SECRET'] = os.environ.get('SPOTIFY_CLIENT_SECRET')

        self.assign_token()

    def _get_authorization_string(self, client_id, client_secret):
        encoded_auth_string = (client_id + ':' + client_secret).encode('ascii')
        encoded_auth_string = base64.b64encode(encoded_auth_string)

        return encoded_auth_string.decode('ascii')


    def assign_token(self):
        client_id = self.config['SPOTIFY_CLIENT_ID']
        client_secret = self.config['SPOTIFY_CLIENT_SECRET']

        auth_string = self._get_authorizization_string(client_id, client_secret)

        token = requests.post(
            'https://accounts.spotify.com/api/token',
            data={'grant_type':'client_credentials'},
            headers={'Authorization':'Basic ' + auth_string}
        )

        self.token = token.json()['access_token']

    def _get_url_endpoint(self, url, base_url='https://api.spotify.com/v1/'):
        return url[len(base_url):]

    def _get_header(self, header_data=None):
        if hasattr(self, 'token'):
            auth_header = {'Authorization': 'Bearer ' + self.token}
        else:
            auth_header = {}
        if header_data is not None:
            auth_header.update(header_data)
        return auth_header

    def _get_url(self, endpoint, version='v1'):
        return u'https://api.spotify.com/{version}/{endpoint}'.format(
            version=version,
            endpoint=endpoint
        )

    def _handle_response(self, response):
        if response.status_code < 400:
            response = response.json()
            if 'limit' in response.keys():
                return self._page_through_response(response)
            else:
                return response
        if response.status_code == 400:
            raise SpotifyInvalidRequestError(response)
        if response.status_code == 401:
            self.assign_token()
            raise SpotifyAuthenticationError(response)
        if response.status_code == 404:
            raise SpotifyNotFoundError(response)
        if response.status_code == 429:
            raise SpotifyTimeoutError(response)
        if response.status_code >= 500:
            raise SpotifyInternalServerError(response)
        raise SpotifyException(response)

    def _page_through_response(self, response, debug=True):
        items = []
        items.extend(response['items'])
        while True:
            next_page = response['next']
            if next_page is None: 
                break
            next_page = self._get_url_endpoint(next_page)   
            response = self.get(next_page)
            if isinstance(response, dict):
                items.extend(response['items'])
            elif isinstance(response, list):
                items.extend(response)
                break
            else:
                print(response)
                raise Exception("Error while paging through response.  most recent page was not of type dict or list, or if dict it was missing an 'items' field")
        return items

    def _manage_ratelimit(self):
        now = time.time()
        if now - self.request_epoch < self.time_between_requests:
            time.sleep(self.time_between_requests)
        self.request_epoch = now

    def get_most_recent_request_address(self):
        return self.most_recent_request_address

    @handle_http_errors
    def get(self, endpoint, params=None):
        url = self._get_url(endpoint)
        print(u"getting from {0}".format( url))
        self._manage_ratelimit()
        self.most_recent_request_address = endpoint
        r = requests.get(
            url,
            headers=self._get_header(),
            params=params)
        return self._handle_response(r)

    @handle_http_errors
    def post(self, endpoint, params=None, data=None):
        url = self._get_url(endpoint)
        print("posting to {}".format(url))
        self._manage_ratelimit()
        self.most_recent_request_address = endpoint
        r = requests.post(
            url,
            headers=self._get_header(),
            params=params,
            data=json.dumps(data))
        return self._handle_response(r)


    @staticmethod
    def parse_datestring(spotify_date):
        return datetime.datetime.strptime(spotify_date, "%Y-%m-%dT%H:%M:%SZ")

if __name__ == '__main__':

    # test Client Auth Flow
    api = SpotifyAPI()
    print(api.get('users/{}'.format(MY_SPOTIFY_ID)))

