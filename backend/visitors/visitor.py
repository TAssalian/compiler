from __future__ import annotations

from abc import ABC, abstractmethod


class Visitor(ABC):
    @abstractmethod
    def generic_visit(self, node):
        raise NotImplementedError
