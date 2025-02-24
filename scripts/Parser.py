import re

from Matcher import Matcher
from structure import *

class ResultParser:
    def __init__(self):
        self.pattensAndHandlers = [] 

    def add(self,patten,handler):
        regex = re.compile(patten)
        self.pattensAndHandlers.append((regex,handler))
    
    def parse(self,input):
        input = input.strip()
        input = re.sub(r'\b(A|An)\b','1',input)
        for regex,handler in self.pattensAndHandlers:
            match = regex.match(input)
            if match is not None:
                return handler(match)
        return None

class AttributeParser(ResultParser):
    regex = r'(.+)\s*:\s*(.+)'
    regex2 = r'(.+)'
    regex_oracle = r'(\S+)\s+(\S+)'
    def handler(self,match):
        name = match.group(1)
        type = match.group(2)
        return AttributeDef(name,type)
    def handler2(self,match):
        name = match.group(1)
        return AttributeDef(name,'')
    def handler_oracle(self,match):
        type = match.group(1)
        name = match.group(2)
        return AttributeDef(name,type)
    
    def __init__(self):
        super().__init__()
        self.add(self.regex,lambda match:self.handler(match))
        self.add(self.regex_oracle,lambda match:self.handler_oracle(match))
        self.add(self.regex2,lambda match:self.handler2(match))

class ClassParser(ResultParser):
    regex = r'(?:[+\-]?|\d+\.?)\s*\**\s*\b([a-zA-Z][^\s`*(:]+)\b\s*[*]*\s*[\(\{]([^()]*)[\)\}](\s*:.*)?'
    regex1 = r'(?:[+\-]?|\d+\.?)\s*(?:abstract|Abstract)\s*[*]*\s*\b([a-zA-Z][^`*(:]*)\b\s*[\(\{]([^()]*)[\)\}](\s*:.*)?'
    regex2 = r'(?:[+\-]?|\d+\.?)\s*\**\s*\b([a-zA-Z][^*`(\s:]+)\b()(\s*:.*)?'
    regex3 = r'(?:[+\-]?|\d+\.?)\s*\**\s*\b([a-zA-Z][^*`(\s:]+)\b\s*[*]*\s*[\(\{]([^()]*)[\)\}](\s*:.*)?'


    def handler(self,match,kind):
        name = match.group(1).strip()
        attribute_string = match.group(2).strip()
        cls = ClassDef(name,kind)
        parser = AttributeParser()
        for attribute in attribute_string.split(','):
            attr = parser.parse(attribute)
            if attr is not None:
                cls.getAttributes().append(attr)
        return cls
    def __init__(self,kind):
        super().__init__()
        self.add(self.regex,lambda match:self.handler(match,kind))
        self.add(self.regex1,lambda match:self.handler(match,kind))
        self.add(self.regex,lambda match:self.handler(match,kind))
        self.add(self.regex2,lambda match:self.handler(match,kind))
        self.add(self.regex3,lambda match:self.handler(match,kind))



