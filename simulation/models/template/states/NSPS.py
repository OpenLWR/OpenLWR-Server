from simulation.models.template.custom_components.NSPS import NuclearSystemProtectionSystem

import json
import copy

class State:
    def __init__(self):
        self.NSPS = NuclearSystemProtectionSystem()

        self.load_state(json.loads("""{"NSPS": {"scram": true, "RPSDivs": [{"Trips": [], "AllTrips": [], "Tripped": false}, {"Trips": [], "AllTrips": [], "Tripped": false}, {"Trips": [], "AllTrips": [], "Tripped": false}, {"Trips": [], "AllTrips": [], "Tripped": false}]}}"""))
    
    def list_fixer(self,values): #looks through lists for classes and fixes them if needed
        val = copy.deepcopy(values)

        i = 0
        while i < len(val):
            if hasattr(val[i],'__dict__'):
                val[i] = self.class_fixer(val[i])
            elif isinstance(val,list):
                val[i] = self.list_fixer(val[i])

        return val


    def class_fixer(self,values): #classes cant be serialized to JSON, so this will condition it
        val =  copy.deepcopy(values.__dict__)

        for value in val:
            if hasattr(val[value],'__dict__'):
                val[value] = self.class_fixer(val[value])
            elif isinstance(val[value],list):
                val[value] = self.list_fixer(val[value])

        return val

    def save_state(self):
        current_state = copy.deepcopy(self.__dict__)

        

        for value in current_state:
            if hasattr(current_state[value],'__dict__'):
                current_state[value] = self.class_fixer(current_state[value])

        return current_state
    
    def load_list(self,entry,lst):
        if hasattr(entry,'__dict__'):
            obj = entry.__dict__
        else:
            obj = entry

        i = 0
        while i < len(lst):
            if (hasattr(obj[i],'__dict__') or isinstance(obj[i],dict)):
                self.load_class(obj[i],lst[i])
            elif isinstance(obj[i],list):
                self.load_list(obj[i],lst[i])
            else:
                obj[i] = lst[i]
            i+=1


    def load_class(self,entry,dictionary):
        if hasattr(entry,'__dict__'):
            obj = entry.__dict__
        else:
            obj = entry

        for value in dictionary:
            if (hasattr(obj[value],'__dict__') or isinstance(obj[value],dict)):
                self.load_class(obj[value],dictionary[value])
            elif isinstance(obj[value],list):
                self.load_list(obj[value],dictionary[value])
            else:
                obj[value] = dictionary[value]


    def load_state(self,dictionary):
        obj = self.__dict__

        for value in dictionary:
            if (hasattr(obj[value],'__dict__') or isinstance(obj[value],dict)):
                self.load_class(obj[value],dictionary[value])
            elif isinstance(obj[value],list):
                self.load_list(obj[value],dictionary[value])
            else:
                obj[value] = dictionary[value]

