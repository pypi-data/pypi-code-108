class RevoteError(Exception):
    """
    Wznoszone podczas próby zagłosowania na tą samą kategorię w inauguracji drugi raz.
    """

    def __init__(self, category: str):
        super().__init__("Próbowałeś zagłosować na kategorię '{}' drugi raz.".format(category))


class InvalidGalleryError(Exception):
    """
    Wznoszone podczas próby pobrania zdjęć z galerii będącej na liście niedziałających.
    """

    def __init__(self, gallery_id: int):
        super().__init__(
            "Galeria o ID {} jest usunięta/uszkodzona. "
            "Próba pobrania zdjęć prawdopodobnie zakończy się statusem 500 Internal Server Error.".format(gallery_id)
        )


class HTTPClientLookupError(Exception):
    """
    Wznoszone, gdy model nie posiada otartego HTTPClient-a do wykonania zapytania
    """

    def __init__(self):
        super().__init__(
            "Model nie znalazł żadnego otwartego HTTPClient-a. "
            "Jeśli nie podasz go w konstruktorze, musisz bezpośrednio w metodzie."
        )


class InactiveCastleError(Exception):
    """
    Wznoszone, podczas próby pobrania listy galerii z nieaktywnego zamku.
    """

    def __init__(self, name: str):
        super().__init__(
            "{} jest aktualnie nieaktywny i nie ma w nim żadnych galerii.".format(name)
        )
