import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file')
    parser.add_argument('line')
    args = parser.parse_args()


if __name__ == '__main__':
    main()