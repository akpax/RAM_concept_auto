import pandas as pd
import re

class ElementFinder:
    """
    Accesses locations of elements in RAM concept
    """
    def __init__(self, model):
        self.struct_layer = model.cad_manager.structure_layer


    def find_point_springs(self, return_df=True):
        spring_locations =[]
        springs = self.struct_layer.point_springs
        for spring in springs:
            
            id = spring.number
            location_str = spring.location.to_bracket_string()
            location = self.parse_location_string(location_str)
            spring_dict = {"ID": id,
                           "x_cord": location[0],
                           "y_cord": location[1]
                           }
            spring_locations.append(spring_dict)

        if return_df:
            return pd.DataFrame(spring_locations)
        else:
            return spring_locations

    def parse_location_string(self,location_string: str) -> list:
        # Use regular expression to find x and y values inside brackets
        match = re.search(r'\[(-?[\d.]+)\]\[(-?[\d.]+)\]', location_string)
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            return [x, y]
        else:
            return None

            



