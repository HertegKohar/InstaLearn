from copy import deepcopy


class _W_Node:
    def __init__(self, value, next_):
        self._value = value
        self._next = next_

    def __str__(self):
        try:
            return "{}-->{}".format(self._value, self._next._value)
        except AttributeError:
            return "{}".format(self._value)


class Wheel:
    def __init__(self):
        self.__front = None
        self.__rear = None
        self.__current = None
        self.__prev = None
        self.__count = 0

    def __len__(self):
        return self.__count

    def __str__(self):
        current = self.__front
        s = ""
        while current:
            s += "{}-->".format(current._value)
            current = current._next

        return s

    def clear(self):
        self.__front = None
        self.__rear = None
        self.__count = 0
        self.__prev = None
        self.__current = None

    def is_empty(self):
        return not self.__front

    def __linear_search(self, key):
        value = None
        prev = None
        current = self.__front
        while current and current._value != key:
            prev = current
            current = current._next

        if current and current._value == key:
            value = key
        return value, prev, current

    def add(self, value):
        if not self.__front:
            self.__front = _W_Node(value, None)
            self.__rear = self.__front
            self.__current = self.__front
        else:
            self.__rear._next = _W_Node(value, None)
            self.__rear = self.__rear._next
        self.__count += 1

    def get_next(self):
        assert self.__front, "Can't get next of an empty wheel"
        if self.__current is self.__rear:
            self.__current = self.__front
            self.__prev = None
        else:
            self.__prev = self.__current
            self.__current = self.__current._next
        return self.__current._value

    def pop(self):
        assert self.__front, "Can't pop an empty wheel"
        value = self.__current._value
        if self.__front is self.__rear:
            self.__front = None
            self.__rear = None
            self.__current = None
        elif self.__current is self.__front:
            self.__front = self.__front._next
            self.__current = self.__front
            self.__prev = None
        elif self.__current is self.__rear:
            self.__prev._next = None
            self.__rear = self.__prev
            self.__current = self.__front
            self.__prev = None
        else:
            self.__current = self.__current._next
            self.__prev._next = self.__current
        self.__count -= 1
        return value

    def peek(self):
        assert self.__front, "Can't peek at an empty wheel"
        return self.__current._value

    def remove(self, key):
        assert self.__front, "Can't remove from an empty wheel"
        value, prev, current = self.__linear_search(key)
        if value == key:
            if current is self.__front:
                self.__front = self.__front._next
            elif current is self.__rear:
                if self.__current is self.__rear:
                    self.__current = self.__front
                    self.__prev = None
                self.__rear = prev
                self.__rear._next = None
            else:
                prev._next = current._next
                if self.__current is current:
                    self.__current = self.__current._next
                    if self.__prev:
                        self.__prev._next = self.__current
        if not self.__front:
            self.__rear = None
            self.__current = None
            self.__prev = None
        return value

    def find(self, key):
        assert self.__front, "Can't find in an empty wheel"
        value, _, _ = self.__linear_search(key)
        return value

    def __iter__(self):
        current = self.__front
        while current is not None:
            yield current._value
            current = current._next
