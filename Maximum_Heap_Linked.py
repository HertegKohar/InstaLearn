from copy import deepcopy
class _MH_Node:
    def __init__(self,value):
        self._value=value
        self._right=None
        self._left=None
        
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
            node=_MH_Node(value)
            self._root=node
            self._count+=1
            self._last=node
        else:
            self._root,inserted=self._push_aux([self._root],None,value)
        

    def _push_aux(self,q,previous,value):
        inserted=False
        node=q.pop(0)
        if not node._left: 
            temp=_MH_Node(value)
            node._left=temp
            self._last=temp
            self._count+=1
            inserted=True

        else:
            q.append(node._left)

        if not node._right and not inserted:
            temp=_MH_Node(value)
            node._right=temp
            self._last=temp
            self._count+=1
            inserted=True
        elif not inserted:
            q.append(node._right)
        if not inserted:
            self._push_aux(q,node,value)

        if node._left is not None and node._left._value>node._value:
            node=self._swap_left(node,previous)

        elif node._right is not None and node._right._value>node._value:
            node=self._swap_right(node,previous)
        return node,inserted

    def _swap_left(self,parent,previous):
        updated=parent._left
        temp_right=updated._right
        updated._right=parent._right
        parent._left=updated._left
        parent._right=temp_right
        updated._left=parent
        if previous is not None:
            if previous._left is parent:
                previous._left=updated
            else:
                previous._right=updated
                
        return updated
        
    def _swap_right(self,parent,previous):
        updated=parent._right
        temp_left=updated._left
        updated._left=parent._left
        parent._right=updated._right
        parent._left=temp_left
        updated._right=parent
        if previous is not None:
            if previous._right is parent:
                previous._right=updated
            else:
                previous._left=updated
        return updated

    def peek(self):
        assert self._root is not None, "Can't peek at an empty heap"
        return self._root._value
    
    def levelorder(self):
        nodes = []
        if self._root is not None:
            queue = []
            queue.append(self._root)

            while len(queue) > 0:
                node = queue.pop(0)
                nodes.append(deepcopy(node._value))

                if node._left is not None:
                    queue.append(node._left)
                if node._right is not None:
                    queue.append(node._right)
        return nodes