from typing import Any


class Stack(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = len(self)

    def push(self, __object: Any) -> None:
        try:
            ans = super().append(__object)
            self.size += 1
            return ans
        except Exception as e:
            raise e

    def append(self, __object: Any) -> None:
        return self.push(__object)

    def pop(self):
        try:
            ans = super().pop()
            self.size -= 1
            return ans
        except Exception as e:
            raise e

    def __getitem__(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self) -> None:
        return super().clear()

    @property
    def is_empty(self):
        return self.size == 0


if __name__ == "__main__":
    q = Stack()
    print("q.is_empty : ", q.is_empty)
    q.push("Hello")
    q.clear()
    print("q.is_empty : ", q.is_empty)
    print(q)
    print(q.pop())
    print("q.is_empty : ", q.is_empty)
