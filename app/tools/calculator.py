from langchain.tools import tool
import operator
import ast

@tool
def calculator(expression: str):
    """Calculate a mathematical expression."""

    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def calculate(node):

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            left = calculate(node.left)
            right = calculate(node.right)

            operation = operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator")

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            value = calculate(node.operand)

            operation = operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator")

            return operation(value)

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")

    return calculate(tree.body)