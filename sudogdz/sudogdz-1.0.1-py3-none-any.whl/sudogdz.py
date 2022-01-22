"""
Parser of everything from the Russian reshebnik GDZ.RU
"""


__version__ = "1.0.1"


import bs4
import requests


def getRandomUserAgent():
    import random

    list = [
        {
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        },
        {
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        },
        {
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        },
        {
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        },
        {
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        },
    ]

    UACount = len(list) - 1
    return list[random.randint(0, UACount)]


def getSchoolItems():
    """
    ### Allows you to get avaliable school subjects

    Subject name parsed from GDZ site, so run command and find your subject
    """
    # List
    schoolItemsList = []

    # UA
    useragent = getRandomUserAgent()

    getGdzPage = requests.get(
        "https://gdz.ru/", headers={"User-Agent": useragent["useragent"]}
    ).text
    wrappedPage = bs4.BeautifulSoup(getGdzPage, "html.parser")

    for schoolitem in wrappedPage.find_all(
        "td", attrs={"class": "table-section-heading"}
    ):
        ejectedUrl = schoolitem.find("a").get("href")
        schoolItemsList.append(str(ejectedUrl).replace("/", ""))

    try:
        schoolItemsList.pop(0)
    except IndexError:
        raise requests.ConnectionError

    return schoolItemsList


def getBooks(type, **args):
    """
    ### Allows you to get avaliable books

    Filter:
    * `popularBooks` - search popular books
    * `books` - search book (need `schoolclass` and `schoolitem` argument)
    * `booksByClass` - search book by class (need only `schoolclass` argument)
    * `booksBySchoolItem` - search book by school item (need only `schoolitem` argument)
    """
    # Lists
    bookList = []
    ErrorList = ["school item is null", "number is greater than 11 or null"]

    # UA
    useragent = getRandomUserAgent()

    if type == "books":
        if int(args.get("schoolclass")) <= 11:
            if "schoolitem" in args:
                getGdzPage = requests.get(
                    f'https://gdz.ru/class-{args["schoolclass"]}/{args["schoolitem"]}',
                    headers={"User-Agent": useragent["useragent"]},
                ).text
            else:
                raise ValueError(ErrorList[0])
        else:
            raise ValueError(ErrorList[1])
    elif type == "booksByClass":
        if "schoolclass" in args and int(args.get("schoolclass")) <= 11:
            getGdzPage = requests.get(
                f'https://gdz.ru/class-{args["schoolclass"]}',
                headers={"User-Agent": useragent["useragent"]},
            ).text
        else:
            raise ValueError(ErrorList[1])
    elif type == "booksBySchoolItem":
        if "schoolitem" in args:
            getGdzPage = requests.get(
                f'https://gdz.ru/{args["schoolitem"]}',
                headers={"User-Agent": useragent["useragent"]},
            ).text
        else:
            raise ValueError(ErrorList[0])
    elif type == "popularBooks":
        getGdzPage = requests.get(
            f"https://gdz.ru", headers={"User-Agent": useragent["useragent"]}
        ).text
    else:
        return []
    wrappedPage = bs4.BeautifulSoup(getGdzPage, "html.parser")
    for ul in wrappedPage.find_all(attrs={"class": "book-list"}):
        for li in ul.find_all("a", attrs={"class": ["book", "book-regular"]}):
            bookList.append(
                {
                    "id": str(li["href"].split("/")[3]),
                    "url": {
                        "with_domain": f"https://gdz.ru{li['href']}",
                        "without_domain": li["href"],
                    },
                    "name": str(li["title"]).replace("ГДЗ ", "").strip(),
                    "authors": str(
                        li.find("span", attrs={"itemprop": "author"}).string
                    ).split(","),
                    "class": str(
                        "".join(filter(str.isdigit, str(li["href"].split("/")[1])))
                    ),
                    "pubhouse": str(
                        li.find("span", attrs={"itemprop": "publisher"}).string
                    ).strip(),
                    "cover": "https:"
                    + li.find("div", attrs={"class": "book-cover"}).select(
                        "noscript>img"
                    )[0]["src"],
                }
            )
    return bookList


def getTasksForBook(url):
    """
    ### Allows you to get avaliable tasks for book

    #### Info!
    You can insert full (https://gdz.ru/class-8...) or incomplete url (/class-8/...)
    """
    # UA
    useragent = getRandomUserAgent()

    if str(url).startswith("https://gdz.ru") or str(url).startswith("http://gdz.ru"):
        getGdzPage = requests.get(
            url, headers={"User-Agent": useragent["useragent"]}
        ).text
    else:
        getGdzPage = requests.get(
            f"https://gdz.ru{url}", headers={"User-Agent": useragent["useragent"]}
        ).text

    wrappedPage = bs4.BeautifulSoup(getGdzPage, "html.parser")

    tasksArray = []

    for taskItem in wrappedPage.find_all(
        "a", attrs={"class": "task-button js-task-button"}
    ):
        try:
            categoryName = str(
                taskItem.parent.parent.find("h2", {"class": "heading"}).text
            ).strip()
        except AttributeError:
            categoryName = str(
                taskItem.parent.parent.find("h3", {"class": "heading"}).text
            ).strip()
        tasksArray.append(
            {
                "num": str(taskItem.text).strip(),
                "category": categoryName,
                "url": {
                    "with_domain": f"https://gdz.ru{taskItem['href']}",
                    "without_domain": taskItem["href"],
                },
            }
        )

    return tasksArray


def getAnswerForBook(url):
    """
    ### Allows you to get answers for book

    #### Info!
    You can insert full (https://gdz.ru/class-8...) or incomplete url (/class-8/...)
    """

    useragent = getRandomUserAgent()

    if str(url).startswith("https://gdz.ru") or str(url).startswith("http://gdz.ru"):
        getGdzPage = requests.get(
            url, headers={"User-Agent": useragent["useragent"]}
        ).text
    else:
        getGdzPage = requests.get(
            f"https://gdz.ru{url}", headers={"User-Agent": useragent["useragent"]}
        ).text

    wrappedPage = bs4.BeautifulSoup(getGdzPage, "html.parser")

    answerArray = []

    for index, answerItem in enumerate(
        wrappedPage.find_all("div", attrs={"class": "task-img-container"})
    ):
        answerArray.append(
            {
                "id": index,
                "title": str(
                    answerItem.find("div", attrs={"class": "with-overtask"}).select(
                        "img"
                    )[0]["alt"]
                ).strip(),
                "png": str(
                    "https:"
                    + answerItem.find("div", attrs={"class": "with-overtask"}).select(
                        "img"
                    )[0]["src"]
                ).strip(),
            }
        )

    return answerArray
