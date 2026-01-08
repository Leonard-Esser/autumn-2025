from os import getenv

from dotenv import load_dotenv
from github import Auth, Github
from pygit2 import RemoteCallbacks, UserPass


def get_github():
    token = get_github_token()
    auth=Auth.Token(token)
    return Github(auth=auth)


def get_remote_callbacks():
    token = get_github_token()
    credentials = UserPass("x-access-token", token)
    return RemoteCallbacks(credentials)


def get_github_token():
    load_dotenv()
    return getenv("GITHUB_TOKEN")


def main():
    github = get_github()
    print(github)
    remote_callbacks = get_remote_callbacks()
    print(remote_callbacks)


if __name__ == "__main__":
    main()