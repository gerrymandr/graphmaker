from main import main
import os

def path_to_shp(fips):
    return os.path.join('/code/tiger_data', fips, 'tl_2012_' + fips + '_vtd10.shp')

states = os.listdir('/code/tiger_data/')
states = [state for state in states if len(state) == 2]

print(list(path_to_shp(fips) for fips in states))

for fips in states:
    main([path_to_shp(fips)])
