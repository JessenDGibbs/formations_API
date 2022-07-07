import random 
import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np 
class TriangulationNotSuccessfulException(Exception):
	'''
	Custom error type that gets thrown
	when an internal check yields that the graph resulting from a trianguliation
	is somehow not chordal.
	'''

class TimeLimitExceededException(Exception):
	'''
	Custom error type that gets thrown
	when a time limit was set and is exceeded.
	'''

class TriangulationAlgorithm:
	'''
	Superclass for all triangulation algorithms
	Args:
		G : the graph to triangulate
		reduce_graph : if set to True, all single-vertex-seperators get removed from the graph,
						and a subgraph for each component gets constructed
		timeout : if timeout is set to a value > 0, it specifies the maximum time in seconds the algorithm
						is allowed to run before it gets terminated
	Attributes:
		G : the original graph
		component_subgraphs : a list of graphs in networkx format
			if G was reduced, this contains each component of the reduced G as a graph.
			otherwise, it contains only G
		H : the triangulated graph
		edges_of_triangulation : the set of edges that are added to G to achieve H
		alpha : a dict {node: int} that contains a perfect elimination ordering, if one gets constructed
	'''
	def __init__(self, G, reduce_graph=True, timeout=-1):
		self.G = G
		self.component_subgraphs = [G]
		if reduce_graph:
			self.get_relevant_components()
			self.get_chordedge_candidates()
			
		self.H = None
		self.edges_of_triangulation = []
		self.alpha = {}
		self.timeout = timeout

	def run(self):
		self.alpha = {}
		for C in self.component_subgraphs:
			# get triangulation for each connected component of the reduced graph G_c:
			self.edges_of_triangulation += self.triangulate(C)
		
		self.H = self.G.copy()
		self.H.add_edges_from(self.edges_of_triangulation)
		
		# does not need to be chordal for PTPG
		#if not nx.is_chordal(self.H):
			#raise self.TriangulationNotSuccessfulException("Resulting graph is somehow not chordal!")
			
	def run_randomized(self):
		self.edges_of_triangulation = []
		self.alpha = {}
		for C in self.component_subgraphs:
			# get triangulation for each connected component of the reduced graph G_c:
			self.edges_of_triangulation += self.triangulate(C, randomized=True)
		
		self.H = self.G.copy()
		self.H.add_edges_from(self.edges_of_triangulation)
		
		# does not need to be chordal for PTPG
		#if not nx.is_chordal(self.H):
			#raise self.TriangulationNotSuccessfulException("Resulting graph is somehow not chordal!")
	
	def get_triangulated(self):
		return [self.H, self.edges_of_triangulation]
		
	def get_triangulation_edges(self):
		return self.edges_of_triangulation

	def get_triangulation_size(self):
		return len(self.edges_of_triangulation)
		
	def get_relevant_components(self):
		#logging.info("TA.get_relevant_components")
		# construct set of possible chord edges:
		# only consider subgraphs after all separators of size 1 have been removed from graph:
		cycle_nodes = list(set([n for c in nx.cycle_basis(self.G) for n in c]))
		single_node_separators = [n for n in self.G.nodes() if n not in cycle_nodes]
		self.G_c = self.G.subgraph(cycle_nodes)
		self.component_subgraphs = [self.G_c.subgraph(c) for c in nx.connected_components(self.G_c) if len(c) > 1]
		
		#logging.debug("cycle nodes: "+str(cycle_nodes))
		#logging.debug("nodes to remove: "+str(single_node_separators))
		#logging.debug("Number of components of the reduced graph: "+str(len(self.component_subgraphs)))
	
	def get_chordedge_candidates(self):
		#logging.info("TA.get_chordedge_candidates")
		if self.G_c == None:
			self.get_relevant_components()

		self.chordedge_candidates = []
		for c in nx.connected_components(self.G_c):
			c = list(c)
			for i in range(len(c)):
				for j in range(i+1, len(c)):
					chord_edge = (c[i], c[j])
					if chord_edge not in self.G.edges():
						self.chordedge_candidates.append(chord_edge)
		
		#logging.debug ("chordedge candidates: "+str(self.chordedge_candidates))

	def draw_triangulation(self):
		edges_original = self.G.edges()

		#pos = nx.shell_layout(self.G)
		pos = nx.kamada_kawai_layout(self.G)
		
		if not self.H == None:
			nx.draw_networkx_nodes(self.H, pos, node_color='r', node_size=50)
			nx.draw_networkx_edges(self.H, pos, edgelist=edges_original, width=1, edge_color='black')
			nx.draw_networkx_edges(self.H, pos, edgelist=self.edges_of_triangulation, width=1, edge_color='blue')
		else:
			nx.draw_networkx_nodes(self.G, pos, node_color='r', node_size=50)
			nx.draw_networkx_edges(self.G, pos, edgelist=self.G.edges(), width=1, edge_color='black')

		labels = {}
		for n in self.G.nodes():
			labels[n] = n
		nx.draw_networkx_labels(self.G, pos, labels, font_size=16)
		plt.axis('off')
		plt.show()

