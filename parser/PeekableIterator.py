'''
Wrapper for iterators to support looking at the next element without extracting.
'''

from typing import Generic, Iterator, TypeVar

T = TypeVar('T')

class PeekableIterator(Generic[T]):
    _itr: Iterator[T]
    _next: T
    _has_next: bool
    def __init__(self, itr: Iterator[T]):
        self._itr = itr
        self._next = None
        self._has_next = False
    def __iter__(self) -> Iterator[T]:
        return self
    def __next__(self) -> T:
        if self._has_next:
            self._has_next = False
            return self._next
        return next(self._itr)
    def peek(self) -> T:
        if not self._has_next:
            self._next = next(self._itr)
            self._has_next = True
        return self._next
