import cmd
import json
import readline
from string import Template
from pprint import pformat

from restcli import Requestor

RESPONSE_TPL = Template('\n'.join([
    'HTTP ${status_code}',
    '${headers}',
    '',
    '${body}',
]))

class Program(cmd.Cmd):

    def __init__(self, groups_file, env_file):
        super().__init__()
        self.r = Requestor(groups_file, env_file)

        self.usage_info = {
            'run': 'Usage: run GROUP REQUEST'
        }

    def usage(self, command, msg):
        print(msg)
        print(self.usage_info[command])

    def do_run(self, arg):
        args = arg.split()
        if len(args) != 2:
            return self.usage('run', 'Invalid input.')

        group_name, request_name = args
        group = self.r.groups.get(group_name)
        if not group:
            return self.usage('run', "Group '{}' not found.".format(group_name))
        request = group.get(request_name)
        if not request:
            return self.usage('run', "Request '{}' not found in Group '{}'."
                              .format(request_name, group_name))

        response = self.r.request(group_name, request_name)

        output = RESPONSE_TPL.substitute(
            status_code=response.status_code,
            headers='\n'.join(['{}: {}'.format(k, v)
                               for k, v in response.headers.items()]),
            body=json.dumps(response.json(), indent=2),
        )
        print(output)

    def do_reload(self, arg):
        self.r.load_config()

    def do_env(self, arg):
        output = '\n'.join(['{}: {}'.format(k, v)
                            for k, v in self.r.env.items()])
        print(output)

if __name__ == '__main__':
    program = Program('examples/requests.yaml', 'examples/env.yaml')
    program.cmdloop()
