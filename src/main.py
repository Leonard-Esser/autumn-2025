import config
from sampling import get_sample


def main():
    print("Hello from autumn-2025!")
    print(f"The configured sample size is: {config.SAMPLE_SIZE}")
    sample = get_sample()
    print(sample)


if __name__ == "__main__":
    main()
