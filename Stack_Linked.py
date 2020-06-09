class _Stack_Node:
	def __init__(self,value,next_):
		self._value=value
		self._next=next_

class Stack:
	def __init__(self):
		self._top=None

	def is_empty(self):
		return self._top is None

	def peek(self):
		assert self._top is not None, "Can't Peek at an Empty Stack"
		return self._top._value

	def pop(self):
		assert self._top is not None, "Can't pop an empty stack"
		value=self._top._value
		self._top=self._top._next
		return value

	def push(self,value):
		self._top=_Stack_Node(value,self._top)

	def __iter__(self):
		current=self._top
		while current is not None:
			yield current._value
			current=current._next



