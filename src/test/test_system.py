# -------------------------------------------------------------------------------
# Name:        test_system
# Purpose:     System testing. This performs an equivalence partitioning test on
#              the entire system.
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Possible input to the system consists of strings.
# Input strings can be: acceptable commands, malformed commands, or unacceptable commands
# Acceptable commands are run:
# -- "exit" exits from the system
# -- "help" displays help text
# -- "say" is manually tested (e.g. by syntheiszing the samples)
# Malformed commands are:
# -- Unacceptable flags: command is rejected and help text is displayed
# --- This case only applies to 'help' and 'say', as exit will detect the existence of an argument
# -- Malformed argument: command is rejected and help text is displayed
# --- 'exit': any argument is refused
# --- 'help': any argument different from "exit", "help", "say", "commands" is refused
# --- 'say' : any argument that is not an acceptable utterance is refused; this is done asynchronously
# Unacceptable commands are any other string

# Global imports
import random
import re
from queue import Empty, Queue
from string import printable, ascii_lowercase
import sys
# Local imports
from ..mediator import Mediator
from ..utils import CommandException, RecoverableException
from ..user_interface import UserInterface
from ..test.test_planning import acceptable


def generate_cases():
    cases = []
    pr = printable.replace('\n', '')  # \n would just generate a new input
    # Unacceptable cases:
    while len(cases) < 20:
        case = ''.join(list(random.choice(pr) for _ in range(random.randrange(0, 20))))
        if not bool(re.search(r'^(exit |help |sys )', case)):
            cases.append(case)
    # Malformed flags:
    while len(cases) < 40:
        fl = ' '
        while bool(re.match(r'^( )*\Z', fl)):  # This would make it acceptable
            fl = ''.join(list(random.choice(pr) for _ in range(random.randrange(1, 10))))
        cases.append('help ' + fl + ' help')
        fl = '-p'
        while bool(re.match(r'^(( )*|-p)\Z', fl)):  # This would make it acceptable
            fl = ''.join(list(random.choice(pr.strip()) for _ in range(random.randrange(1, 10))))
        cases.append('say ' + fl + ' ba')
    # Malformed arguments:
    while len(cases) < 100:
        argument = 'help'
        while argument in ['help', 'exit', 'say', 'commands']:
            argument = ''.join(list(random.choice(ascii_lowercase+'_') for _ in range(random.randrange(1, 20))))
        cases.append('help ' + argument)
        cases.append('exit ' +
                     ''.join(list(random.choice(ascii_lowercase+'_') for _ in range(random.randrange(1, 20)))))
        argument = 'ba'
        while bool(re.match(acceptable, argument)):
            argument = ''.join(list(random.choice(ascii_lowercase+'_') for _ in range(random.randrange(0, 20))))

    # Acceptable arguments:
    cases.append('help help')
    cases.append('help commands')
    cases.append('help say')
    cases.append('help exit')
    cases.append('exit')

    return cases


# Tweaking the _interface class to obtain the exceptions:
class MockInterface(UserInterface):
    def __init__(self, input_pipe, output_pipe, exception_pipe):
        super(MockInterface, self).__init__(input_pipe, output_pipe)
        self._exception = exception_pipe

    def _handle_exception(self, ex):
        if isinstance(ex, Empty):
            pass
        elif isinstance(ex, CommandException):
            self._exception.put(("CommandException ", str(ex)))
        elif isinstance(ex, RecoverableException):
            self._exception.put(("RecoverableException", str(ex)))
        else:
            self._exception.put(("UnknownException", str(ex)))
            self._terminate(str(ex))


UserInterface = MockInterface


