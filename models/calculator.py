class Calculator:
    number_stack = []

    def type_number(self, number):
        self.number_stack.append(number)

    def get_binary_operands(self):
        if len(self.number_stack) < 2:
            raise Exception("This operation requires at least 2 operands")

        return (
            self.number_stack.pop(-2),
            self.number_stack.pop(-1)
        )

    def exec_operation(self, operation):
        x, y = self.get_binary_operands()
        result = operation(x, y)
        self.number_stack.append(result)
        return result

    def add(self):
        def operation(x, y) : return x + y
        return self.exec_operation(operation)

    def subtract(self):
        def operation(x, y) : return x - y
        return self.exec_operation(operation)

    def divide(self):
        def operation(x, y) : return x / y
        return self.exec_operation(operation)

    def multiply(self):
        def operation(x, y) : return x * y
        return self.exec_operation(operation)
