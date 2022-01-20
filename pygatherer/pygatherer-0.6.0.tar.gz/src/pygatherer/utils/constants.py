from pathurl import URL

BASE_URL = URL("https://gatherer.wizards.com/")
CARD_URL = BASE_URL.join("Pages/Card/")
CARD_DETAILS_URL = CARD_URL.join("Details.aspx")


SUPERTYPES = {"Basic", "Legendary", "Ongoing", "Snow", "World"}
