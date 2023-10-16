import tkinter as tk, _tkinter
from tkinter import font
import ctypes
from json import loads, dumps
from tkinter.filedialog import askopenfilename, asksaveasfilename
from functools import partial

ctypes.windll.shcore.SetProcessDpiAwareness(True)

APPNAME = "PyWord"


class TextEditor:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title(APPNAME)

        self.filePath = "Untitled"
        self.initialdir = "./DOCS/"
        self.validFileTypes = (("Rich Text File", "*.rte"),)
        self.fontName = "Bahnschrift"
        self.padding = 20
        self.document = None
        self.defaultContent = {
            "content": "",
            "tags": {"bold": [(), ()]},
        }

        self.styles = {
            "Bold": {"font": f"{self.fontName} 15 bold"},
            "Italic": {"font": f"{self.fontName} 15 italic"},
            "Code": {
                "font": "Consolas 15",
                "background": self.rgb2hex((200, 200, 200)),
            },
        }

        self.size = {
            "Smallest Size": {"font": f"{self.fontName} 8"},
            "Smaller Size": {"font": f"{self.fontName} 10"},
            "Normal Size": {"font": f"{self.fontName} 15"},
            "Larger Size": {"font": f"{self.fontName} 25"},
            "Largest Size": {"font": f"{self.fontName} 35"},
        }

        self.highlight = {
            "Highlight Red": {"background": self.rgb2hex((255, 0, 0))},
            "Highlight Green": {"background": self.rgb2hex((0, 255, 0))},
            "Highlight Black": {"background": self.rgb2hex((0, 0, 0))},
        }

        self.color = {
            "Text White": {"foreground": self.rgb2hex((255, 255, 255))},
            "Text Grey": {"foreground": self.rgb2hex((200, 200, 200))},
            "Text Blue": {"foreground": self.rgb2hex((0, 0, 255))},
            "Text green": {"foreground": self.rgb2hex((0, 255, 0))},
            "Text Red": {"foreground": self.rgb2hex((255, 0, 0))},
            "Text Black": {"foreground": self.rgb2hex((0, 0, 0))},
        }

        self.textArea = tk.Text(
            self.root,
            font=f"{self.fontName} 15",
            relief=tk.FLAT,
            undo=True,
            maxundo=-1,
            autoseparators=True,
        )
        self.textArea.pack(
            fill=tk.BOTH, expand=tk.TRUE, padx=self.padding, pady=self.padding
        )
        self.textArea.bind("<Key>", self.keyDown)

        self.resetTags()

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.fileMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.fileMenu)

        self.fileMenu.add_command(
            label="Open",
            command=partial(self.fileManager, action="open"),
            accelerator="Ctrl+O",
        )
        self.root.bind_all("<Control-o>", partial(self.fileManager, action="open"))

        self.fileMenu.add_command(
            label="Save",
            command=partial(self.fileManager, action="save"),
            accelerator="Ctrl+S",
        )
        self.root.bind_all("<Control-s>", partial(self.fileManager, action="save"))

        self.fileMenu.add_command(label="Exit", command=self.root.quit)

        styleMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Format", menu=styleMenu)

        for tagType in self.styles:
            styleMenu.add_command(
                label=tagType,
                command=partial(
                    self.tagToggle, tagName=tagType.lower(), parent="style"
                ),
            )

        sizeMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Size", menu=sizeMenu)
        for tagType in self.size:
            sizeMenu.add_command(
                label=tagType,
                command=partial(self.tagToggle, tagName=tagType.lower(), parent="size"),
            )

        highlightMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Highlight", menu=highlightMenu)
        for tagType in self.highlight:
            highlightMenu.add_command(
                label=tagType,
                command=partial(
                    self.tagToggle, tagName=tagType.lower(), parent="highlight"
                ),
            )

        colorMenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Color", menu=colorMenu)
        for tagType in self.color:
            colorMenu.add_command(
                label=tagType,
                command=partial(
                    self.tagToggle, tagName=tagType.lower(), parent="color"
                ),
            )

        self.root.mainloop()

    @staticmethod
    def rgb2hex(rgb: tuple[int, int, int]):
        r, g, b = rgb
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def resetTags(self):
        for tag in self.textArea.tag_names():
            print(tag)
            self.textArea.tag_remove(tag, "1.0", "end")

        for tagTypes in [self.styles, self.color, self.highlight, self.size]:
            for tagType in tagTypes:
                self.textArea.tag_configure(tagType.lower(), tagTypes[tagType])

    def tagToggle(self, tagName, parent):
        try:
            start, end = "sel.first", "sel.last"
            print(self.textArea.tag_names("sel.first"))
            if tagName in self.textArea.tag_names("sel.first"):
                self.textArea.tag_remove(tagName, start, end)
            else:
                self.textArea.tag_add(tagName, start, end)
        except _tkinter.TclError:
            pass

    def keyDown(self, event=None):
        self.root.title(f"{APPNAME} - *{self.filePath}")

    def fileManager(self, event=None, action=None):
        filePath = self.filePath
        if action == "open":
            filePath = askopenfilename(
                filetypes=self.validFileTypes, initialdir=self.initialdir
            )
            with open(filePath, "r") as f:
                document = loads(f.read())
            self.textArea.delete("1.0", tk.END)
            self.textArea.insert("1.0", document["content"])
            self.root.title(f"{APPNAME} - {filePath}")
            self.resetTags()
            for tagName in document["tags"]:
                for tagStart, tagEnd in document["tags"][tagName]:
                    self.textArea.tag_add(tagName, tagStart, tagEnd)
        elif action == "save":
            document = self.defaultContent
            document["content"] = self.textArea.get("1.0", tk.END)
            for tagName in self.textArea.tag_names():
                if tagName == "sel":
                    continue

                document["tags"][tagName] = []
                ranges = self.textArea.tag_ranges(tagName)
                for i, tagRange in enumerate(ranges[::2]):
                    document["tags"][tagName].append(
                        [str(tagRange), str(ranges[i + 1])]
                    )

                if filePath == "Untitled":
                    newfilePath = asksaveasfilename(
                        filetypes=self.validFileTypes, initialdir=self.initialdir
                    )
                if newfilePath is None:
                    return
                filePath = newfilePath
                if not filePath.endswith(".rte"):
                    filePath += ".rte"
                with open(filePath, "w") as f:
                    print("Saving at: ", filePath)
                    f.write(dumps(document))
                self.root.title(f"{APPNAME} - {filePath}")


if __name__ == "__main__":
    TextEditor()