# Reproducing test-friendly main function; MockInterface is used and no user input is asked.
# Aside from this, this is equivalent to the system entrypoint function
def mock_main(exception_queue: Queue, input_inputs=None):
    if input_inputs is None:
        inputs = []
    else:
        inputs = input_inputs

    # Creates queue for user commands
    mediator_input = Queue(0)
    # Creates return queue for mediator's message passing
    interface_input = Queue(0)

    try:  # Create the mediator
        mediator = Mediator(mediator_input, interface_input)  # raises Exception, unrecoverable
    except Exception as ex:
        print("Failure initializing the mediator:\n" + str(ex) + '\nExiting...')
        sys.exit()
    try:  # Create the interface
        interface = MockInterface(interface_input, mediator_input, exception_queue)
    except Exception as ex:
        print("Failure initializing the interface:\n" + str(ex) + "\nExiting...")
        if mediator.is_alive():
            mediator.kill()
            mediator.join()
        sys.exit()

    try:  # Start the two threads:
        mediator.start()
        interface.start()
    except Exception as ex:
        print("Failure starting:\n" + str(ex) + "\nExiting...")
        if mediator.is_alive():
            mediator.kill()
            mediator.join()
        if interface.is_alive():
            interface.kill()
            interface.join()
        sys.exit()

    print("System ready.\n"
          "Type 'help commands' for a list of available commands")
    while interface.is_alive():
        try:
            # For testing purposes:
            while len(inputs) != 0:
                u_input = inputs.pop(0)
                interface_input.put(("input", u_input))
            # Actual user input is not asked otherwise the test excepts
            break

        except Exception as ex:
            if not isinstance(ex, EOFError):
                print("Unexpected exception:\n" + str(ex) + "\nExiting...")
                break

    try:
        if mediator.is_alive():
            mediator.kill()
            mediator.join()
    except Exception as ex:
        print("Unexpected exception:\n" + str(ex) + "\nExiting...")

    try:
        if interface.is_alive():
            interface.kill()
            interface.join()
    except Exception as ex:
        print("Unexpected exception:\n" + str(ex) + "\nExiting...")


def test_system():
    # Test setup:
    # Redirect input to file:
    old_stdout = sys.stdout
    new_stdout = open('test_results', 'w+')
    sys.stdout = new_stdout
    exception_queue = Queue(0)

    # Run tests:
    cases = generate_cases()
    mock_main(exception_queue, cases)

    # Check results:
    sys.stdout = old_stdout
    new_stdout.close()
    results = open('test_results', 'r').readlines()[21:]  # First 21 lines are initialization
    print(results)
    print(len(results))
    print(exception_queue.qsize())
    for i in range(20):
        exc = exception_queue.get_nowait()
        assert ('Unexpected character' in exc[1] or
                'Empty input' in exc[1] or
                'not recognised as an available command' in exc[1])
    for i in range(20, 40):
        exc = exception_queue.get_nowait()
        assert 'not a properly formed flag' in exc[1]
    for i in range(40, 100):
        exc = exception_queue.get_nowait()
        assert ('Wrong form:' in exc[1] or
                'No help text' in exc[1])

    expected_results = ["help [command|'commands']\n", "  This command displays explanatory text for (command)\n",
                        "  'help commands' displays a list of available commands\n",
                        "Here is a list of available commands:\n", "  exit\n", "  help [command]\n",
                        "  say [-p] word(_word)*\n", "say [-p] word(_word)*\n",
                        "  This command synthesizes the utterance. Words must be separated by '_'\n",
                        "  Allowed syllables are: b[aiu], d[aiu], ghi, g[au], gli, gli[au], "
                        "l[aiu], m[aiu], n[aiu], v[aiu], z[aiu]\n",
                        "  It's advised to only use: ba, da, di, ga, gli, glia, gli, gliu, la, li, lu, "
                        "ma, mi, mu, na, ni, nu, va, vi, vu, za, zi, zu\n",
                        "  Setting the flag -p will show the trajectory of single articulators before synthesis\n",
                        "exit\n", "  This command terminates outstanding threads and exits the program\n",
                        "  Warning: this command will kill any ongoing synthesis jobs\n"]
    for i in range(len(expected_results)):
        assert results[i] == expected_results[i]


if __name__ == '__main__':
    test_system()
