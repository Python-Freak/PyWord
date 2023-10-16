class Action:
    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end
        self.isDefault = True

class ColorChange(Action):
    def __init__(self, start, end, prevColor, newColor) -> None:
        super().__init__(start, end)
        self.isDefault = False
        self.previousColor = prevColor
        self.newColor = newColor

class StyleChange(Action):
    def __init__(self, start, end, prevStyle, newStyle) -> None:
        super().__init__(start, end)
        self.isDefault = False
        self.prevStyle = prevStyle
        self.newStyle = newStyle

