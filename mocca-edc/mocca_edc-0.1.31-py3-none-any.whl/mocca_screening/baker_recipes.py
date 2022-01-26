from faker import Faker
from model_bakery.recipe import Recipe

from .models import MoccaRegisterContact

fake = Faker()

moccaregistercontact = Recipe(
    MoccaRegisterContact,
)
