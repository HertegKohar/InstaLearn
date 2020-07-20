class _W_Node:
	def __init__(self,value,next_):
		self._value=value
		self._next=next_

	def __str__(self):
		try:
			return '{}-->{}'.format(self._value,self._next._value)
		except AttributeError:
			return '{}'.format(self._value)

class Wheel:
	def __init__(self):
		self._front=None
		self._rear=None
		self._current=None
		self._prev=None
		self._count=0

	def __len__(self):
		return self._count

	def __str__(self):
		current=self._front
		s=''
		while current:
			s+='{}-->'.format(current._value)
			current=current._next

		return s

	def clear(self):
		self._front=None
		self._rear=None
		self._count=0
		self._prev=None
		
	def is_empty(self):
		return not self._front

	def _linear_search(self,key):
		value=None
		prev=None
		current=self._front
		while current and current._value!=key:
			prev=current
			current=current._next

		if current and current._value==key: value=key
		return value,prev,current

	def add(self,value):
		if not self._front:
			self._front=_W_Node(value,None)
			self._rear=self._front
			self._current=self._front
		else:
			self._rear._next=_W_Node(value,None)
			self._rear=self._rear._next		
		self._count+=1

	def get_next(self):
		assert self._front, "Can't get next of an empty wheel"
		if self._current is self._rear:
			self._current=self._front
			self._prev=None
		else:
			self._prev=self._current
			self._current=self._current._next
		return self._current._value

	def pop(self):
		assert self._front, "Can't pop an empty wheel"
		value=self._current._value
		if self._front is self._rear:
			self._front=None
			self._rear=None
			self._current=None
		elif self._current is self._front:
			self._front=self._front._next
			self._current=self._front
			self._prev=None
		elif self._current is self._rear:
			self._prev._next=None
			self._rear=self._prev
			self._current=self._front
			self._prev=None
		else:
			self._current=self._current._next
			self._prev._next=self._current
		self._count-=1
		return value

	def peek(self):
		assert self._front, "Can't peek at an empty wheel"
		return self._current._value

	def remove(self):
		assert self._front, "Can't remove from an empty wheel"
		value,prev,current=self._linear_search(key)
		if value==key:
			if current is self._front:
				self._front=self._front._next
			elif current is self._rear:
				if self._current is self._rear:
					self._current=self._front
					self._prev=None
				self._rear=prev
				self._rear._next=None
			else:
				prev._next=current._next
				if self._current is current:
					self._current=self._current._next
					if self._prev: self._prev._next=self._current
		if not self._front:
			self._rear=None
			self._current=None
			self._prev=None
		return value

	def find(self,key):
		assert self._front, "Can't find in an empty wheel"
		value,_,_=self._linear_search(key)
		return value

	def __iter__(self):
		current=self._front
		while current is not None:
			yield current._value
			current=current._next