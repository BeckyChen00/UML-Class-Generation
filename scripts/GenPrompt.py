
from config import PROMPT_MODEL_2_ROUND, PROMPT_MODEL_INHERIT_RELATION, PROMPT_MODEL_ASSOCIATION_RELATION, PROMPT_MODEL_REVIEW, BaseDev

H2S_description_example="The Helping Hand Store (H2S) collects second hand articles and non-perishable foods from residents. A resident enters a name, street address, phone number, optional email address, as well as a description of the items to be picked up. \n\nAt the beginning of every weekday, a pickup route for that day is determined for each vehicle for which a volunteer driver is available. Volunteer drivers indicate their available days on the H2S website. The route takes into account the available storage space of a vehicle and the dimensions and weights of scheduled items. After completing all scheduled pickups, the driver drops off all collected second hand articles at H2S?? distribution center. Those articles that can still be used are tagged with an RFID device. In addition, the H2S employee assigns a category to the article from a standard list of 134 categories (e.g., baby clothing, women?? winter boots, fridge, microwave??. \n\nH2S allows those clients to indicate which categories of articles they need. An H2S employee calls them to let them know about the relevant articles that were dropped off that day. Delivery of such articles is made by a volunteer driver before picking up items according to the pickup route.\n"
H2S_answer_example=''' 
# Enumerations:
    + ItemCategory(BabyClothing, Fridge)
# Classes (attributes):
    + H2S()
    + Person( name:string,  address:string,  phoneNumber:string,  emailAddress:string)
    + abstract UserRole()
    + Volunteer() 
    + Resident()
    + SecondHandArticle( codeRFID:string,  discarded:boolean,  category:ItemCategory)
    + abstract item( description:string,  dimension:string,  weight:int,  requestedPickedDate:Date)
    + Route( date:Date)
'''
H2S_classes = '''
    + H2S()
    + Person( name:string,  address:string,  phoneNumber:string,  emailAddress:string)
    + abstract UserRole()
    + Volunteer() 
    + Resident()
    + SecondHandArticle( codeRFID:string,  discarded:boolean,  category:ItemCategory)
    + abstract item( description:string,  dimension:string,  weight:int,  requestedPickedDate:Date)
    + Route( date:Date)
    '''
H2S_answer_example_association = '''
```
Final Composition Relationships:
    + [1] H2S contain [*] Item
    + [1] H2S contain [*] Vehicle
    + [1] H2S contain [*] Route
    + [1] H2S contain [*] UserRole
    + [1] H2S contain [*] Person
    + [1] Volunteer contain [*] Date

Final Association Relationships:
    + [1] Person associate [*] UserRole
    + [0..1] Client associate [*] SecondHandArticle
    + [1] Volunteer associate [*] Route
    + [1] Vehicle associate [*] Route
    + [0..1] Route associate [*] Item
    + [0..1] Route associate [*] SecondHandArticle
    + [1] Resident associate [*] Item
```

'''
H2S_answer_example_inheritance = '''
```
Final Inheritance Relationships:
    + Client inherit UserRole
    + Volunteer inherit UserRole
    + Resident inherit UserRole
    + SecondHandArticle inherit Item
    + FoodItem inherit Item
```
'''


def generate_class_prompt_one_shot(name,description):
    message = []
    message = [
        {"role":"user","content":PROMPT_MODEL_2_ROUND["prompt1"].format(H2S_description_example)},
        {"role":"assistant","content":f"{H2S_answer_example}"},
        {"role": "user", "content": PROMPT_MODEL_2_ROUND["prompt1"].format(description)},
        {"role": "user", "content": PROMPT_MODEL_2_ROUND["prompt2"]},

    ]
    return message

def generate_association_prompt_one_shot(name,classes,description):
    message = [ 
        {"role": "user", "content": PROMPT_MODEL_ASSOCIATION_RELATION.format(H2S_description_example,H2S_classes)} ,
        {"role": "assistant", "content": f"{H2S_answer_example_association}"},
        {"role": "user", "content": PROMPT_MODEL_ASSOCIATION_RELATION.format(description,classes)}   
    ]
    return message

