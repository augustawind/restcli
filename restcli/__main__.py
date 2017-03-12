import argparse

from .cli import Program

parser = argparse.ArgumentParser()
parser.add_argument('collection',
                    help='Path to Collection file.')
parser.add_argument('environment', nargs='?',
                    help='Path to Environment file.')
args = parser.parse_args()

program = Program(args.collection, args.environment)
program.cmdloop()
