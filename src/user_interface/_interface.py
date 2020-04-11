# -------------------------------------------------------------------------------
# Name:        interface
# Purpose:     Handles interaction between the user and the system
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
from queue import Queue, Empty
# Local imports
from ..utils import RecoverableException, UnrecoverableException, HSFCThread, CommandException
from ._interface_utils import parse, help_text
from ._interface_utils import unknown_command, help_function


class UserInterface(HSFCThread):
    def __init__(self, input_queue: Queue,  # Input to the interface
                 mediator_input: Queue):  # Output from the interface
        super(UserInterface, self).__init__(input_queue, mediator_input)

        # Command dictionary:
        self._commands = {
            'exit': self._exit,
            'help': help_function,
            'say': self._say
        }

        self._UI_changes = {
            'message': print,
            'termination': self._terminate
        }

    def _say(self, flags, argument):
        if argument == 'say' or len(flags) > 1:
            raise CommandException("Wrong form: "
                                   "say " + ''.join(list(f+' ' for f in flags)) + argument +
                                   "\n" + help_text['say'])
        toPlot = False
        if len(flags) != 0:
            found = False
            if '-p' in flags:
                toPlot = True
                found = True
            if not found:
                raise CommandException("Unrecognised flag.\n" + help_text['say'])
        self._output.put((toPlot, argument))

    def _exit(self, flags, argument):
        if flags or argument:
            raise CommandException("Wrong form: "
                                   "exit " + ''.join(list(f+' ' for f in flags)) + argument +
                                   "\n" + help_text['exit'])
        self._terminate()

    def _terminate(self, failure=None):
        if failure:  # This is the cause of abrupt termination
            print("The interface must terminate because:\n"+str(failure))
        self.kill()
        print("Press ENTER to exit.")

    def _process_UI_changes(self, kind, argument):
        try:
            execute_change = self._UI_changes.get(kind, None)
            if execute_change:
                execute_change(argument)
            else:
                raise UnrecoverableException("Unknown UI change "+kind+" with argument "+str(argument))
        except UnrecoverableException as ex:
            self._terminate("The interface must terminate because: \n" + str(ex))

    def _process_user_input(self, user_input):
        command_label, flags, argument = parse(user_input)
        command = self._commands.get(command_label, None)
        if command:
            command(flags, argument)
        else:
            unknown_command(command_label)

    def _handle_exception(self, ex):
        if isinstance(ex, Empty):
            pass
        elif isinstance(ex, CommandException):
            print(str(ex))
        elif isinstance(ex, RecoverableException):
            print(str(ex))
        else:
            self._terminate(str(ex))

    def run(self):
        while self.live():
            try:
                # Extract input
                kind, item = self._input.get_nowait()
                self._input.task_done()
                # Execute appropriately
                if kind == "input":
                    self._process_user_input(item)
                else:
                    self._process_UI_changes(kind, item)
            except Exception as ex:
                self._handle_exception(ex)
