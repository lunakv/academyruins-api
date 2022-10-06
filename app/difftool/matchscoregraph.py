class MatchScoreGraph:
    """
    Weighed directed bipartite graph used for calculating rules matches in CRMatcher
    """

    def __init__(self):
        self.edges = {}  # dict of neighbour lists for each vertex in the source partition
        self.edge_count = 0

    def add_edge(self, src: str, dst: str, weight: float) -> None:
        """
        Adds a weighted edge from src to dst into the graph
        """
        if src not in self.edges:
            self.edges[src] = []

        self.edges[src].append((src, dst, weight))
        self.edge_count += 1

    def get_max_edge(self) -> (str, str, float):
        """
        Returns an edge with the maximum weight in the entire graph
        """
        curr_max = None
        for src in self.edges:
            for edge in self.edges[src]:
                if not curr_max or (curr_max[2] < edge[2]):
                    curr_max = edge
        return curr_max

    def remove_nodes(self, src, dst):
        """
        Deletes node src from the source partition and dst from the destination partition along with all their edges
        """
        self.edge_count -= len(self.edges[src])
        del self.edges[src]
        for n in self.edges:
            old_len = len(self.edges[n])
            self.edges[n] = [x for x in self.edges[n] if x[1] != dst]
            self.edge_count -= old_len - len(self.edges[n])