class RelationshipParser(ResultParser): 
    # del
    def checkMultiplicity(self,mul:str):
        if mul is None:
            return 1
            # return False
        # mul_int = int(mul)
        # if mul_int > 1:
            # return '*'
        else:
            return mul
    
    # (?:[+\-]?|\d+\.?)\s*\[*(\d+|\*|\d+\.\.\d+|\d+\.\.\*)?\]*\.?\s*([A-Za-z0-9]+)(?:\(.*\))?\s+\<*associate\>*\s+\[*(\d+|\*|\d+\.\.\d+|\d\.\.|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?
    regex_association_1 =   r'(?:[+\-]?|\d+\.?)\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?\s+\<*associate\>*\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?'
    regex_association_2 =   r'[\d]+\.*\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*associate\>*\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.*\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?'
    regex_aggregation_1 = r'(?:[+\-]?|\d+\.?)\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*|\d+\.*\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*contain\>*\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.*\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?'
    regex_aggregation_2 = r'[\d]+\.*\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*|\d+\.*\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*contain\>*\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.*\*)?\]*\s*([A-Za-z0-9]+)(?:\(\))?'
    regex_association_3 = r'(?:[+\-]?|\d+\.?)\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?\s+.+?\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?'
    regex_association_4 = r'(?:[+\-]?|\d+\.?)\s*\[*(\d+|\*|\d+\.\.\d+|\d*\.\.\*|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)\s+[^0-9*.]+\s+\[*(\d+|\*|\d+\.\.\d+|\d\.*|\d+\.\.\*)?\]*\s*([A-Za-z0-9]+)(?:\(.*\))?'

    def handler1(self,match,kind):
        mulSrc = self.checkMultiplicity(match.group(1))
        src = match.group(2)
        src = src.partition('(')[0]
        mulTrg = self.checkMultiplicity(match.group(3))
        trg = match.group(4)
        trg = trg.partition('(')[0]
        return RelationshipDef(src,trg,kind,mulSrc,mulTrg)
    
    # regex_inheritance = r'[+\-]?\s*([A-Z].*)\s+extends\s+([A-Z].*)'
    # regex_inheritance_baseline = r'[+\-]?\s*\d*\s*([A-Z].*)\s+inherit\s+([A-Z].*)'
    
    regex_inheritance = r'(?:[+\-]?|\d+\.?)\s*\[?([A-Za-z0-9]+)\]?(?:\(\))?\s+\<*(?:extends|extend|inherit|inherits)\>*\s+\[?([A-Za-z0-9]+)\]?(?:\(\))?'
    regex_inheritance_2 = r'(?:[+\-]?|\d+\.?)\s*\[*[\d+|\*|\d+\.\.\d+|\d+\.\.\*]*\]*\.?\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*(?:extends|extend|inherit|inherits)\>*\s+\[*[\d+|\*|\d+\.\.\d+|\d+\.\.\*]*\]*\s*([A-Za-z0-9]+)(?:\(\))?'
    regex_inheritance_baseline = r'(?:[+\-]?|\d+\.?)\s*\d*\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*(?:extends|extend|inherit|inherits)\>*\s+([A-Za-z0-9]+)(?:\(\))?'
    regex_inheritance_baseline_2 = r'[\d+|\*|\d+\.\.\d+|\d+\.\.\*]\.?\s*([A-Za-z0-9]+)(?:\(\))?\s+\<*(?:extends|extend|inherit|inherits)\>*\s+\[*[\d+|\*|\d+\.\.\d+|\d+\.\.\*]\s*([A-Za-z0-9]+)(?:\(\))?'
    
    
    def handler2(self,match):
        src = match.group(1)
        src = src.partition('(')[0]
        trg = match.group(2)
        trg = trg.partition('(')[0]
        return RelationshipDef(src,trg,KIND_INHERITANCE,False,False)
    
    def __init__(self):
        super().__init__()       
        self.add(self.regex_inheritance,lambda match:self.handler2(match))
        self.add(self.regex_inheritance_2,lambda match:self.handler2(match))
        self.add(self.regex_inheritance_baseline,lambda match:self.handler2(match))
        self.add(self.regex_inheritance_baseline_2,lambda match:self.handler2(match))
        self.add(self.regex_association_4,lambda match:self.handler1(match,KIND_ASSOCIATION))
        self.add(self.regex_association_1,lambda match:self.handler1(match,KIND_ASSOCIATION))
        self.add(self.regex_association_2,lambda match:self.handler1(match,KIND_ASSOCIATION))
        self.add(self.regex_aggregation_1,lambda match:self.handler1(match,KIND_AGGREGATION))
        self.add(self.regex_aggregation_2,lambda match:self.handler1(match,KIND_AGGREGATION))
        self.add(self.regex_association_3,lambda match:self.handler1(match,KIND_ASSOCIATION))


