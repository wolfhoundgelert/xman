class Child:

    def __init__(self):
        self.parent = None

    @property
    def root(self):  # TODO check usage
        node = self
        while node.parent is not None:
            node = node.parent
        return node


class Parent(Child):  # TODO check if I need this

    def __init__(self):
        super().__init__()
        self.__children = []

    def has(self, child: Child):
        return child in self.__children

    def add(self, child: Child):
        if self.has(child):
            raise ValueError(f"`{self} already has `{child}`")
        self.__children.append(child)
        child.parent = self

    def remove(self, child: Child):
        if not self.has(child):
            raise ValueError(f"`{self}` doesn't have `{child}`")
        self.__children.remove(child)
        child.parent = None

    def children(self):
        return self.__children.copy()
