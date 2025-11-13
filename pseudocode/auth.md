```
from os import getenv

from dotenv import load_dotenv
from github import Auth, Github
from pygit2 import RemoteCallbacks, UserPass


def get_github() -> Github:
    token = get_github_token()
    auth=Auth.Token(token)
    return Github(auth)


def get_remote_callbacks() -> RemoteCallbacks:
    token = get_github_token()
    credentials = UserPass("x-access-token", token)
    return RemoteCallbacks(credentials)


def get_github_token():
    load_dotenv()
    return getenv("GITHUB_TOKEN")
```
