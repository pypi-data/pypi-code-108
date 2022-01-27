from .models import Athlete, Sport


def create_demo_data():
    data = [
        Sport(
            name="Soccer",
            athletes=[
                Athlete(name="Ronaldo"),
                Athlete(name="Messi"),
                Athlete(name="Beckham"),
            ],
        ),
        Sport(
            name="Hockey",
            athletes=[
                Athlete(name="Gretzky"),
                Athlete(name="Crosby"),
                Athlete(name="Ovechkin"),
                Athlete(name="Sundin"),
                Athlete(name="Domi"),
            ],
        ),
    ]

    return data
