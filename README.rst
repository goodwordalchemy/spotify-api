This module provides a wrapper for the spotify web api.  Both 'Client Credentials' and 'Authorization Code' flows are supported.  To use the former check spotify_api.py.  To use the latter check out spotify_auth_api.py.  You need to create an app on the spotify developer site and set environment variables for SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_CALLBACK_URL.

You can pip install this module `pip install gwa_spotify_api`.  If you do that, you still need to set those environment variables.
