import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial
from json import loads, dumps
from text import UndoText
from typing import List, Union, Dict, Tuple

APPNAME = "PyWord"
CONSTANTS = {"normalFontSize": 15, "smallFontSize": 10, "largeFontSize": 25}


class TextEditor:
    """
    Text editor application using Tkinter.
    """

    def __init__(self) -> None:
        """
        Initialize the TextEditor application.
        """
        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.title(APPNAME)
        self.root.configure(bg="white")
        self.file_path = "Untitled"
        self.initial_dir = "./DOCS/"
        self.valid_file_types = (("Rich Text File", "*.rte"),)
        self.font_name = "Bahnschrift"
        self.padding = 20

        self.text_area = UndoText(
            self.root, font=f"{self.font_name} {CONSTANTS["normalFontSize"]}", relief=tk.FLAT
        )
        self.text_area.pack(
            fill=tk.BOTH, expand=tk.TRUE, padx=self.padding, pady=self.padding
        )
        self.text_area.bind("<Key>", self.key_down)
        self.text_area.bind("<Control-z>", lambda _: self.text_area.undo())
        self.text_area.bind("<Control-y>", lambda _: self.text_area.redo())

        self.styles: Dict[str, Dict[str, Union[str, str]]] = {
            "Small": {"font": f"{self.font_name} {CONSTANTS['smallFontSize']}"},
            "Normal": {"font": f"{self.font_name} {CONSTANTS["normalFontSize"]}"},
            "Larger": {"font": f"{self.font_name} {CONSTANTS['largeFontSize']}"},
            "Small Bold": {"font": f"{self.font_name} {CONSTANTS['smallFontSize']} bold"},
            "Normal Bold": {"font": f"{self.font_name} {CONSTANTS["normalFontSize"]} bold"},
            "Larger Bold": {"font": f"{self.font_name} {CONSTANTS['largeFontSize']} bold"},
            "Small Italic": {"font": f"{self.font_name} {CONSTANTS['smallFontSize']} italic"},
            "Normal Italic": {"font": f"{self.font_name} {CONSTANTS["normalFontSize"]} italic"},
            "Larger Italic": {"font": f"{self.font_name} {CONSTANTS['largeFontSize']} italic"},
            "Code": {
                "font": f"Consolas {CONSTANTS['normalFontSize']}",
                "background": self.rgb2hex((200, 200, 200)),
            },
        }

        self.highlight: Dict[str, Dict[str, str]] = {
            "Highlight Red": {"background": self.rgb2hex((255, 0, 0))},
            "Highlight Green": {"background": self.rgb2hex((0, 255, 0))},
            "Highlight Black": {"background": self.rgb2hex((0, 0, 0))},
        }

        self.color: Dict[str, Dict[str, str]] = {
            "Text White": {"foreground": self.rgb2hex((255, 255, 255))},
            "Text Grey": {"foreground": self.rgb2hex((200, 200, 200))},
            "Text Blue": {"foreground": self.rgb2hex((0, 0, 255))},
            "Text Green": {"foreground": self.rgb2hex((0, 255, 0))},
            "Text Red": {"foreground": self.rgb2hex((255, 0, 0))},
            "Text Black": {"foreground": self.rgb2hex((0, 0, 0))},
        }

        self.reset_tags()
        self.setup_menu()

        self.root.mainloop()

    @staticmethod
    def rgb2hex(rgb: Tuple[int, int, int]) -> str:
        """
        Convert an RGB color tuple to a hexadecimal color code.

        Args:
            rgb (Tuple[int, int, int]): RGB color values.

        Returns:
            str: Hexadecimal color code.
        """
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def reset_tags(self) -> None:
        """
        Reset all text tags to their default values.
        """
        for tag in self.text_area.tag_names():
            self.text_area.tag_remove(tag, "1.0", "end")

        for tag_types in [self.styles, self.color, self.highlight]:
            for tag_type in tag_types:
                self.text_area.tag_configure(tag_type.lower(), **tag_types[tag_type])

    def get_tags(self, start, end) -> set:
        """
        Get the set of tags applied to a text range.

        Args:
            start: The start position of the text range.
            end: The end position of the text range.

        Returns:
            set: A set of tags applied to the text range.
        """
        index = start
        tags = []
        while self.text_area.compare(index, "<=", end):
            tags.extend(self.text_area.tag_names(index))
            index = self.text_area.index(f"{index}+1c")
        return set(tags)

    def key_down(self, event=None) -> None:
        """
        Event handler for key presses.
        Updates the window title.

        Args:
            event: The key event.
        """
        self.root.title(f"{APPNAME} - *{self.file_path}")

    def file_manager(self, action=None) -> None:
        """
        Manage file operations such as opening and saving.

        Args:
            action: The file operation to perform (e.g., "open" or "save").
        """
        if action == "open":
            file_path = filedialog.askopenfilename(
                filetypes=self.valid_file_types, initialdir=self.initial_dir
            )
            if file_path:
                self.load_document(file_path)
        elif action == "save":
            self.save_document()

    def load_document(self, file_path: str) -> None:
        """
        Load a document from a file.

        Args:
            file_path (str): The path to the document file.
        """
        try:
            with open(file_path, "r") as f:
                document = loads(f.read())
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", document["content"])
                self.reset_tags()
                for tag_name in document["tags"]:
                    for tag_start, tag_end in document["tags"][tag_name]:
                        self.text_area.tag_add(tag_name, tag_start, tag_end)
                self.file_path = file_path
                self.root.title(f"{APPNAME} - {self.file_path}")
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while opening the file: {str(e)}"
            )

    def save_document(self) -> None:
        """
        Save the document to a file.
        """
        document = {"content": self.text_area.get("1.0", tk.END), "tags": {}}
        for tag_name in self.text_area.tag_names():
            if tag_name == "sel":
                continue
            document["tags"][tag_name] = []
            ranges = self.text_area.tag_ranges(tag_name)
            for i in range(0, len(ranges), 2):
                document["tags"][tag_name].append([str(ranges[i]), str(ranges[i + 1])])

        file_path = filedialog.asksaveasfilename(
            filetypes=self.valid_file_types, initialdir=self.initial_dir
        )
        if file_path:
            if not file_path.endswith(".rte"):
                file_path += ".rte"
            try:
                with open(file_path, "w") as f:
                    f.write(dumps(document))
                self.file_path = file_path
                self.root.title(f"{APPNAME} - {self.file_path}")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while saving the file: {str(e)}"
                )

    def setup_menu(self) -> None:
        """
        Set up the application menu.
        """
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(
            label="Open",
            command=partial(self.file_manager, action="open"),
            accelerator="Ctrl+O",
        )
        self.root.bind_all("<Control-o>", self.open_file)

        file_menu.add_command(
            label="Save",
            command=partial(self.file_manager, action="save"),
            accelerator="Ctrl+S",
        )
        self.root.bind_all("<Control-s>", self.save_file)

        file_menu.add_command(label="Exit", command=self.root.quit)

        format_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Format", menu=format_menu)

        self.setup_submenu(format_menu, "style", self.styles)
        self.setup_submenu(format_menu, "highlight", self.highlight)
        self.setup_submenu(format_menu, "color", self.color)

    def open_file(self, event=None):
        self.file_manager("open")

    def save_file(self, event=None):
        self.file_manager("save")

    def setup_submenu(self, parent_menu, tag_type, tags) -> None:
        """
        Set up submenus for different tag types in the Format menu.

        Args:
            parent_menu: The parent menu to add the submenus to.
            tag_type: The type of tags (e.g., "style", "highlight", "color").
            tags: A dictionary of tag names and configurations.
        """
        submenu = tk.Menu(parent_menu, tearoff=0)
        parent_menu.add_cascade(label=tag_type.capitalize(), menu=submenu)
        for tag_name in tags:
            submenu.add_command(
                label=tag_name,
                command=partial(
                    self.tag_toggle, tag_name=tag_name.lower(), parent=tag_type
                ),
            )

    def tag_toggle(self, tag_name, parent) -> None:
        """
        Toggle the application of a tag to the selected text.

        Args:
            tag_name: The name of the tag to toggle.
            parent: The type of tags (e.g., "style", "highlight", "color").
        """
        try:
            start, end = "sel.first", "sel.last"
            x = tag_name.split(" ")
            if len(x) == 1:
                self.text_area.tag_remove("small", start, end)
                self.text_area._undo_stack.pop()
                self.text_area.tag_remove("normal", start, end)
                self.text_area._undo_stack.pop()
                self.text_area.tag_remove("larger", start, end)
                self.text_area._undo_stack.pop()
            else:
                if x[1] == "bold":
                    self.text_area.tag_remove("smaller bold", start, end)
                    self.text_area._undo_stack.pop()
                    self.text_area.tag_remove("normal bold", start, end)
                    self.text_area._undo_stack.pop()
                    self.text_area.tag_remove("larger bold", start, end)
                    self.text_area._undo_stack.pop()
                else:
                    self.text_area.tag_remove("smaller italic", start, end)
                    self.text_area._undo_stack.pop()
                    self.text_area.tag_remove("normal italic", start, end)
                    self.text_area._undo_stack.pop()
                    self.text_area.tag_remove("larger italic", start, end)
                    self.text_area._undo_stack.pop()
            if tag_name in self.text_area.tag_names("sel.first"):
                self.text_area.tag_remove(tag_name, start, end)
            else:
                self.text_area.tag_add(tag_name, start, end)
        except tk.TclError:
            pass


if __name__ == "__main__":
    TextEditor()
