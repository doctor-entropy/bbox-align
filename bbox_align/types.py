from .geometry import Number, Point, Line as GeometryLine
from typing import Tuple, List, Optional, Union

# ### Geometry related #######
Coords = Tuple[Number, Number]
###############################

# ###### Line ################
PointOfIntersections = List[
    List[Union[Point, None]]
]
PassThroughs = List[
    List[bool]
]
InLines = List[
    List[bool]
]
Line = List[int]
Lines = List[Line]
# ###########################

# Vertex #####################
Vertices = Tuple[
    Coords,
    Coords,
    Coords,
    Coords,
    Optional[int],
]
BBoxVertices = List[Vertices]
#############################

