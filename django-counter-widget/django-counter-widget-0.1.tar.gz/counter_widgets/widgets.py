from django.forms import NumberInput


class CounterWidget(NumberInput):
    template_name = "counter_widgets/counter.html"
    delta = 1
    increment_value = None
    decrement_value = None
    increment_text = "+"
    decrement_text = "-"
    counter_class = "counter"
    decrement_class = "decrement"
    increment_class = "increment"

    def get_context(self, name, value, attrs):
        return {
            **super().get_context(name, value, attrs),
            "increment_value": self.increment_value if self.increment_value else self.delta,
            "decrement_value": self.decrement_value if self.decrement_value else self.delta,
            "increment_text": self.increment_text,
            "decrement_text": self.decrement_text,
            "counter_class": self.counter_class,
            "decrement_class": self.decrement_class,
            "increment_class": self.increment_class,
        }
