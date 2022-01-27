import math
import re


class ArrangeCalculator:
    size: int
    max_depth: int
    max_depth_length: int
    child_suffix: str

    def __init__(self, size: int = 3, length: int = 19):
        max_depth = math.floor(length / 3) - 1
        max_depth_length = max_depth * 3
        child_suffix = ''.ljust(max_depth_length, '0')

        self.size = size
        self.length = length
        self.max_depth = max_depth
        self.max_depth_length = max_depth_length
        self.child_suffix = child_suffix

    def item(self, arrange: int):
        return ArrangeItemCalculator(self, arrange)

    def after_item(self, arrange: int):
        return ArrangeItemCalculator(self, self.item(arrange).after)

    def reviser(self, arrange: int):
        return ArrangeReviser(self, arrange)


class ArrangeItemCalculator:
    calculator: ArrangeCalculator
    arrange: int
    root_order: str
    depth: int
    child_depth: int

    _child_order_mount: int
    _first_child: int
    _last_child: int
    _sibling_order_amount: int

    @property
    def child_order_amount(self):
        if hasattr(self, '_child_order_amount'):
            return self._child_order_amount

        calculator = self.calculator
        depth = self.depth

        child_order_amount = int(
            '1' + ''.ljust(
                calculator.size * (calculator.max_depth - depth - 1),
                '0'
            )
        )

        self._child_order_mount = child_order_amount
        return child_order_amount

    @property
    def first_child(self):
        if hasattr(self, '_first_child'):
            return self._first_child

        first_child = self.arrange + self.child_order_amount
        self._first_child = first_child

        return first_child

    @property
    def last_child(self):
        if hasattr(self, '_last_child'):
            return self._last_child

        last_child = self.after - self.child_order_amount
        self._last_child = last_child

        return last_child

    @property
    def sibling_order_amount(self):
        if hasattr(self, '_sibling_order_amount'):
            return self._sibling_order_amount

        sibling_order_amount = int(
            str(self.child_order_amount) + ''.rjust(self.calculator.size, '0')
        )

        self._sibling_order_amount = sibling_order_amount
        return sibling_order_amount

    @property
    def after(self):
        return self.arrange + self.sibling_order_amount

    def __init__(self, calculator: ArrangeCalculator, arrange: int):

        if arrange is None:
            print("Arrange is None!!!!!!!!!!!!!!")
            arrange = 0

        string_arrange = str(arrange)
        root_order = string_arrange[0:len(string_arrange) - calculator.max_depth_length]

        depth = math.ceil(
            len(re.sub('0+$', '', string_arrange[len(root_order):]))
            / calculator.size
        )

        self.calculator = calculator
        self.arrange = arrange
        self.root_order = root_order
        self.depth = depth
        self.child_depth = depth + 1


class ArrangeReviser:
    calculator: ArrangeCalculator
    arrange: int

    def __init__(self, calculator: ArrangeCalculator, arrange: int):
        self.calculator = calculator
        self.arrange = arrange
