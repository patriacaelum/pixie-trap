class Point:
    def __init__(self, x=0, y=0):
        self.Set(x, y)

    def Set(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.Set(x, y, w, h)

    def Contains(self, point):
        """Returns `True` if the point is inside the rectangle, otherwise `False`."""
        x_in = self.x <= point.x <= self.x + self.w
        y_in = self.y <= point.y <= self.y + self.h

        return x_in and y_in

    def Set(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def center(self):
        """The center point of the rectangle."""
        return self.centre

    @property
    def centre(self):
        """The centre point of the rectangle."""
        return Point(self.x + self.w / 2, self.y + self.h / 2)
