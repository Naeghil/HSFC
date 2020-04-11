# -------------------------------------------------------------------------------
# Name:        main
# Purpose:     Main module of the application, system entry point
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import sys
from queue import Queue
# Local imports
from src.user_interface import UserInterface
from src.mediator import Mediator


def main(input_inputs=None):  # inputs used for testing purposes
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
        interface = UserInterface(interface_input, mediator_input)
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
            # Actual user input:
            u_input = input()
            interface_input.put(("input", u_input))

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


if __name__ == '__main__':
    inp = list(line.replace('\n', '') for line in sys.stdin.readlines())
    main(inp)
