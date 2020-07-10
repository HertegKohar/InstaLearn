from copy import deepcopy
class W_Node:
	def __init__(self,value,next_):
		self._next=next_
		self._value=value

class Wheel:
	def __init__(self):
		self._front=None
		self._rear=None
		self._current=None
		self._count=0

	def is_empty(self):
		return self._count==0

	def clear(self):
		self._front=None
		self._rear=None
		self._current=None
		self._count=0
		self._prev=None
	
	def _check_reset(self):
		if self._count==0:
			self._front=None
			self._rear=None
			self._current=None
			self._prev=None


	def __len__(self):
		return self._count

	def add(self,value):
		if self._front is None:
			self._front=W_Node(value,None)
			self._rear=self._front
			self._prev=None
			self._current=self._front
		else:
			self._rear._next=W_Node(value,self._front)
			self._rear=self._rear._next
		self._count+=1

	def peek(self):
		assert self._front, "Can't peek at an empty wheel"
		return self._current._value

	def pop(self):
		assert self._front, "Can't pop an empty wheel"
		if self._prev is None:
			value=self._front._value
			self._front=self._front._next
			self._current=self._front
		else:
			value=self._current._value
			if self._current is self._front:
				self._front=self._front._next
			elif self._current is self._rear:
				self._rear=self._prev
			self._current=self._current._next
			self._prev._next=self._current
		self._count-=1
		self._check_reset()
		return value

	def get_next(self):
		assert self._front, "Can't get the next of an empty wheel"
		self._prev=self._current
		self._current=self._current._next
		return self._current._value

	def remove(self,key):
		assert self._front, "Can't remove from an empty wheel"
		value=None
		if self._front._value==key and self._front is self._rear:
			value=self._front._value
		elif self._front._value==key:
			value=self._front._value
			self._front=self._front._next
			self._rear._next=self._front
		if self._current._value==key:
			value=self._current._value
			self._current=self._current._next
			if self._prev:
				self._prev._next=self._current
		else:
			prev=None
			current=self._front
			while current is not self._rear and current._value!=key:
				prev=current
				current=current._next
			if current._value==key and current is self._rear:
				value=self._rear._value
				self._rear=prev
				self._rear._next=self._front
			elif current._value==key:
				value=current._value
				prev._next=current._next
		if value: self._count-=1
		self._check_reset()

	def __str__(self):
		current=self._front
		s=''
		while current is not None and current is not self._rear:
			s+='{}-->'.format(current._value)
			current=current._next
		if current is not None:
			s+='{}<--'.format(current._value)
		return s
