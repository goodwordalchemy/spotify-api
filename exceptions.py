import time


ERROR_LOG_FILENAME = 'apierrors.log'

INTERNAL_SERVER_ERROR_WAIT_TIME = 60


class SpotifyException(Exception):

    def __init__(self, response):
        try:
            response_json = response.json()

        except ValueError:
            response_json = response

        print('response: {}'.format(response_json))
        self.response_json = response_json

    def get_response(self):
        return self.response_json['error']

    def get_status_code(self):
        return str(self.response_json['error']['status'])

    def get_message(self):
        return self.response_json['error']['message']

    def log_to_file(self, api, filename=ERROR_LOG_FILENAME):
        most_recent_request = api.get_most_recent_request_address()
        line = '|'.join([self.get_status_code(), self.get_message(), most_recent_request]) + '\n'
        with open(filename, 'a') as logfile:
            logfile.write(line.encode("UTF-8"))


class SpotifyTimeoutError(SpotifyException):

    def __init__(self, response):
        SpotifyException.__init__(self, response)
        self.retry_after = response['headers']['Retry-After']

    def wait(self):
        print("exceeded rate limit.  Trying again in {} seconds...".format(self.retry_after))
        time.sleep(self.retry_after)


class SpotifyAuthenticationError(SpotifyException):

    def __init__(self, response):
        print("token timed out.  Getting new authentication token")
        if 'data/spotify-token.pickle' in os.listdir('.'):
            os.remove('data/spotify-token.pickle')
        SpotifyException.__init__(self, response)

    def authenticate(self):
        return SpotifyAuthAPI()


class SpotifyNotFoundError(SpotifyException):
    pass


class SpotifyInvalidRequestError(SpotifyException):
    pass


class SpotifyInternalServerError(SpotifyException):
    def __init__(self, response):
        SpotifyException.__init__(self, response)
        print("iternal server error.  Going to sleep for {}".format(INTERNAL_SERVER_ERROR_WAIT_TIME))
        time.sleep(wait_time)
