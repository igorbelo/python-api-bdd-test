from textx.metamodel import metamodel_from_file
import unittest
from random import randint
import re
import unittest

class TestWrapper(unittest.TestCase):
    pass

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'_'):
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(word.split())
    return unicode(delim.join(result))

def exec_code(body, code_before_resource = None, self = None):
    if code_before_resource:
        exec "\n".join(code_before_resource) in globals(), locals()

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
    def __init__(self, context, test, code_before_resource):
        self.code_before_resource = code_before_resource
        self.context = context
        self.test = test

    def run(self, before_callbacks, after_callbacks):
        body = self.test.body
        imports = self.code_before_resource

        def test_function(inner_self):
            for before in before_callbacks:
                exec_code(before.body)

            exec_code(body,
                      imports,
                      inner_self)

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
        self.code_before_resource = kwargs['code_before_resource']

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
                    code_before_resource = self.code_before_resource,
                    context = context,
                    test = command
                )
                context.tests.append(test)

        return self.contexts

    def run(self):
        [context.run() for context in self.contexts]

def build_and_run_flow(resource, code_before_resource = []):
    for command in resource.commands:
        flow = Flow(code_before_resource = code_before_resource)
        flow.build(command)
        flow.run()

mm = metamodel_from_file('grammar.tx')
model = mm.model_from_file('program.api')

if model.header_codes:
    code_before_resource = [header_code for header_code in model.header_codes if type(header_code) == unicode]
    resource = model.header_codes[len(code_before_resource)]
    build_and_run_flow(resource, code_before_resource)
else:
    build_and_run_flow(model.resource)

if __name__ == '__main__':
    unittest.main()
