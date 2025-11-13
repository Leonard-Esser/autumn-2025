```
def get_sample():
    return {get_full_name_of_some_repo(), "tensorflow/tensorflow"}


def get_full_name_of_some_repo() -> str:
    return "microsoft/vscode"


def main():
    print(get_sample())


if __name__ == "__main__":
    main()
```