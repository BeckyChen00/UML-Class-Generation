from typing import List, Set
from config import *

from Levenshtein import ratio

KIND_CLASS = "class"
KIND_INHERITANCE = "inheritance"
KIND_ASSOCIATION = "association"
KIND_AGGREGATION = "aggregation"
KIND_ENUM = "enum"

class AttributeDef:
    name:str = ""
    type:str = ""
    def __init__(self,name,type):
        self.name = name
        self.type = type
    def getName(self):
        return self.name
    def getType(self):
        return self.type
    # def isMatched(self,oracle):
    #     if ratio(self.name.lower(),oracle.name.lower()) >= 0.9 and self.type == oracle.getType():
    #         return True
    #     return False
    # def isNameMatched(self,oracle):
    #     if ratio(self.name.lower(),oracle.name.lower()) >= 0.9:
    #         return True
    #     return False

class ClassDef:
    name:str = ""
    kind:str = ""
    attributes:List[AttributeDef] = [] 

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.attributes = []
    def getName(self)->str:
        return self.name
    def getKind(self)->str:
        return self.kind
    def getAttributes(self)->List[AttributeDef]:
        return self.attributes
    
    def __str__(self):
        enum_attributes = ", ".join([f"{attr.getName()}" for attr in self.attributes if self.kind==KIND_ENUM])
        cls_attributes = ",".join([f"{attr.getName()}:{attr.getType()}" for attr in self.attributes if self.kind ==KIND_CLASS])
        
        return f"Class: {self.name} ({self.kind}) - Enum Attributes: [{enum_attributes}], Class Attributes: [{cls_attributes}]"
    # def isMatched(self,oracle):
    #     if ratio(self.name.lower(),oracle.name.lower()) >= 0.9:
    #         return True
    #     else:
    #         cand=list(oracle.attributes)
    #         matched = 0
    #         for attr in self.attributes:
    #             for i in range(len(cand)):
    #                 if attr.isMatched(cand[i]):
    #                     matched += 1
    #                     cand.pop(i)
    #                     break
    #         union = len(self.attributes) + len(oracle.attributes) - matched
    #         if union:
    #             jacc = matched / (len(self.attributes) + len(oracle.attributes) - matched)
    #         else:
    #             jacc = 0
    #         return jacc >= 0.6
    # def isNameMatched(self,oracle):
    #     return ratio(self.name.strip().lower(),oracle.name.strip().lower()) >= 0.9
    


class RelationshipDef:
    source = ""
    target = ""
    kind = ""
    srcMulti=False
    trgMulti=False

    def __init__(self,source,target,kind,srcMulti,trgMulti):
        self.source = source
        self.target = target
        self.kind = kind
        self.srcMulti = srcMulti
        self.trgMulti = trgMulti
    def getSource(self):
        return self.source
    def getTarget(self):
        return self.target
    def getKind(self):
        return self.kind
    def getSrcMulti(self):
        return self.srcMulti
    def getTrgMulti(self):
        return self.trgMulti
    def __str__(self):
        return f" {self.srcMulti} {self.source} {self.kind} {self.trgMulti} {self.target}"

    
    
class ModelDef:
    classes : List[ClassDef]
    relationships : List[RelationshipDef]

    def get_all_classes(self)->list[ClassDef]:
        return self.classes
    
    def get_all_relationships(self)->List[RelationshipDef]:
        return self.relationships
    
    def set_classes(self,classes:list[ClassDef]):
        self.classes=classes
        return True
    
    def set_relationships(Self,relationships:List[RelationshipDef]):
        Self.relationships=relationships
        return True
        
    def get_class_by_name(self, name:str) -> ClassDef:
        for cls in self.classes:
            if cls.getName()==name:
                return cls
        return None
        # raise ValueError(f"Class with name {name} not found")
        

    def get_all_parent_classes(self, cls:ClassDef,visited:Set[ClassDef]=None) -> Set[ClassDef]:
        if visited is None:
            visited = set()  # Initialize the visited set if not provided

        # If the class has been already visited, return an empty set to avoid infinite recursion
        if cls in visited:
            return set()

        visited.add(cls)

        all_parents = {cls}
        parents = self.get_parent_classes(cls)

        for par in parents:
            # Recursively add the parents of the parent class
            all_parents.update(self.get_all_parent_classes(par, visited))

        return all_parents
    

    def get_parent_classes(self, cls:ClassDef) -> Set[ClassDef]:
        parents = set()
        name = cls.getName()
        for rel in self.relationships:
            if rel.getKind() == KIND_INHERITANCE and rel.getSource() == name :
                if self.get_class_by_name(rel.getTarget()):
                    parents.add(self.get_class_by_name(rel.getTarget()))
        return parents
    
    
    