def generate_inheritance_prompt_one_shot(name,classes,description):
    message = [
        {"role": "user", "content": PROMPT_MODEL_INHERIT_RELATION.format(H2S_description_example,H2S_classes)},
        {"role": "assistant", "content": f"{H2S_answer_example_inheritance}"},
        {"role": "user", "content": PROMPT_MODEL_INHERIT_RELATION.format(description,classes)}
    ]
    return message

def generate_relation_prompt(name,classes,description):
    message = []
    prompt = PROMPT_MODEL_ASSOCIATION_RELATION.format(description,classes)
    message = [
        {"role": "user", "content": f"{prompt}"}    
    ]
    return message

def generate_inherit_relation_prompt(name,classes,description):
    prompt = PROMPT_MODEL_INHERIT_RELATION.format(description,classes)
    message = [
        {"role": "user", "content": f"{prompt}"}    
    ]

    return message

def generate_class_atr_prompt(name,description):
    prompt_list ={
        'prompt':'',
        'name':'',
        }
    message = []
    prompt1 = PROMPT_MODEL_2_ROUND["prompt1"].format(description)
    prompt2 = PROMPT_MODEL_2_ROUND["prompt2"]
    message = [
        {"role":"user","content":f"{prompt1}"},
        {"role":"user","content":f"{prompt2}"}
    ]

    return message


def generate_review_prompt(name,descripiton,classes_answer,association_answer,inheritance_answer):
    prompt = PROMPT_MODEL_REVIEW.format(description=descripiton,
                               classes=classes_answer,
                               associations=association_answer,
                               inheritances=inheritance_answer)

    message = [
        {"role":"system","content":"You are a domain modeling review expert. Your task is to review the given <Domain Model> based on <Description>.\n\n"},  
        {"role":"user","content":prompt}
    ]

    return message



def generate_prompt_base_one_shot_BTMS(description):
    # H2S
    message = [
        {"role": "system", "content": "Generate the lists of model classes and associations from a given description."},
        {"role":"user","content":f"Description: A city is using the Bus Transportation Management System (BTMS) to simplify the day-to-day activities related to the city?? public bus system.\n\nThe BTMS keeps track of a driver?? name and automatically assigns a unique ID to each driver. A bus route is identified by a unique number that is determined by city staff, while a bus is identified by its unique licence plate. The highest possible number for a bus route is 9999, while a licence plate number may be up to 10 characters long, inclusive. For up to a year in advance, city staff assigns buses to routes. Several buses may be assigned to a route per day. Each bus serves at the most one route per day but may be assigned to different routes on different days. Similarly, for up to a year in advance, city staff posts the schedule for its bus drivers. For each route, there is a morning shift, an afternoon shift, and a night shift. A driver is assigned by city staff to a shift for a particular bus on a particular day. The BTMS offers city staff great flexibility, i.e., there are no restrictions in terms of how many shifts a bus driver has per day. It is even possible to assign a bus driver to two shifts at the same time.\n\nurrent version of BTMS does not support the information of bus drivers or buses to be updated ??only adding and deleting is supported. However, BTMS does support indicating whether a bus driver is on sick leave and whether a bus is in the repair shop. If that is the case, the driver cannot be scheduled or the bus cannot be assigned to a route. For a given day, an overview shows ??for each route number ??the licence plate number of each assigned bus, the entered shifts and the IDs and names of the assigned drivers. If a driver is currently sick or a bus is in the repair shop, the driver or bus, respectively, is highlighted in the overview.\n"},
        {"role": "assistant", "content": f"Enumeration: \nShift(morning, afternoon, night)\nClasses: \nBTMS()\nBusVehicle(string licencePlate, boolean inRepairShop)\nRoute(int number)\nRouteAssignment(Date date)\nDriver(string name, string id, boolean onSickLeave)\nDriverSchedule(Shift shit) \n\n  Relationships:\n1 BTMS contain * BusVehicle \n1 BTMS contain * Route\n1 BTMS contain * RouteAssignment\n1 BTMS contain * Drivers\n1 BTMS contain * DriverSchedule\n\n* RouteAssignment associate 1 BusVehicle\n* RouteAssignment associate 1 Route\n* DriverSchedule associate 1 Driver\n* DriverSchedule associate 1 RouteAssignment\n\n"},
        {"role":"user","content":f"Description:{description}"}
    ]

    return message

