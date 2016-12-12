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
        exec"\n".join(code_before_resource) in globals(), locals()

    exec "\n".join(body) in globals(), locals()

class Context:
    parent = None

    def __init__(self, *args, **kwargs):
        self.description = kwargs['description']
        if 'parent' in kwargs:
            self.parent = kwargs['parent']
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
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent

        for i in range(level): print "   ",
        print self.description

        for test in self.tests:
            for i in range(level+1): print "   ",
            print test.test.description
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
            befores = []
            for before in before_callbacks:
                befores.append(before.body)

            code = befores + [body]
            all_code = [item for sublist in code for item in sublist]

            exec_code(all_code,
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

    def build(self, command, parent_context=None):
        if type(command).__name__ == 'ContextCommand':
            context = Context(
                description = command.description,
                parent = parent_context
            )
            self.contexts.append(context)
            for body in command.body:
                self.build(body, context)
        else:
            if not self.contexts:
                context = Context(
                    description = "MainContext"
                )
            else:
                context = self.contexts[-1]

            parent = context.parent
            while parent:
                if parent.before:
                    for before in parent.before:
                        context.before.insert(0, before)

                if parent.after:
                    for after in parent.after:
                        context.after.insert(0, after)

                parent = parent.parent

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
