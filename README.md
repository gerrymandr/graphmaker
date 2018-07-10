# graphmaker

Builds adjacency graphs for use with RunDMCMC.

## Examples

### Create an adjacency graph from Census geometries

Some states are missing from the vtd-adjacency-graphs repository because
the Census TIGER 2012 data set contains no VTDs for that state.
Kentucky is one of those states, so we'll use it as an example.

As a replacement, we can use Census tracts instead.
The same technique can be used to make a graph out of any shapefile. This could
be applied to counties (e.g. for Iowa), city wards, strange back-alley precinct
geometries... the sky's the limit!

First we'll download the tracts. The `Tiger` class in `graphmaker.resources` lets us
access Census shapefile URLs as if they were just python objects. We can access
the URL for Kentucky's Census tract shapefiles like this:

```python
from graphmaker.resources import Tiger

kentucky_tracts = Tiger(2012).tract.ky
# or, equivalently (fips)
kentucky_tracts = Tiger(2012).tract['21']
# or, equivalently (full name)
kentucky_tracts = Tiger(2012).tract.kentucky
```

To download from the url, call `download()` and pass the directory
you want to save the shapefiles in. (You may need to make sure the directory exists first.)

```python
kentucky_tracts.download(target='./kentucky/')
```

The shapefile in the target folder will be named `tl_2012_21_tract.shp`. Now
we can make the graph from the shapefile like this:

```python
from graphmaker.graph import Graph

kentucky_queen = Graph.from_shapefile(
    './kentucky/tl_2012_21_tract.shp', adjacency_type='queen')
```

...This might take a while...

Once it's done, you can view some statistics about the graph like this:

```python
from graphmaker.reports.graph_report import graph_report

print(graph_report(kentucky_queen.graph))
```

Lastly (and crucially!), save the graph wherever you want:

```
kentucky_queen.save('./kentucky/queen.json')
```

## Add data columns to a graph

We'll continue with our Kentucky example. First, load your graph from wherever you saved it:

```python
kentucky_queen = Graph.load('./kentucky/queen.json')
```

Then you can add columns from a shapefile:

```python
kentucky_queen.add_columns_from_shapefile('./kentucky/tl_2012_21_tract.shp',
                                          columns=['ALAND', 'AWATER', 'COUNTYFP', 'STATEFP'])
```

Or from a CSV (using an imaginary example here):

```python
kentucky_queen.add_columns_from_csv('./votes.csv',
                                    columns=['D_VOTES_2020', 'R_VOTES_2020'],
                                    id_column='TRACT')
```

By writing `id_column='VTD'`, we are signalling that the column with IDs that match the nodes of the
graph (the tract GEOIDs) is `'TRACT'`. Usually this won't be necessary, because the program
will automatically recognize common names like `'GEOID'` or `'ID'`.

## Add a districting plan assignment

The `graphmaker.match` module has a function called `match` that will use census
block assignment files to try to match 'units' (normally VTDs) to 'parts' (like
congressional districts or state legislative districts). The Block Assignment Files
from the Census have matchings for State Upper and Lower Legislatures included,
so you can run Markov chains even if your state has only one congressional
district.

First we'll load the state adjacency graph from wherever you downloaded it to.
We'll use Florida as an example this time.

```python
from graphmaker.graph import Graph

my_state = Graph.load('../graphs/12/queen.json')
```

```python
from graphmaker.match import match

match(my_state, 'VTD', 'SLDU')
```

Now we can print all the nodes and verify that the 'SLDU' attribute has been added.

```python
print(my_state.graph.nodes(data=True))
```

And save, of course:

```python
my_state.save()
```