def generate_prompt_base_one_shot_H2S(description):
    # H2S
    message = [
        {"role": "system", "content": "Generate the lists of model classes and associations from a given description."},
        {"role":"user","content":f"Description: The Helping Hand Store (H2S) collects second hand articles and non-perishable foods from residents. A resident enters a name, street address, phone number, optional email address, as well as a description of the items to be picked up. \n\nAt the beginning of every weekday, a pickup route for that day is determined for each vehicle for which a volunteer driver is available. Volunteer drivers indicate their available days on the H2S website. The route takes into account the available storage space of a vehicle and the dimensions and weights of scheduled items. After completing all scheduled pickups, the driver drops off all collected second hand articles at H2S?? distribution center. Those articles that can still be used are tagged with an RFID device. In addition, the H2S employee assigns a category to the article from a standard list of 134 categories (e.g., baby clothing, women?? winter boots, fridge, microwave??. \n\nH2S allows those clients to indicate which categories of articles they need. An H2S employee calls them to let them know about the relevant articles that were dropped off that day. Delivery of such articles is made by a volunteer driver before picking up items according to the pickup route.\n"},
        {"role": "assistant", "content": f"Enumeration:\nItemCategory(Baby Clothing, Fridge, ...)\nClasses:\nH2S()\nPerson(string name, string address, string phoneNumber, string emailAddress)\nabstract UserRole()\nVolunteer() \nResident()\nSecondHandArticle(string codeRFID, boolean discarded, ItemCategory category)\nabstract item(string description, string dimension, int weight, Date requestedPickedDate)\nRoute(Date date)\n\nRelationships:\nRelationships:\n1 H2S contain *Item\n1 H2S contain *Route\n1 H2S contain *UserRole\n1 H2S contain *Person\n1 Volunteer contain *Date\n\nVolunteer inherit UserRole\nResident inherit UserRole\nSecondHandArticle inherit Item\n\n1 Person associate *UserRole\n1 Volunteer associate * Route\n0..1 Route associate *Item\n0..1 Route associate *SecondHandArticle\n1 Resident associate *Item\n\n"},
        {"role":"user","content":f"Description:{description}"}
    ]

    return message



