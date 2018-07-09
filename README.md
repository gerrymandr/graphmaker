# graphmaker

Builds adjacency graphs for use with RunDMCMC.

```
        fallback
       ...........census tract shapefiles----------------------->
       .                                                         \
vtd shapefiles---------------------------------------------------->
                                                                   \  
block-to-cd assignments___             vtd-to-cd assignments---->--->---adjacency graphs
  (districting plans)     \___________/                            /
                           |match                                 /
block-to-vtd assignments__/                                      /
                       \                                        /
                        +-----------> vtd-level statistics-->--+
                       /  integrate
block-level statistics
   (e.g. population)
```
