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


"""from frameworks import SupportQueries

framework_support = SupportQueries()


class Node:
    def __init__(self, query, parents, attr=[], key_attr=[]):

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

    def traverse(self, N):

        if N.query == "sum":

            return True

        elif N.parents == []:

            return False

        else:

            for parent in N.parents:

                ret = self.traverse(parent)
                if ret == False:

                    return False

            return True


def visualize(n):

    if type(n) == Node:

        for i in n.parents:

            print(i)
            visualize(i)

    else:

        print(n)


def validate(N):

    if N.query == "sum":

        return True

    elif N.parents == []:

        return False

    else:

        for parent in N.parents:

            ret = validate(parent)
            if ret == False:

                return False

        return True


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
            return False"""


"""Maintain a Node , create a child node and parent node as parent"""

"""
N3 = Node("sum", [])
N4 = Node("sum", [])
N1 = Node("set_item", [N3, N4])
N2 = Node("add", [N1])

assert validate(N2) == True

N3 = Node("su", [])
N4 = Node("sum", [])
N1 = Node("set_item", [N3, N4])
N2 = Node("add", [N1])

assert validate(N2) == False"""