def generate_prompt_base_CoT(descirption):
    message = [
        {'role': 'system', 'content': 'Generate the lists of model classes and associations from a given description. There are only 3 types of associations: associate, inherit, contain. Do not use other names for associations'}, 
        {'role': 'user', 'content': 'Here is the format and example for a class diagram:\n\nEnumerations:\nEnumerationClassName (typename)\nExample: Color(Red, Blue, Yellow)\n\nClass:\nclassName(type attribute)\ntype can be string, boolean, int, date, or list\nExample: Person(string name, int age)\n\nAssociations:\n<Multiplicity>  ClassName1 <relationship> <Multiplicity>  ClassName2\n\n<relationship> can be <associate> OR <contain> OR <inherit>\n<Multiplicity> can be 1, 0, *, 0..1, 1..*\nExample: \n1 Student <associate> * Assignment\n1 SchoolSystem <contain> * Student\n1 Student <inherit> User\n\n\n(If no classes, enumerations or relationships, JUST OUTPUT "None")'}, 
        {'role': 'user', 'content': 'Description: H2S\nThe Helping Hand Store (H2S) collects second hand articles and non-perishable foods from residents of the city  and distributes them to those in need. -> H2S()\n\nH2S also operates in other cities, but each location is run independently. \n\nTo increase the number of items available for distribution, H2S is seeking to offer a Pickup and Delivery Service to its customers, which would allow a resident to schedule a pickup of items from a street address online at the H2S website.  -> Resident()\n\nA resident enters a name, street address, phone number, optional email address, as well as a description of the items to be picked up. -> Person(string name, string address, string phoneNumber, string emailAddress), abstract item(string description), 1 H2S contain * Person\n\nThe resident places the items just outside the front door of the building at the stated street address in the morning of the weekday requested for pickup. ->Date(),  abstract item(string description, Date requestedPickedDate), 1 H2S contain * Item, 1 Resident associate * Item\n\nH2S has a fleet of pickup vehicles, which it uses to collect items from residents. -> Vehicle(), 1 H2S contain * Vehicle\n\nAt the beginning of every weekday, a pickup route for that day is determined for each vehicle for which a volunteer driver is available. -> Route(Date date), 1 H2S contain * Route\n\nVolunteer drivers indicate their available days on the H2S website. -> Volunteer(), 1 Volunteer contain * Date \n\nThe route takes into account the available storage space of a vehicle and the dimensions and weights of scheduled items. -> Vehicle(string dimension, int weightRestriction), abstract item(string description, string dimension, int weight, Date requestedPickedDate), 1 Vehicle associate * Route\n\nA scheduled pickup may occur anytime between 8:00 and 14:00.\n\nAfter completing all scheduled pickups, the driver drops off all collected second hand articles at H2S’s distribution center. -> SecondHandArticle(), 1 SecondHandArticle inherit Item\n\nNon-perishable foods, on the other hand, are directly dropped off at the   food bank, which then deals with these items without further involvement from H2S. -> FoodItem(), 1 FoodItem inherit Item\n\nAt H2S’s distribution center, an H2S employee examines the quality of the received second hand articles. Those articles that can still be used are tagged with an RFID device. -> SecondHandArticle(string codeRFID)\n\nThe H2S employee double checks the description of the article given by the resident and makes any corrections as needed. In addition, the H2S employee assigns a category to the article from a standard list of 134 categories (e.g., baby clothing, women’s winter boots, fridge, microwave…). -> ItemCategory(Baby Clothing, Fridge, ...), SecondHandArticle(string codeRFID, ItemCategory category)\n\nIn some cities in which H2S operates, the distribution center offers an additional service for clients who receive second hand articles from H2S but are not able to personally visit the H2S distribution center. Instead, H2S allows those clients to indicate which categories of articles they need. -> Client(ItemCategory[] neededCategories), 0..1 Client associate * SecondHandArticle\n\n At the end of each day, an H2S employee calls them to let them know about the relevant articles that were dropped off that day. SecondHandArticle(string codeRFID, boolean discarded, ItemCategory category)\n\nIf the client still needs an article, the H2S employee arranges delivery of the article to the client’s home address. Delivery of such articles is made by a volunteer driver before picking up items according to the pickup route. ->1 Volunteer associate * Route,0..1 Route associate * Item, 0..1 Route associate * SecondHandArticle\n\nBecause a Person can be Volunteer, Resident, Client at the same time, we can use a player-role pattern. -> abstract UserRole(), 1 Person associate * UserRole, 1 Client inherit UserRole, 1 Volunteer inherit UserRole, 1 Resident inherit UserRole, 1 H2S contain * UserRole\n\n'},
        {'role': 'user', 'content': f"Description:{descirption}"}
    ]
    

    return message



def generate_prompt_base_zero_shot(description):
    message = [
        {"role": "system", "content":"Generate the lists of model classes and associations from a given description."},
        {"role":"user","content":"Create a class diagram for the following description by giving the enumerations, classes, and relationships using format:\n```\nEnumerations:\n1.enumerationName(literals)\n2.enumerationName(literals)\n(there might be no or multiple enumerations)\n\nClass:\n1.className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))\n2.className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))\n(there might be multiple classes)\n\nRelationships:\nmul1 class1 associate mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]).\n(there might be multiple associations)\n\nclass1 inherit class2 (class1 and class2 are classes above)\n(there might be multiple inheritance)\n\nmul1 class1 contain mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])\n(there might be multiple composition)\n```"},
        {"role":"user","content":f"Description:{description}"}
        ]

    return message

def generate_prompt_base_Dev_zero_shot(description):
    message = [
        {"role": "user", "content":BaseDev.format(description)},
    ]
    return message


