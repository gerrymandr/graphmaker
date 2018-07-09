from graphmaker.graph import Graph

# We'll continue from the Kentucky example:

# Load your graph from wherever you saved it:
kentucky_queen = Graph.load('./kentucky/queen.json')

# You can add columns from a shapefile:
kentucky_queen.add_columns_from_shapefile('./kentucky/tl_2012_21_tract.json',
                                          columns=['ALAND', 'AWATER', 'COUNTYFP', 'STATEFP'])
# Or from a CSV (using a made up example):
kentucky_queen.add_columns_from_csv('./votes.csv', columns=['D_VOTES_2020', 'R_VOTES_2020'],
                                    id_column='TRACT')
# By writing id_column='VTD', we note that the column with IDs that match the nodes of the
# graph (the tract GEOIDs) is 'TRACT'. Usually this won't be necessary, because the program
# will automatically recognize common names like 'GEOID' or 'ID'.
