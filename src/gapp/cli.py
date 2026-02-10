import argparse

parser = argparse.ArgumentParser()
parser.add_argument("device")

def main():
    args = parser.parse_args()
    print(args)

