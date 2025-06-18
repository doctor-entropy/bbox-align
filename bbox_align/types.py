from .geometry import Point
from typing import Tuple, List, Optional, Union

# ### Geometry related #######
Number = Union[float, int]
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

