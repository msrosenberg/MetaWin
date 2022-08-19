"""
Module containing the class associated with storing and manipulating phylogenetic trees
"""


class Node:
    """
    A class which represents a single node of a phylgenetic tree

    The class works by hierarchically by pointing to other nodes, either as ancestor or as a set of descendants.
    """

    def __init__(self):
        self.__name = ""
        self.__branch_length = 1
        self.__ancestor = None
        self.__descendants = list()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def branch_length(self):
        """
        The branch length represents the distance from the node to its ancestor
        """
        return self.__branch_length

    @branch_length.setter
    def branch_length(self, value):
        self.__branch_length = value

    @property
    def descendants(self):
        return self.__descendants

    @property
    def ancestor(self):
        return self.__ancestor

    @ancestor.setter
    def ancestor(self, value):
        self.__ancestor = value

    def add_child(self, new_child):
        """
        add a new descendant to the node. the function automatically assigns this node as the ancestor of the child
        """
        self.descendants.append(new_child)
        new_child.ancestor = self

    def n_descendants(self) -> int:
        """
        return the immediate number of descendants of the node
        """
        return len(self.descendants)

    def root(self):
        """
        find and return the node representing the root of the tree
        """
        if self.ancestor is None:
            return self
        else:
            return self.ancestor.root()

    def is_descendant(self, query) -> bool:
        """
        is the query node a descendant of the calling node
        """
        result = False
        for d in self.descendants:
            if d == query:
                result = True
            elif d.is_descendant(query):
                result = True
        return result

    def is_sibling(self, query) -> bool:
        """
        is the query node a sibling (same direct ancestor) of the calling node
        """
        return self.ancestor == query.ancestor

    def n_tips(self) -> int:
        """
        number of tips descended from this node, including itself
        """
        if self.n_descendants() == 0:
            return 1
        else:
            count = 0
            for d in self.descendants:
                count += d.n_tips()
            return count

    def distance_to_ancestor(self, query) -> float:
        """
        returns the sum of branch lengths between this node and the queried ancestor

        Note that if the query is not an ancestor this will get stuck in a loop.
        """
        distance = 0
        current_node = self
        while current_node != query:
            distance += current_node.branch_length
            current_node = current_node.ancestor
        return distance

    def common_ancestor(self, query):
        """
        returns the node representing the common ancestor between this node and the query, including the case
        where one is the ancestor of the other
        """
        if query.is_descendant(self):
            return query
        else:
            common_anc = self
            while not common_anc.is_descendant(query):
                common_anc = common_anc.ancestor
            return common_anc

    def distance_on_tree(self, query) -> float:
        """
        returns the sum of branch lengths separating this node from the query node on the tree
        """
        if self.is_descendant(query):
            return query.distance_to_ancestor(self)
        elif query.is_descendant(self):
            return self.distance_to_ancestor(query)
        else:
            common_anc = self.common_ancestor(query)
            return (self.distance_to_ancestor(common_anc) +
                    query.distance_to_ancestor(common_anc))

    def max_node_tip_length(self) -> float:
        """
        find the longest distance between a node and its most distance descendant
        """
        long = 0
        for d in self.descendants:
            long = max(long, d.max_node_tip_length())
        return long + self.branch_length

    def max_node_name(self) -> int:
        """
        find the longest name associated with a node and its descendants
        """
        long = len(self.name)
        for d in self.descendants:
            long = max(long, d.max_node_name())
        return long

    def tip_names(self) -> list:
        """
        return a list of all tip names associated with a node
        """
        names = []
        if self.n_descendants() == 0:
            names.append(self.name)
        else:
            for d in self.descendants:
                names.extend(d.tip_names())
        return names

    def tip_nodes(self) -> list:
        """
        return a list of all tip nodes associated with a node
        """
        tips = []
        if self.n_descendants() == 0:
            tips.append(self)
        else:
            for d in self.descendants:
                tips.extend(d.tip_nodes())
        return tips

    def newick_recursion(self, bl_format: str = "0.4f") -> str:
        """
         This function will output the tree in the Newick format. If bl_format is not an empty string
         it will include branch lengths in the format specified by the bl_format string.
        """
        if self.n_descendants() == 0:
            outstr = self.name
        else:
            outlist = []
            for d in self.descendants:
                outlist.append(d.newick_recursion(bl_format))
            outstr = "(" + ",".join(outlist) + ")"
        if bl_format != "":
            outstr += ":" + format(self.branch_length, bl_format)
        return outstr

    def output_newick(self, bl_format: str = "0.4f") -> str:
        """
        calls the recursive function to produce the Newick form of the tree and adds the semicolon to the end
        """
        return self.newick_recursion(bl_format) + ";"

    def find_tip_by_name(self, query: str):
        """
        find and return the node with the queried name
        """
        if self.name == query:
            return self
        else:
            for d in self.descendants:
                x = d.find_tip_by_name(query)
                if x is not None:
                    return x
        return None


def read_newick_tree(tree_str) -> Node:
    """
    Translate a string representing a tree in Newick format into the internal tree structure and return the
    node representing the root.
    """
    symbols = "(),;"
    i = 0
    current_node = Node()
    while tree_str[i] != ";":
        if tree_str[i] == "(":
            new_node = Node()
            current_node.add_child(new_node)
            current_node = new_node
        elif tree_str[i] == ",":
            current_node = current_node.ancestor
            new_node = Node()
            current_node.add_child(new_node)
            current_node = new_node
        elif tree_str[i] == ")":
            if current_node.ancestor is not None:
                current_node = current_node.ancestor
        else:  # must be a name and/or a branch length
            j = i
            while not tree_str[j] in symbols:
                j += 1
            sub_str = tree_str[i:j]
            if ":" not in sub_str:  # just a name
                current_node.name = sub_str
            elif sub_str[0] == ":":  # just a branch length
                bl = eval(sub_str[1:].strip())
                current_node.branch_length = bl
            else:  # a name and branch length combined
                new_name, new_bl = sub_str.split(":")
                current_node.name = new_name.strip()
                current_node.branch_length = eval(new_bl.strip())
            i = j - 1
        i += 1
    root_node = current_node.root()
    return root_node
