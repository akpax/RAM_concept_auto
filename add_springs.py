import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.insert(1, raw_path)

from ram_concept.concept import Concept
from ram_concept.cad_manager import CadManager
from ram_concept.model import Model
from ram_concept.point_spring import DefaultPointSpring
from ram_concept.point_2D import Point2D

concept = Concept.start_concept(headless=True)

#this is needed to covnert 2d point locations to flaots to perform opperations on them
# by default the 2Dpoint.location returns location in "[x][y]" from as string not list
def extract_values(input_string):
    # Remove the brackets and split the string into x and y parts
    x_y_string = input_string.strip("[]")
    x_part, y_part = x_y_string.split('][')
    
    # Convert the x and y parts to floats
    x_value = float(x_part)
    y_value = float(y_part)
    
    return x_value, y_value

def create_point_group(point,delta, configuration="rectangle", include_point=False):
    """
    Takes the center point and creates 2DPoint objects surrounding the center.
    X----------X
    |          |
    |     X    |
    |          |
    X----------X
    
    point: 2DPoint object that is center of grouping
    delta: distance by which x,y coordinates are added to in order to get corners
    include_point: whether to include the center point in the group
    
    Returns a list of Point2D objects representing the group.
    """
    center_x, center_y = extract_values(point.to_bracket_string())
    #create points for bottom two corners
    point_group = [
        Point2D(center_x+delta,center_y-delta),
        Point2D(center_x-delta,center_y-delta)
    ]
    
    if configuration == "rectangle":
        top_corners = [
        Point2D(center_x-delta,center_y+delta),
        Point2D(center_x+delta,center_y+delta)
        ]
        point_group.extend(top_corners)
    elif configuration=="triangle":
        point_group.append(Point2D(center_x,center_y+delta))

    if include_point==True:
        point_group.append(point)
    return point_group





# Check RAM concept initilaization
# response = concept.ping()
# print("RAM Concept responded: " + response)

file_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept Tiedown (dead only)\21035_Mat Slab_08072023_Basic_geotech_hydro_t28_self_dead_wdeckconc_no_spring.cpt"

concept.open_file(file_path)
model = Model(concept)
cad_manager = model.cad_manager

# initaite structure layer (mesh layer)
struct_layer = cad_manager.structure_layer
columns_above = struct_layer.columns_above

col_locations = []

# get column locations
for i, column in enumerate(columns_above):
    col_locations.append(column.location)
    # print(column.location.to_point_list_bracket_string())
    # print(
    #     f"column #: {i} || location (x,y): {column.location.to_point_list_bracket_string()}")

# set spring properties before applying deault point spring to model
default_point_spring = cad_manager.default_point_spring
default_point_spring.angle = 0
default_point_spring.elevation = 0
default_point_spring.kFr = 0
default_point_spring.kFs = 0
default_point_spring.kFz = 627
default_point_spring.kMr = 0
default_point_spring.kMs = 0


for column in col_locations:
    spring_group = create_point_group(column, 2, configuration="triangle", include_point=False)
    for location in spring_group:
        struct_layer.add_point_spring(location)


# # save updated file
model.save_file(r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept Tiedown (dead only)\21035_Mat Slab_08072023_self_dead_wdeckconc_corner_grouping_triangle_no_center.cpt")

concept.shut_down()
