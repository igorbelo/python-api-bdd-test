from textx.metamodel import metamodel_from_file

class Context:
    def __init__(self, *args, **kwargs):
        self.description = kwargs['description']
        self.resource = kwargs['resource']
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

class Response:
    def __init__(self, *args, **kwargs):
        self.status_code = 200

def build_flow(command, resource, contexts = []):
    if type(command).__name__ == 'ContextCommand':
        context = Context(
            description = command.description,
            resource = resource
        )
        contexts.append(context)
        for body in command.body:
            build_flow(body, resource, contexts)
    else:
        if not contexts:
            context = Context(
                description = "MainContent",
                resource = resource
            )
        else:
            context = contexts[-1]

        if len(contexts) > 1:
            last_context = contexts[-2]

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
            context.tests.append(command)

    return contexts

def prepare_test_execution(test, context):
    response = Response()

def exec_code(body):
    exec("\n".join(body))

def exec_test(test, context):
    prepare_test_execution(test, context)
    exec_code(test.body)

def exec_context(context):
    for test in context.tests:
        for before in context.before:
            exec_code(before.body)

        exec_test(test, context)

        for after in context.after:
            exec_code(after.body)

def exec_flow(flow):
    for context in flow:
        exec_context(context)


mm = metamodel_from_file('grammar.tx')
model = mm.model_from_file('program.api')

for command in model.commands:
    flow = build_flow(command, model.resource)
    exec_flow(flow)
