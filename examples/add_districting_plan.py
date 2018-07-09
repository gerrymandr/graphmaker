from graphmaker.graph import Graph
from graphmaker.match import match

# Load the state adjacency graph from wherever you downloaded it to
my_state = Graph.load(
    '../graphmaker/graphs/vtd-adjacency-graphs/vtd-adjacency-graphs/12/queen.json')

# Match the VTDs to 'State Legislature Upper Chamber' Districts
match(my_state, 'VTD', 'SLDU')

# Print all the nodes, to see that the 'SLDU' attribute has been added
print(my_state.graph.nodes(data=True))

# Save the graph back to the same file
my_state.save()
