from .geometry import (
    Number,
    Point,
    Line as GeometryLine # noqa
)
from typing import Tuple, List, Optional, Union


##### Geometry related #######
Coords = Tuple[Number, Number]
###############################

######## Relationshipd ########
PointOfIntersections = List[
    List[Union[Point, None]]
]
PassThroughs = List[
    List[bool]
]
InLines = List[
    List[bool]
]
#############################

######## Line ########
Line = List[int]
Lines = List[Line]
######################

######### Vertex ############
BBox = Tuple[
    Coords,
    Coords,
    Coords,
    Coords,
    Optional[int],
]
BBoxes = List[BBox]
#############################
