import io
import pickle


class Book:
    title = ""
    isbn = ""
    parts = None
    chapters = None

    def __init__(self, title, isbn, parts, chapters):
        self.title = title
        self.isbn = isbn
        self.parts = parts
        self.chapters = chapters

    def identify(self):
        print("Title of the book: %s" % (self.title))
        print("ISBN of the book: %s" % (self.isbn))
        print("Parts are:")
        for part in self.parts:
            print(part)
        print("Chapters are:%s" % (self.chapters))


class Part:
    partName = ""
    beginChapter = -1
    endChapter = -1

    def __init__(self, partName, beginChapter, endChapter):
        self.partName = partName
        self.beginChapter = beginChapter
        self.endChapter = endChapter

    def __str__(self):
        stringRep = "%s" % (self.partName)
        return stringRep


part1 = Part("Part 1", 1, 3)
part2 = Part("Part 2", 4, 5)
part3 = Part("Part 3", 6, 7)
bookTitle = "Book yet to be written"
bookISBN = "XXX-X-XX-XXXXXX-X"
bookParts = [part1, part2, part3]
bookChapters = [
    "Chapter 1",
    "Chapter 2",
    "Chapter 3",
    "Chapter 4",
    "Chapter 5",
    "Chapter 6",
    "Chapter 7",
]
book = Book(bookTitle, bookISBN, bookParts, bookChapters)
pickleBuffer = io.BytesIO()
print("Pickling of the object into the memory buffer started")
pickle.dump(book, pickleBuffer)
print("Pickling of the object into the memory buffer ended")
print("Pickled buffer beginning address:")
print(pickleBuffer.getbuffer())
print("Unpickling of the object from memory started")
unpickledBook = pickle.loads(pickleBuffer.getbuffer())
print("Unpickling of the object from memory ended")
print("Printing the attributes of unpickled object")
unpickledBook.identify()
