from graphmaker.graph import Graph
from graphmaker.resources import Tiger
from graphmaker.reports.graph_report import graph_report

# Some states are missing from the vtd-adjacency-graphs repository because
# the Census TIGER 2012 data set contains no VTDs for that state.
# Kentucky is one of those states, so we'll use it as an example.

# As a replacement, we can use Census tracts instead.
# The same technique can be used to make a graph of counties (e.g. for Iowa)
# or any other shapefile you want.

# First we'll download the tracts:

# The Tiger class lets us access Census shapefile URLs as if they were
# just python objects.
kentucky_tracts = Tiger(2012).tract.ky
# or, equivalently (fips)
kentucky_tracts = Tiger(2012).tract['21']
# or, equivalently (full name)
kentucky_tracts = Tiger(2012).tract.kentucky

# To download from the url, call download() and pass the directory
# you want to save the shapefiles in. (Make sure the directory exists.)
kentucky_tracts.download(target='./kentucky/')

# The shapefile will be named 'tl_2012_21_tract.shp
kentucky_queen = Graph.from_shapefile(
    './kentucky/tl_2012_21_tract.shp', adjacency_type='queen')

# ...This might take a while...

# Once it's done, you can view some statistics about the graph like this:
print(graph_report(kentucky_queen.graph))

# And then save the graph wherever you want:
kentucky_queen.save('./kentucky/queen.json')