class FileParser:
    def parseLines(self,lines:str)->ModelDef:
        
        list_classes = []
        list_relationships = []
        line_list = lines.split('\n')

        class_parser = ClassParser(KIND_CLASS)
        relation_parser = RelationshipParser()
        section = 'classes'  # Track the section we're parsing (could be 'classes', 'relationships', 'enumerations')

        # rela_sign = 1

        for line in line_list:
            line = line.strip()
            if not line:
                continue
            
            try:
                if 'Enumeration'in line or 'Enumerations' in line:
                    section = 'enumerations'
                    class_parser = ClassParser(KIND_ENUM)
                elif 'classes:' in line.lower() or 'class:' in line.lower():
                    section = 'classes'
                    class_parser = ClassParser(KIND_CLASS)
                elif 'Association' in line or 'Relationship' in line:
                    # rela_sign = 0
                    section = 'relationships'
                elif 'None' not in line:
                    # Parsing line based on current section
                    if section == 'classes' or section == 'enumerations': 
                        class_result = class_parser.parse(line)
                        if class_result:
                            list_classes.append(class_result)
                    elif section == 'relationships':
                        relation_result = relation_parser.parse(line)
                        if relation_result:
                            list_relationships.append(relation_result)
            except Exception as e:
                print(f"Error parsing line: {line}. Error: {e}")

        # Create and return the ModelDef object
        model_def = ModelDef()
        model_def.set_classes(list_classes)
        model_def.set_relationships(list_relationships)

        return model_def


# Test
if __name__ == "__main__":
    text_gen = '''
```
classes:
abstract PersonRole()
Abstract ABBE()
AAAA()
SSSS()
Relationships:
1 TeamSportsScoutingSystem contains * Employees
1 TeamSportsScoutingSystem contains * PlayerProfiles
1 TeamSportsScoutingSystem contains * LongList
1 TeamSportsScoutingSystem contains * ScoutingAssignments
1 TeamSportsScoutingSystem contains * ShortList
1 TeamSportsScoutingSystem contains * OfficialOffers
* Employee may have 1 PlayerPosition
* LongList associate 1 Player
* ScoutingAssignment associate 1 Player
* ScoutingReport associate 1 Player
* ShortList associate 1 Player
* OfficialOffer associate 1 Player
```
    '''

    oracle = '''
    Enumeration: 
    Shift(morning, afternoon, night)
    Classes: 
    abstract PersonRole()
    BusVehicle (string licencePlate, boolean inRepairShop)
    Route(int number)
    RouteAssignment(Date date)
    Driver(string name, string id, boolean onSickLeave)
    DriverSchedule(string name,Shift shift)

    Relationship
    * BusVehicle  associate 1 Route
        1 BTMS contain * BusVehicle 
    1 BTMS contain * Route
    1 BTMS contain * RouteAssignment
    1 BTMS contain * Drivers
    1 BTMS contain * DriverSchedule

    * RouteAssignment associate 1 BusVehicle
    * RouteAssignment associate 1 Route
    - Room inherit from Reservation
- Reservation contain mul Room
- Room contain 1..* Reservation
- Reservation associate 1 User
Room contain 1..* Reservation
Reservation associate 1 Guest
User inherit Guest
 1 Room aggregation 1..* Reservation
 1 Reservation association 1 User

    * DriverSchedule associate 1 Driver
    * DriverSchedule associate 1 Route

    BusVehicle extends Driver
    Driver extends Route
    - 1 Entity contain 1..* Entity (for grouping entities under a virtual folder)
- 1 Associate contain 1..* Entity (for linking entities to an associate)
- 1 Associate contain 1..* Entity (for linking entities to an associate)
- 1 Entity inherit 1 Entity (for creating relationships between entities)
- 1 Entity contain 1 Associate (for linking an associate to an entity)
    '''

   # Initialize the parsers
    file_parser1 = FileParser()
    model_gen = file_parser1.parseLines(text_gen)  # Returns an instance of ModelDef
    print("Model 1 Classes:")
    for cls in model_gen.get_all_classes():
        print(cls)
    print("\nModel 1 Relationships:")
    for rel in model_gen.get_all_relationships():
        print(rel)

