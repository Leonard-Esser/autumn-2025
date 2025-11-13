import config
from auth import get_github, get_remote_callbacks
from sampling import get_sample


def main():
    print("Hello from autumn-2025!")
    print(f"The configured sample size is: {config.SAMPLE_SIZE}")
    github = get_github()
    sample = get_sample()
    print(sample)
    remote_callbacks = get_remote_callbacks()


if __name__ == "__main__":
    main()
