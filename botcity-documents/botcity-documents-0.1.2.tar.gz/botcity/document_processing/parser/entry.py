from dataclasses import dataclass
from botcity.document_processing.geometry import Point


@dataclass
class Entry:
    """Parser Entry.

    Attributes:
        index: The entry index.
        text: The entry content.
        page: The entry page number.
        p1: Coordinates for entry on the top-left corner.
        p2: Coordinates for the entry on the top-right corner.
        p3: Coordinates for the entry on the bottom-right corner.
        p4: Coordinates for the entry on the bottom-left corner.
    """
    index: int = 0
    text: str = ""
    page: int = 1
    p1: Point = Point()
    p2: Point = Point()
    p3: Point = Point()
    p4: Point = Point()

    @property
    def width(self) -> int:
        """Entry width.
        """
        x = [p.x for p in [self.p1, self.p2, self.p3, self.p4]]
        return max(x) - min(x)

    @property
    def height(self) -> int:
        """Entry height.
        """
        y = [p.y for p in [self.p1, self.p2, self.p3, self.p4]]
        return max(y) - min(y)

    def __repr__(self) -> str:
        points = ",".join([f"({p.x:.0f},{p.y:.0f})" for p in [self.p1, self.p2, self.p3, self.p4]])
        return f"{self.text}: {points}"
