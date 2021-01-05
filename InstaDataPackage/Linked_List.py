from copy import deepcopy


class _L_Node:
    def __init__(self, value, _next):
        self._value = value
        self._next = _next

    def __str__(self) -> str:
        return f"{self._value}-->"


class Linked_List:
    def __init__(self):
        self.__front = None
        self.__rear = None
        self.__count = 0

    def __len__(self) -> int:
        return self.__count

    def __str__(self) -> str:
        current = self.__front
        s = ""
        while current:
            s += str(current)
            current = current._next
        return s

    def __getitem__(self, i: int):
        assert self.__valid_index(i), "Invalid index"

        j = 0
        if i < 0:
            i += self.__count
        current = self.__front
        while j < i:
            current = current._next
            j += 1
        return current._value

    def __setitem__(self, i: int, value):
        assert self.__valid_index(i), "Invalid Index"
        if i < 0:
            i += self.__count
        j = 0
        current = self.__front
        while j < i:
            current = current._next
            j += 1
        current._value = value

    def __contains__(self, key):
        _, _, index = self.__linear_search(key)
        return index > -1

    def __linear_search(self, key):
        prev = None
        current = self.__front
        index = 0
        while current and current._value != key:
            prev = current
            current = current._next
            index += 1
        if not current:
            index = -1
        return current, prev, index

    def __valid_index(self, index: int):
        return -self.__count <= index < self.__count

    def clear(self) -> None:
        self.__front = None
        self.__rear = None
        self.__count = None

    def is_empty(self) -> bool:
        return self.__count == 0

    def prepend(self, value) -> None:
        if not self.__front:
            self.__front = _L_Node(value, None)
            self.__rear = self.__front
        else:
            self.__front = _L_Node(value, self.__front)
        self.__count += 1

    def append(self, value) -> None:
        if not self.__rear:
            self.__front = _L_Node(value, None)
            self.__rear = self.__front
        else:
            self.__rear._next = _L_Node(value, None)
            self.__rear = self.__rear._next
        self.__count += 1

    def __iter__(self):
        current = self.__front
        while current:
            yield current._value
            current = current._next

