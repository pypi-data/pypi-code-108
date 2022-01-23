from django.forms import NumberInput


class CounterWidget(NumberInput):
    template_name = "counter_widgets/counter.html"
    counter_class = "counter"
    decrement_class = "decrement"
    increment_class = "increment"

    def __init__(self, attrs=None, delta=1, increment_value=None, decrement_value=None, increment_text="+", decrement_text="-"):
        super().__init__(attrs)
        self.delta = delta
        self.increment_value = increment_value if increment_value else self.delta
        self.decrement_value = decrement_value if decrement_value else self.delta
        self.increment_text = increment_text
        self.decrement_text = decrement_text

    def get_context(self, name, value, attrs):
        return {
            **super().get_context(name, value, attrs),
            "increment_value": self.increment_value,
            "decrement_value": self.decrement_value,
            "increment_text": self.increment_text,
            "decrement_text": self.decrement_text,
            "counter_class": self.counter_class,
            "decrement_class": self.decrement_class,
            "increment_class": self.increment_class,
        }
