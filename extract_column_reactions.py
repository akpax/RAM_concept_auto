# """
# Cannot extract spring reactions yet in this version of API. Only column reactions can be extracted.
# """
# import sys  #add RAM concept API instalation  to path so it can be found (it is in same location as application not in venv)
# raw_path = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
# sys.path.insert(1, raw_path)

# from ram_concept.concept import Concept
# from ram_concept.model import Model
# from ram_concept.model import StructureType
# from ram_concept.force_loading_layer import ForceLoadingLayer
# from ram_concept.element_layer import ElementLayer
# from ram_concept.point_load import PointLoad
# from ram_concept.point_2D import Point2D
# from ram_concept.result_layers import ReactionContext


# import pandas as pd

# model_path = r"G:\2021jobs\2021,035 - 1320 Bayport Laboratory\Calculations\2_Gravity\Concrete Slab\Mat Slab\RAM concept finished struct (inlcudes live loadings and  finishings)\21035_Mat Slab_09062023_cracked_t34_all_loads_noDewater.cpt"

# concept = Concept.start_concept(headless=True)
# concept.open_file(model_path)

# model = Model(concept)
# cad_manager = model.cad_manager
# element_layer = cad_manager.element_layer

# # get all the load combos
# load_combos = cad_manager.load_combo_layers

# for i,combo in enumerate(load_combos):
#     print(combo.name)
#     if i==1:
#         for col_element in element_layer.column_elements_above:
#             print("Name: {col_element.name}")
#             reaction = combo.column_reaction(col_element, ReactionContext.STANDARD)
#             print(f"Reaction: {reaction}")
#             print(f"Location: {col_element.location}\n")