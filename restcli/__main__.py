import argparse

from restcli.icli import Cmd


parser = argparse.ArgumentParser()
parser.add_argument('collection',
                    help='Path to Collection file.')
parser.add_argument('environment', nargs='?',
                    help='Path to Environment file.')
args = parser.parse_args()

cmd = Cmd(args.collection, args.environment)
cmd.cmdloop()
