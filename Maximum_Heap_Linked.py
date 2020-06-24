from copy import deepcopy
class _MH_Node:
    def __init__(self,_parent,value):
        self._value=value
        self._parent=_parent
        self._right=None
        self._left=None
        
    def _set_parent(self):
        if self._left is not None and self._right is not None:
            self._left._parent=self
            self._right._parent=self
        elif self._left is not None:
            self._left._parent=self
        elif self._right is not None:
            self._right._parent=self
        
class Maximum_Heap_Linked:
    def __init__(self):
        self._root=None
        self._last=None
        self._count=0

    def __len__(self):
        return self._count

    def is_empty(self):
        return self._count==0

    def push(self,value):
        if self._root is None:
            node=_MH_Node(None,value)
            self._root=node
            self._count+=1
            self._last=node

        else:
            self._root,inserted=self._push_aux([self._root],value)
        

    def _push_aux(self,q,value):
        inserted=False
        node=q.pop(0)
        if not node._left: 
            temp=_MH_Node(node,value)
            node._left=temp
            self._last=temp
            inserted=True

        else:
            q.append(node._left)

        if not node._right and not inserted:
            temp=_MH_Node(node,value)
            node._right=temp
            self._last=temp
            inserted=True
        elif not inserted:
            q.append(node._right)
        if not inserted:
            self._push_aux(q,value)

        if node._left is not None and node._left._value>node._value:
            node=self._swap_left(node)

        elif node._right is not None and node._right._value>node._value:
            node=self._swap_right(node)
        return node,inserted

    def _swap_left(self,parent):
        updated=parent._left
        temp_right=updated._right
        updated._right=parent._right
        parent._right=temp_right
        parent._left=updated._left
        updated._left=parent
        updated._parent=parent._parent
        parent._parent=updated
        updated._set_parent()
        parent._set_parent()
        if updated._parent is not None:
            if updated._parent._left is parent:
                updated._parent._left=updated
            else:
                updated._parent._right=updated
        return updated
        
    def _swap_right(self,parent):
        updated=parent._right
        temp_left=updated._left
        updated._left=parent._left
        parent._left=temp_left
        parent._right=updated._right
        updated._right=parent
        updated._parent=parent._parent
        parent._parent=updated
        updated._set_parent()
        parent._set_parent()
        if updated._parent is not None:
            if updated._parent._left is parent:
                updated._parent._left=updated
            else:
                updated._parent._right=updated
        return updated

    def peek(self):
        assert self._root is not None, "Can't peek at an empty heap"
        return self._root._value
        
MH=Maximum_Heap_Linked()
MH.push(1)
MH.push(2)
MH.push(3)
MH.push(4)
MH.push(5)
print(MH.peek())