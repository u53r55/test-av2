import sys, os
import inspect
import logging
import abc
import ast
from Decorators import returns


def initCommands():
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)
    for m in Command.commands:
        try:
            Command.knownCommands[m] = __import__("Command_%s" % m)
        except:  # pragma: no cover
            import AVCommon
            Command.knownCommands[m] = __import__("AVCommon.Command_%s" % m)


class Command():
    __metaclass__ = abc.ABCMeta

    commands = ["START", "END", "STARTVM"]
    knownCommands = dict(zip(commands,  [None] * len(commands)))

    payload = ""
    success = True

    """command"""
    def __init__(self, name):
        self.name = name
        initCommands()
        assert(len(Command.knownCommands) > 0)

    @staticmethod
    def unserialize(serialized):
        initCommands()

        #ident, command, answer = serialized.split(',', 2)
        #assert(ident == "CMD")
        command, success, payload = serialized

        className = "Command_%s" % command
        #print Command.knownCommands
        assert(isinstance(success, bool) or success is None)
        assert(isinstance(command, str))
        assert(command in Command.knownCommands.keys())

        #logging.debug("dir: ", dir(Command.knownCommands[command]))
        if command in Command.knownCommands:
            m = Command.knownCommands[command]
            c = getattr(m, className)
            cmd = c(command)
            try:
                cmd.payload = ast.literal_eval(payload)
            except:
                cmd.payload = payload
            cmd.success = success
            return cmd

    def serialize(self):
        return (self.name, self.success, self.payload)

    """ server side """
    @abc.abstractmethod
    def onInit(self, args):
        pass  # pragma: no cover

    @abc.abstractmethod
    def onAnswer(self, success, answer):
        pass  # pragma: no cover

    """ client side """
    @abc.abstractmethod
    def Execute(self, args):
        pass  # pragma: no cover

    def __str__(self):
        return "%s,%s,%s" % (self.name, self.success, self.payload)

