import tkinter as tk
import pyperclip
from typing import List, Tuple, Union
from custom_stack import Stack


class UndoText(tk.Text):
    """
    A text widget with undo and redo functionality.
    """

    def __init__(self, *args: List[Union[str, int]], **kwargs: dict) -> None:
        """
        Initialize the UndoText widget.

        Args:
            *args: Positional arguments to pass to the parent class.
            **kwargs: Keyword arguments to pass to the parent class.
        """
        super().__init__(*args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind("<<Paste>>", self.paste)
        self._undo_stack: List[Tuple[Tuple, Tuple]] = []
        self._redo_stack: List[Tuple[Tuple, Tuple]] = []

    def _proxy(self, *args: List[Union[str, int]]) -> str:
        """
        Intercept and handle Text widget commands.
        Args:
            *args: Additional arguments for the command.
        Returns:
            The result of the original Text widget command.
        """
        try:
            if args[0] in ["insert", "delete"]:
                self._handle_edit_command(args)
            elif args[0] == "tag":
                self._handle_tag_command(args)
            result = self.tk.call((self._orig,) + args)
            return result
        except tk.TclError:
            pass

    def _handle_edit_command(self, args: List[Union[str, int]]) -> None:
        """
        Handle insert and delete commands for undo and redo.
        Args:
            args: Arguments for the command.
        """
        if args[1] == "end":
            index = self.index("end-1c")
        else:
            index = self.index(args[1])
        if args[0] == "insert":
            undo_args = ("delete", index, "{}+{}c".format(index, len(args[2])))
        else:
            undo_args = ("insert", index, self.get(*args[:1]))
        self._clear_redo_stack()
        self._undo_stack.append((undo_args, args))

    def _handle_tag_command(self, args: List[Union[str, int]]) -> None:
        """
        Handle tag add and remove commands for undo and redo.
        Args:
            args: Arguments for the command.
        """
        if args[1] in ["add", "remove"] and args[2] != "sel":
            indexes = tuple(self.index(ind) for ind in args[3:])
            undo_args = (
                "tag",
                "remove" if args[1] == "add" else "add",
                args[2],
            ) + indexes
            self._clear_redo_stack()
            self._undo_stack.append((undo_args, args))

    def _clear_redo_stack(self) -> None:
        """
        Clear the redo stack to prevent redoing after making new changes.
        """
        self._redo_stack.clear()

    def paste(self, event: tk.Event) -> None:
        """
        Handle paste event with special functionality.

        Args:
            event: The paste event.
        """
        tag_ranges = self.tag_ranges("sel")
        if tag_ranges:
            selection_start = self.index(tk.SEL_FIRST)
            selection_end = self.index(tk.SEL_LAST)
            self.delete(selection_start, selection_end)
            self.mark_set(tk.INSERT, selection_start)
        self.insert(tk.INSERT, pyperclip.paste())
        self.see(tk.INSERT)
        return "break"

    def undo(self) -> None:
        """
        Undo the last text edit operation.
        """
        if not self._undo_stack:
            return
        undo_args, redo_args = self._undo_stack.pop()
        self._redo_stack.append((undo_args, redo_args))
        self.tk.call((self._orig,) + undo_args)

    def redo(self) -> None:
        """
        Redo the last undone text edit operation.
        """
        if not self._redo_stack:
            return
        undo_args, redo_args = self._redo_stack.pop()
        if redo_args[0] == "tag":
            if redo_args[1] == "add":
                self.tag_add(redo_args[2], undo_args[3], undo_args[4])
            else:
                self.tag_remove(redo_args[2], redo_args[3], redo_args[4])
            self._undo_stack.append((undo_args, redo_args))
        else:
            self._undo_stack.append((undo_args, redo_args))
            try:
                self.tk.call((self._orig,) + redo_args)
            except tk.TclError:
                pass

    def dump_tags(self) -> List[Tuple[str, str, str]]:
        """
        Serialize the tags and their associated text ranges.
        Returns:
            A list of tag information (tag name, start index, end index).
        """
        tag_info: List[Tuple[str, str, str]] = []
        for tag in self.tag_names():
            if tag != "sel":
                indices = self.tag_ranges(tag)
                for i in range(0, len(indices), 2):
                    tag_info.append((tag, indices[i], indices[i + 1]))
        return tag_info

    def load_tags(self, tags: List[Tuple[str, str, str]]) -> None:
        """
        Load tags from serialized tag information.
        Args:
            tags: A list of tag information (tag name, start index, end index).
        """
        self.tag_remove("sel", "1.0", "end")
        for tag, start, end in tags:
            self.tag_add(tag, start, end)
