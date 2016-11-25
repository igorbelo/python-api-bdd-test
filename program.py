from textx.metamodel import metamodel_from_file

def exec_code(body):
    exec("\n".join(body))

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
            for before in self.before:
                exec_code(before.body)

            test.run()

            for after in self.after:
                exec_code(after.body)

class Test:
    def __init__(self, context, test):
        self.context = context
        self.test = test

    def prepare(self):
        pass

    def run(self):
        self.prepare()
        exec_code(self.test.body)

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
