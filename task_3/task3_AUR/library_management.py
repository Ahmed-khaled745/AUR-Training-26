from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, timedelta


class ItemStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    LOST = "Lost"


class LibraryItem(ABC):
    """
    Abstract base class for all library items.

    ISBN validation:
    This implementation validates ISBN-13.
    """

    def __init__(self, title, status=ItemStatus.AVAILABLE):
        self._title = title
        self._status = status

    @property
    def title(self):
        return self._title

    @property
    def status(self):
        return self._status

    @abstractmethod
    def loan_period(self): 
        pass

    def checkout(self):
        if self._status != ItemStatus.AVAILABLE:
            raise ValueError( f"Cannot check out '{self._title}': item is {self._status.value}.")

        self._status = ItemStatus.CHECKED_OUT

    def return_item(self):
        if self._status != ItemStatus.CHECKED_OUT:
            raise ValueError(f"Cannot return '{self._title}': item is {self._status.value}.")
            
        self._status = ItemStatus.AVAILABLE

    def mark_lost(self):
        if self._status == ItemStatus.LOST:
            raise ValueError(f"'{self._title}' is already marked as lost.")
        self._status = ItemStatus.LOST

    def __lt__(self, other):
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return self._title.casefold() < other._title.casefold()

    def __str__(self):
        return f"{self._title} ({self.__class__.__name__}) - {self._status.value}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"title={self._title!r}, status={self._status.name})"
        )

    @staticmethod
    def is_valid_isbn(isbn):
        """
        Validate an ISBN-13 checksum.
        """
        if not isinstance(isbn, str):
            return False

        digits = isbn

        if len(digits) != 13 or not digits.isdigit():
            return False

        total = 0
        for i, digit in enumerate(digits):
            number = int(digit)
            total += number if i % 2 == 0 else number * 3

        return total % 10 == 0
        
    @classmethod
    def from_dict(cls, data):
        
        item_type = data.get("type")
        item_class = ITEM_TYPE_REGISTRY.get(item_type)

        if item_class is None:
            raise ValueError(f"Unknown library item type: {item_type!r}")

        if "title" not in data:
            raise ValueError("Each item must have a title.")

        item = item_class.from_dict(data)

        status_name = data.get("status", "AVAILABLE")
        try:
            item._status = ItemStatus[status_name]
        except KeyError:
            raise ValueError(f"Invalid item status: {status_name!r}")

        return item


class Book(LibraryItem):
    def __init__(self, title, author, isbn=None, status=ItemStatus.AVAILABLE):
        super().__init__(title, status)
        self._author = author
        self._isbn = isbn

        if isbn is not None and not self.is_valid_isbn(isbn):
            raise ValueError(f"Invalid ISBN-13: {isbn}")

    @property
    def author(self):
        return self._author

    @property
    def isbn(self):
        return self._isbn

    def loan_period(self):
        return 21

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            author=data.get("author", ""),
            isbn=data.get("isbn")
        )


class DVD(LibraryItem):
    def __init__(self, title, director, status=ItemStatus.AVAILABLE):
        super().__init__(title, status)
        self._director = director

    @property
    def director(self):
        return self._director

    def loan_period(self):
        return 5

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            director=data.get("director", "")
        )


class Magazine(LibraryItem):
    def __init__(self, title, issue, status=ItemStatus.AVAILABLE):
        super().__init__(title, status)
        self._issue = issue

    @property
    def issue(self):
        return self._issue

    def loan_period(self):
        return 14

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            issue=data.get("issue", "")
        )



# To add a new type, create the subclass and register it here.
ITEM_TYPE_REGISTRY = {
    "Book": Book,
    "DVD": DVD,
    "Magazine": Magazine,
}

class Database:
    """Responsible only for reading and writing database.txt."""

    def __init__(self, filename="database.txt"):
        self._filename = filename

    def load(self):
        items = []

        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        data = {}
                        for part in line.split("|"):
                            key, value = part.split("=", 1)
                            data[key] = value

                        items.append(LibraryItem.from_dict(data))

                    except (ValueError, KeyError) as error:
                        raise ValueError(
                            f"Invalid database entry on line {line_number}: {error}"
                        ) from error

        except FileNotFoundError:
            return 

        return items

    def save(self, items):
        with open(self._filename, "w", encoding="utf-8") as file:
            for item in items:
                data = self._item_to_dict(item)
                line = "|".join(f"{key}={value}" for key, value in data.items())
                file.write(line + "\n")

    @staticmethod
    def _item_to_dict(item):
        if isinstance(item, Book):
            return {
                "type": "Book",
                "title": item.title,
                "author": item.author,
                "isbn": item.isbn or "",
                "status": item.status.name,
            }

        if isinstance(item, DVD):
            return {
                "type": "DVD",
                "title": item.title,
                "director": item.director,
                "status": item.status.name,
            }

        if isinstance(item, Magazine):
            return {
                "type": "Magazine",
                "title": item.title,
                "issue": item.issue,
                "status": item.status.name,
            }

        raise TypeError(f"Unsupported library item: {type(item).__name__}")


class Library:
    """
    Manages items, members, and loans.
    It does not read/write files; Database handles persistence.
    """

    def __init__(self, items=None, database=None):
        self._items = list(items) if items else []
        self._database = database

    @property
    def items(self):
        return tuple(self._items)

    
    def add_item(self, item):
        if not isinstance(item, LibraryItem):
            raise TypeError("Only LibraryItem objects can be added.")
        self._items.append(item)

    def remove_item(self, title):
        item = self.find_by_title(title)

        if item is None:
            raise ValueError(f"Item '{title}' was not found.")

        if item.status == ItemStatus.CHECKED_OUT:
            raise ValueError("A checked-out item cannot be removed.")

        self._items.remove(item)
        return item

    def find_by_title(self, title):
        for item in self._items:
            if item.title.casefold() == title.casefold():
                return item
        return None

    def list_available(self):
        return sorted(
            item for item in self._items
            if item.status == ItemStatus.AVAILABLE
        )

    

    def checkout(self, title, member):
        item = self.find_by_title(title)
        if item is None:
            raise ValueError(f"Item '{title}' was not found.")
        item.checkout()

    def return_item(self, title):
        item = self.find_by_title(title)

        if item is None:
            raise ValueError(f"Item '{title}' was not found.")

        item.return_item()


    def mark_lost(self, title):
        item = self.find_by_title(title)

        if item is None:
            raise ValueError(f"Item '{title}' was not found.")

        item.mark_lost()

    def load_from_database(self):
        if self._database is None:
            raise ValueError("No Database object was provided.")

        self._items = self._database.load()

    def save_to_database(self):
        if self._database is None:
            raise ValueError("No Database object was provided.")

        self._database.save(self._items)


def main():
    database = Database("database.txt")
    library = Library(database=database)

    # Load the four records from database.txt.
    library.load_from_database()

    print("ALL ITEMS:")
    for item in sorted(library.items):
        print(item)

    print("\nAVAILABLE ITEMS:")
    for item in library.list_available():
        print(item)

    print("\nREPR:")
    for item in library.items:
        print(repr(item))

    print("\nLOAN PERIODS:")
    for item in library.items:
        print(f"{item.title}: {item.loan_period()} days")

    # trying ISBN-13 validation.
    print("\nISBN VALIDATION:")
    book = library.find_by_title("Dune")
    print(f"{book.isbn}: {LibraryItem.is_valid_isbn(book.isbn)}")

main()
