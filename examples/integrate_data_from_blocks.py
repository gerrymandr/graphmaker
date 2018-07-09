from graphmaker.resources import BlockAssignmentFile
from graphmaker.graph import Graph
from graphmaker.integrate import integrate

# You can also add columns from a Pandas dataframe, which lets you do whatever joining,
# transformation, or merging that you need to do before adding it to the graph.

# A good way to do this is with our `integrate` function to take Census block-level
# statistics (like population) and add them to the VTD graph.

# First we need to download Block Assignment Files. These match census blocks to bigger
# subdivisions (like VTDs) so that we know how to add up the block-level data.

# We'll use Florida:

blocks = BlockAssignmentFile('12').download(target='./florida/blocks/')

# This actually downloads a whole set of files, with matchings from blocks to multiple
# different types of subdivisions, including Upper and Lower State Legislatures and
# elementary school districts.

# Now let's load our graph:
florida = Graph.load('./florida/queen.json')

df = integrate('./florida/blocks/BlockAssign_ST12_FL_VTD', ['POP10'], 'VTD')

florida.add_columns_from_df(df, columns=['POP10'])
