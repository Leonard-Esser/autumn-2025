from os import getenv

from dotenv import load_dotenv
from github import Auth, Github
from pygit2 import RemoteCallbacks, UserPass


def get_github():
    token = _get_github_token()
    auth=Auth.Token(token)
    return Github(auth=auth)


def get_remote_callbacks():
    token = _get_github_token()
    credentials = UserPass("x-access-token", token)
    return RemoteCallbacks(credentials)


def _get_github_token():
    load_dotenv()
    return getenv("GITHUB_TOKEN")