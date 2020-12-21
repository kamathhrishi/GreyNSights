from .frameworks import SupportQueries

framework_support = SupportQueries()


class Node:
    def __init__(self, query, attr=[], key_attr=[], parents=[]):

        self.query = query
        self.attr = attr
        self.key_attr = key_attr
        self.parents = parents

    def inherit(self):

        pass

    def __str__(self):

        str = ""
        print(self.query)
        print(self.attr)
        print(self.key_attr)
        print(self.parents)
        return str


def visualize(n):

    if type(n) == Node:

        for i in n.parents:

            print(i)
            visualize(i)

    else:

        print(n)


def validate(n):

    if type(n) == Node:

        for parent in n.parents:
            if parent in framework_support.pandas:
                return True
            validate(parent)

    else:

        if n in framework_support.pandas:
            return True
        else:
            return False
