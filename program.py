from textx.metamodel import metamodel_from_file
from test_wrapper import TestWrapper
import unittest
from random import randint
import re

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'_'):
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(word.split())
    return unicode(delim.join(result))

def exec_code(body, self = None):
    exec "\n".join(body) in globals(), locals()

class Context:
    def __init__(self, *args, **kwargs):
        self.description = kwargs['description']
        if 'before' in kwargs:
            self.before = kwargs['before']
        else:
            self.before = []
        if 'after' in kwargs:
            self.after = kwargs['after']
        else:
            self.after = []
        if 'tests' in kwargs:
            self.tests = kwargs['tests']
        else:
            self.tests = []

    def run(self):
        for test in self.tests:
            test.run(self.before, self.after)

class Test:
    def __init__(self, context, test):
        self.context = context
        self.test = test

    def run(self, before_callbacks, after_callbacks):
        body = self.test.body

        def test_function(self):
            for before in before_callbacks:
                exec_code(before.body)

            exec_code(body, self)

            for after in after_callbacks:
                exec_code(after.body)

        setattr(
            TestWrapper,
            slugify(
                "test_%s_%s" %
                (self.context.description, self.test.description)
            ),
            test_function
        )

class Flow:
    def __init__(self, *args, **kwargs):
        self.contexts = []

    def build(self, command):
        if type(command).__name__ == 'ContextCommand':
            context = Context(
                description = command.description
            )
            self.contexts.append(context)
            for body in command.body:
                self.build(body)
        else:
            if not self.contexts:
                context = Context(
                    description = "MainContext"
                )
            else:
                context = self.contexts[-1]

            if len(self.contexts) > 1:
                last_context = self.contexts[-2]

                if len(context.before) == 0:
                    for last_before in last_context.before:
                        context.before.append(last_before)

                if len(context.after) == 0:
                    for last_after in last_context.after:
                        context.after.append(last_after)

            if type(command).__name__ == 'CallbackCommand':
                if command.callback == 'before':
                    context.before.append(command)
                else:
                    context.after.append(command)
            else:
                test = Test(
                    context = context,
                    test = command
                )
                context.tests.append(test)

        return self.contexts

    def run(self):
        [context.run() for context in self.contexts]

mm = metamodel_from_file('grammar.tx')
model = mm.model_from_file('program.api')

for command in model.commands:
    flow = Flow()
    flow.build(command)
    flow.run()

if __name__ == '__main__':
    unittest.main()
