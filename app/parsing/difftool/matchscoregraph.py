class MatchScoreGraph:
    def __init__(self):
        self.edges = {}
        self.edges_by_dst = {}
        self.edge_count = 0
        self.__dstv = set()
        self.__srcv = set()

    def add_edge(self, src, dst, weight):
        if src not in self.edges:
            self.edges[src] = []
        if dst not in self.edges_by_dst:
            self.edges_by_dst[dst] = []

        self.edges[src].append((src, dst, weight))
        self.edges_by_dst[dst].append(src)
        self.edge_count += 1

    def get_max_edge(self):
        curr_max = None
        for src in self.edges:
            for edge in self.edges[src]:
                if not curr_max or (curr_max[2] < edge[2]):
                    curr_max = edge
        return curr_max

    def remove_nodes(self, src, dst):
        self.edge_count -= len(self.edges[src])
        del self.edges[src]
        for n in self.edges:
            old_l = len(self.edges[n])
            self.edges[n] = [x for x in self.edges[n] if x[1] != dst]
            self.edge_count -= old_l - len(self.edges[n])