class Algorithm_MCSM(TriangulationAlgorithm):
	'''
	Args:
		G : a graph in netwokx format
		randomize : if set to True, the order in which the nodes are processed is randomized
	
	Returns:
		H : a minimal triangulation of G.
		alpha : the corresponding minimal elimination ordering of G 
	'''
	
	def __init__(self, G, reduce_graph=True, timeout=-1):
		#logging.info("=== LexM.Algorithm_LexM.init ===")
		super().__init__(G, reduce_graph, timeout)
		self.alpha = {}

	def get_alpha(self):
		return self.alpha

	def triangulate(self, C, randomized=False):
		'''
		Implementation of MCS-M Algorithm 
			Bery, Blair, Heggernes, Peyton: Maximum Cardinality Search for Computing Minimal Triangulations of Graphs
			https://link.springer.com/article/10.1007/s00453-004-1084-3
		to construct a minimal elemination ordering alpha of a graph G
		and the corresponding minimal triangulation H(G, alpha)
		
		Args:
			C : a graph in networkx format
			randomized : 
		
		Returns:
			F : a set of edges s.t. C + F is a minimal triangulation C.
		'''
		#logging.info("=== triangulate_MCS_M ===")
		print("=== triangulate_MCS_M ===")
		
		F = []
		unnumbered_nodes = [n for n in C.nodes()]
		if randomized:
			random.shuffle(unnumbered_nodes)
			
		weight = {n : 0 for n in unnumbered_nodes}
		n = len(C)
		for i in range(n,0, -1):
			# check timeout:
			if self.timeout > 0 and time.time() > self.timeout:
				raise TriangulationAlgorithm.TimeLimitExceededException("Time Limit Exceeded!")

			#logging.debug("Iteration: "+str(i))
			#logging.debug("all unnumbered nodes:")
			#logging.debug([str(n)+": "+str(weight[n]) for n in unnumbered_nodes])
			
			# get node with maximum weight:
			node_v = unnumbered_nodes[0]
			maxweight = weight[node_v]
			for n in unnumbered_nodes:
				if weight[n] > maxweight:
					node_v = n
					maxweight = weight[node_v]
			self.alpha[node_v] = i
			unnumbered_nodes.remove(node_v)
			S = []
			for node_u in unnumbered_nodes:
				if not node_u == node_v:
					unnumbered_lowerweight_nodes = [node_x for node_x in unnumbered_nodes if weight[node_x] < weight[node_u]]
					if nx.has_path(C.subgraph(unnumbered_lowerweight_nodes+[node_v, node_u]),node_v, node_u):
						#logging.debug("Add target node "+str(node_u)+" to set S")
						print("Add target node "+str(node_u)+" to set S")
						S.append(node_u)
			for node_u in S:
				weight[node_u] += 1
				if not (node_v, node_u) in C.edges():
					F.append((node_v, node_u))
					
			#logging.debug("End of iteration. all node labels:")
			print("End of iteration. all node labels:")
			#logging.debug([str(n)+": "+str(weight[n]) for n in C])	
			print([str(n)+": "+str(weight[n]) for n in C])	
		print("F a set of edges s.t. C + F is a minimal triangulation C.:", F)
		return F #[F[-1]] #only the last one for now

def triangulate_MCSM(G, randomized=False, repetitions=1, reduce_graph=True, timeout=-1):
	algo = Algorithm_MCSM(G, reduce_graph, timeout)
	if not randomized:
		algo.run()
		return {
			"H" : algo.get_triangulated(),
			"size" : len(algo.get_triangulation_edges()),
			"alpha" : algo.get_alpha(), 
			"mean" : len(algo.get_triangulation_edges()),
			"variance" : 0,
			"repetitions" : 1
			}
	else:
		H_opt = None
		alpha_opt = None
		size_opt = None
		all_sizes = []
		for i in range(repetitions):
			algo.run_randomized()
			all_sizes.append(len(algo.get_triangulation_edges()))
			if H_opt == None or len(algo.get_triangulation_edges()) < size_opt:
				H_opt = algo.get_triangulated()
				alpha_opt = algo.get_alpha()
				size_opt = len(algo.get_triangulation_edges())
		return {
			"H" : H_opt,
			"size" : size_opt,
			"alpha" : alpha_opt, 
			"mean" : np.mean(all_sizes),
			"variance" : np.var(all_sizes),
			"repetitions" : repetitions
			}