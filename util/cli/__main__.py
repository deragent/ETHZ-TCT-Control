if __name__ == "__main__":

    # Inspired by: https://opensource.com/article/17/5/4-practical-python-libraries

    import prompt_toolkit as pt
    import argparse
    import sys

    import numpy as np

    from tct.lab.control import *
    from tct.logger import Logger

    from .handler import *

    def printError(msg):
        pt.print_formatted_text(pt.HTML(f'<ansibrightred>ERROR: {msg}!</ansibrightred>'))
    def printWarning(msg):
        pt.print_formatted_text(pt.HTML(f'<ansiyellow>WARNING: {msg}!</ansiyellow>'))


    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Command-Line Interface (CLI) for the TCT Setup')
    parser.add_argument('--vlimit', '-V', type=float, required=True,
                        help='Voltage limit for the high-voltage PSU [V].')
    parser.add_argument('--ilimit', '-I', type=float, required=True,
                        help='Current limit for the high-voltage PSU [mA].')
    parser.add_argument('--no-laser', dest='laser', action='store_false',
                        help='Do not use the laser - For source type operations!')

    args = parser.parse_args()

    if np.abs(args.vlimit) > 1000:
        printError('|V-Limit| must be smaller than 1kV!')
        sys.exit(-1)

    if np.abs(args.ilimit) > 20:
        printError('|I-Limit| must be smaller than 20mA!')
        sys.exit(-1)


    # Create a logger
    log = Logger('.tct_cli.log', print=True, debug=False)

    # Create all Command Handlers
    handlers = {}
    handlers['amp'] = AmpHandler(log=log)
    handlers['bias'] = BiasHandler(VLimit=args.vlimit, ILimit=args.ilimit*1e-3, log=log)
    handlers['stage'] = StageHandler(log=log)
    handlers['temp'] = TempHandler(log=log)

    # TODO Implement Scope Handler / Unify with viewer
    # handlers['scope'] = ....
    handlers['view'] = ViewHandler(log=log)

    if args.laser:
        handlers['laser'] = LaserHandler(log=log)

    # Create the auto-complete command dict
    command_dict = {
        'off': None,
        'exit': None,
        'quit': None,
    }
    for key, handler in handlers.items():
        command_dict[key] = handler.commandDict()

    command_completer = pt.completion.NestedCompleter.from_nested_dict(command_dict)

    ## TODO add status rprompt

    # Run the main prompt
    while 1:
        try:
            user_input = pt.prompt('TCT > ',
                history = pt.history.FileHistory('.tct_history'),
                auto_suggest = pt.auto_suggest.AutoSuggestFromHistory(),
                completer = command_completer
            )
        except KeyboardInterrupt as e:
            break

        commands = user_input.lower().split(' ')

        if len(commands) < 1:
            continue

        cmd = commands[0]
        rest = commands[1:]

        if cmd in ['quit', 'exit']:
            break

        elif cmd in ['off']:
            result = pt.shortcuts.yes_no_dialog(
                title='System Off',
                text='Do you want to turn all components off?'
            ).run()
            if result:
                for key in ['laser', 'amp', 'bias']:
                    if key in handlers:
                        handlers[key].off()

            continue

        elif cmd in ['on']:
            for key in ['laser', 'amp', 'bias']:
                if key in handlers:
                    handlers[key].on()

            continue

        if len(rest) < 1:
            printError('Missing arguments!')
            continue

        if cmd in handlers:
            handler = handlers[cmd]
            ret = handler.handle(rest)
            if isinstance(ret, CommandHandler.Error):
                printError(ret)
            elif isinstance(ret, CommandHandler.Warning):
                printWarning(ret)
            elif ret is not None:
                print(ret)
        else:
            printWarning(f'Command [{cmd}]')

    ## TODO handle safe shutdown if wanted

    if 'view' in handlers:
        handlers['view'].terminate()
