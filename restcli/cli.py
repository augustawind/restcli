import argparse

from app import App


def run():
    parser = argparse.ArgumentParser(prog='restcli')

    # Positional arguments
    parser.add_argument('group')
    parser.add_argument('request', nargs='?', default=None)
    parser.add_argument('attr', nargs='?', default=None)

    # Options
    parser.add_argument('-c', '--collection')
    parser.add_argument('-e', '--env')

    # Flags
    parser.add_argument('-i', '--inspect', action='store_true')
    parser.add_argument('-s', '--save-env', action='store_true')

    args = parser.parse_args()

    program = App(args.collection, args.env)

    if args.inspect:
        program.inspect(args.group, args.request, args.attr)
    else:
        program.run(args.group, args.request)
        if args.save_env:
            program.save()
