import sys
import os

external_module_folder = r"C:\Program Files\Bentley\Engineering\RAM Concept CONNECT Edition\RAM Concept CONNECT Edition V8\python"
sys.path.append(external_module_folder)


from ram_concept.concept import Concept

concept = Concept.start_concept(headless=True)

response = concept.ping()
print("RAM Concept responded: " + response)

concept.shut_down()