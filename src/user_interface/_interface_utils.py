# -------------------------------------------------------------------------------
# Name:        _interface_utils
# Purpose:     Utility functions for the interface
#
# Author:      Naeghil
#
# Last mod:    9/04/2020
# Copyright:   (c) Naeghil 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# Global imports
import re
# Local imports
from ..utils import RecoverableException, CommandException

# Help text
help_text = {
    "commands":
        "Here is a list of available commands:\n"
        "  exit\n"
        "  help [command]\n"
        "  say [-p] word(_word)*",
    "help":
        "help [command|'commands']\n"
        "  This command displays explanatory text for (command)\n"
        "  'help commands' displays a list of available commands",
    "exit":
        "exit\n"
        "  This command terminates outstanding threads and exits the program\n"
        "  Warning: this command will kill any ongoing synthesis jobs",
    "say":
        "say [-p] word(_word)*\n"
        "  This command synthesizes the utterance. Words must be separated by '_'\n"
        "  Allowed syllables are: b[aiu], d[aiu], ghi, g[au], gli, gli[au], l[aiu], m[aiu], n[aiu], v[aiu], z[aiu]\n"
        "  It's advised to only use: ba, da, di, ga, gli, glia, gli, gliu, la, li, lu, "
        "ma, mi, mu, na, ni, nu, va, vi, vu, za, zi, zu\n"
        "  Setting the flag -p will show the trajectory of single articulators before synthesis"
}


# Non-member commands and helpers:
def help_function(flags, argument):
    if flags:
        raise CommandException("Wrong form: "
                                       "help " + ''.join(list(f+' ' for f in flags)) + argument +
                                       "\n" + help_text['help'])
    h_text = help_text.get(argument, None)
    if h_text:
        print(h_text)
    else:
        raise RecoverableException('No help text available for ' + argument)


def unknown_command(command):
    raise RecoverableException(command+" is not recognised as an available command.\n" +
                               help_text.get("commands", ''))


# Command validation and parsing:
def validate(command_list,
             isIllegal=re.compile(r'[^a-z_]').search,  # Commands and inputs are allowed only alphabetic lowercases or _
             isLegalFlag=re.compile(r'-([a-z]\Z)+').match):  # flags are only of the form -flag
    command_length = len(command_list)
    if command_length == 0:
        raise CommandException("Empty input.")
    if isIllegal(command_list[0]):
        raise CommandException("Unexpected character in the command '"+command_list[0]+"'")
    if isIllegal(command_list[-1]):
        raise CommandException("Unexpected character in the argument '"+command_list[-1]+"'")
    if command_length > 2:
        for flag in command_list[1:-1]:
            if not isLegalFlag(flag):
                raise CommandException(flag + " is not a properly formed flag. Flags must be of the form:\n -flag")


def parse(user_input):
    command_list = user_input.split()
    try:
        validate(command_list)
        if len(command_list) == 1:
            return command_list[0], [], ''
        if len(command_list) == 2:
            return command_list[0], [], command_list[1]
        return command_list[0], command_list[1:-1], command_list[-1]
    except CommandException as ex:
        if "Empty" in str(ex):
            raise CommandException(str(ex))
        else:
            raise CommandException(str(ex)+'\n'+help_text.get(command_list[0], ''))
