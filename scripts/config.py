import os
running_params = {
    'llm':1,# 1：'gpt-3.5-turbo',2： 'gpt-4o' ，3'llama3-8b',4'qwen-plus'
    'cycle':20,  # 每次运行的重复次数
    'temperature_cls': 0.7, # for ours class generation 
    'temperature_association' : 0.7, # for ours association generation 0.9
    'tempetature_inheritance' : 0.7, # for ours inheritance gen1eration 0.8
    'base-temperature': 0.7, # lab1_baseline 
    'max_tokens': 3000, # openai 相关参数1
    'top_p': 1, # openai 相关参数s
    'frequency_penalty': 0, # openai 相关参数
    'presence_penalty': 0, # openai 相关参数
    'ratio':0.9, #
    'jaccard':0.6, # 
    'jaccard_ratio':0.9, # 
    'openai_api_key':'',
    'llama3-8b_api_key':'',
    'http_proxy': 'http://127.0.0.1:10809',        # set http_proxy
    'https_proxy':'http://127.0.0.1:10809',
}

root_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file ={
    'model_file':[
      #   f'{root_file}\dataset\modelsdemo.csv',
      #   f'{root_file}\dataset\models32.csv', 
                  # f'{root_file}\dataset\models-01.csv',        
                  # f'{root_file}\dataset\models-02.csv',
                  f'{root_file}\dataset\models-03.csv',         
                  
     ] 
}


PROMPT_MODEL_2_ROUND= {
'prompt1': """
# Task:
Generate lists of enumerations, classes and attributes based on <Description>. Follow <Guidelines> below step by step to ensure clarity and consistency.

# Guidelines:
1. Identify the <relevant nouns> extracted from <Description>. You need to output only the distinct class names, avoiding overly broad, vague, or redundant terms.
2. Identify <key objects/entities> from <relevant nouns>. You need to output them (e.g., <key object1/entity1>)
3. Define <enumerations> based on the identified <key objects/entities>. You need to output them (e.g., <enum_name>(literal1, literal2)). Avoid creating enumerations like "DayOfTheWeek(monday, tuesday, wednesday, thursday, friday)", "PickupTimeRange(8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 2PM)". 
4. Define <classes> based on the identified <key objects/entities>, ensuring appropriate abstraction levels. You need to output them (e.g., <class_name1>, <class_name2>).
5. Define <attributes> for each class in <classes>. You need to output them(e.g., <class_name>(attribute1: attributeType1, attribute2: attributeType2)). If the class has no attribute, you need to output them (e.g., <class_name>()).
6. Use clear and consistent naming conventions that reflect the role or function of the class within the system. Ensure that keep the class names consistent with the words mentioned in the system description.

# Description:
{}

""",
'prompt2': """
# Task:
Review all the enumerations, classes and attributes based on <Guidelines> step by step. Output the final enumerations, classes and attributes using <Format> strictly.

# Guidelines:
1. All structural components (enumerations, classes, literals, and attributes) MUST USE CamelCase naming convention. However, for components that require only a single word as their name, CamelCase is not necessary (e.g., 'User', 'Employee', 'Role', 'Client').
2. If an enumeration literal contains 'e.g.', 'etc.' or '...', MUST REMOVE these terms only.
3. Remove enumerations such as "DayOfTheWeek(monday, tuesday, wednesday, thursday, friday)", "PickupTimeRange(8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 2PM)", "Season(Summer, Spring, Autumn)". 
4. Ensure that enumeration names and class names are unique to prevent conflicts or redundancy.
5. If an enum or class has no attributes, output it in the format `ClassName()` or `EnumName()`.
6. An attribute type MUST BE a primitive type (i.e., int, boolean, String, Date), an enum type, or a list of a primitive type (e.g., int[] and String[]).
7. Remove attributes that represent relationships or links to other objects without replacement. Ensure the output format remains valid.

# Format:
```
Enumerations:
   + enumerationName(literalName1, literalName2)
Classes:
   + className(attributeName1: attributeType1, attributeName2: attributeType2)
```
"""
}


PROMPT_MODEL_2_ROUND_one_shot= {
'prompt1': """
# Task:
Generate lists of enumerations, classes and attributes based on <Description>. Follow <Guidelines> below step by step to ensure clarity and consistency.

# Guidelines:
1. Identify the <relevant nouns> extracted from <Description>. You need to output only the distinct class names, avoiding overly broad, vague, or redundant terms.
2. Identify <key objects/entities> from <relevant nouns>. You need to output them as classes.
3. Define <enumerations> based on the identified <key objects/entities>. You need to output them (e.g., <enum_name>(literal1, literal2)). Avoid creating enumerations like "DayOfTheWeek(monday, tuesday, wednesday, thursday, friday)", "PickupTimeRange(8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 2PM)". 
4. Define <classes> based on the identified <key objects/entities>, ensuring appropriate abstraction levels.
5. Define <attributes> for each class in <classes>. You need to output them(e.g., <class_name>(attribute1: attributeType1, attribute2: attributeType2)). If the class has no attribute, you need to output them (e.g., <class_name>()).
6. Use clear and consistent naming conventions that reflect the role or function of the class within the system. Ensure that keep the class names consistent with the words mentioned in the system description.

# This is an Example:
## Input Description:
{input_description}
## Output Result:
{output_result}

# Now, please based on the <Input Description> to solve the <Task>.
## Input Description:
{description}
""",
'prompt2': """
# Task:
Review all the enumerations, classes and attributes based on <Guidelines> step by step. Output the final enumerations, classes and attributes using <Format> strictly.

# Guidelines:
1. All structural components (enumerations, classes, literals, and attributes) MUST USE CamelCase naming convention. However, for components that require only a single word as their name, CamelCase is not necessary (e.g., 'User', 'Employee', 'Role', 'Client').
2. If an enumeration literal contains 'e.g.', 'etc.' or '...', MUST REMOVE these terms only.
3. Remove enumerations such as "DayOfTheWeek(monday, tuesday, wednesday, thursday, friday)", "PickupTimeRange(8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 2PM)", "Season(Summer, Spring, Autumn)". 
4. Ensure that enumeration names and class names are unique to prevent conflicts or redundancy.
5. If an enum or class has no attributes, output it in the format `ClassName()` or `EnumName()`.
6. An attribute type MUST BE a primitive type (i.e., int, boolean, String, Date), an enum type, or a list of a primitive type (e.g., int[] and String[]).
7. Remove attributes that represent relationships or links to other objects without replacement. Ensure the output format remains valid.

# Format:
```
Enumerations:
   + enumerationName(literalName1, literalName2)
Classes:
   + className(attributeName1: attributeType1, attributeName2: attributeType2)
```

# This is an Example:
## Input:
{input}
## Output:
{output}

# Now, please based on the <Input Context> to solve the task.
## Input Context:
{context}

"""
}


#-------------------------
# our aproach prompt of association generation
#-------------------------
PROMPT_MODEL_ASSOCIATION_RELATION="""
# Task:
To create a class model based on <Description> and given <Classes>, list all the Association and Composition relationships following <Guidelines> and output using the following <Format> strictly.

# Guidelines:
1. RECALL the meaning of association (i.e., "is-associated-with"), composition (i.e., "is-a-part-of" or "has-a").
2. Consider the classes in (<Classes>) ONLY. Do not generate new classes.
3. List all potential associations and compositions.
4. CHECK your answer, DELETE redundant bidirectional associations.

# Format:
<Intermidiate reasoning results>
   + [mul1] [class1] associate [mul2] [class2] because [reasoning].
   + [mul1] [class1] contain [mul2] [class2] because [reasoning].

```
Final Association Relationships:
   + [mul1] [class1] associate [mul2] [class2] (class1 and class2 MUST be included in given <Classes>. The multiplicity [mul1] and the corresponding multiplicity [mul2] MUST be one of the following options: [0..*], [1], [0..1], [1..*])
Final Composition Relationships:
   + [mul1] [class1] contain [mul2] [class2] (class1 and class2 MUST be included in given <Classes>. The multiplicity [mul1] and the corresponding multiplicity [mul2] MUST be one of the following options: [0..*], [1], [0..1], [1..*])
```

# Description:
{}

# Classes:
{}
"""
#-------------------------
# our aproach prompt of inheritance generation
#-------------------------

PROMPT_MODEL_INHERIT_RELATION="""
# Task:
To create a class model based on <Description> and given <Classes>, list all the inheritances among <Classes> following all steps of <Guidelines> step by step and output each step's reasoning. Note that the parent class and child class MUST include in given <Classes>.

# Guidelines:
1. RECALL the meaning of inheritance (i.e., "is-a-kind-of").
2. MUST DEFINE inheritances conforming to general knowledge of taxonomy and classification. Inheritances should reflect real-word hierachical structures where appropriate (e.g., a Mammal is a kind of Animal).
3. DO NOT mistake inheritance for association/aggregation/message. Inheritance is not about "is-a-part-of", "has-a", "is-associated-with" or "calls". Inheritance is strickly "is-a-kind-of".
4. Consider the classes in (<Classes>) ONLY. Do not generate new classes.
5. List all potential inheritances.
6. CHECK your answer, DELETE incorrect inheritances.

# Format:
<Intermidiate reasoning results>
   + [class1] extends [class2] because [reasoning (i.e., "A is-a-kind-of B")].
   + [class3] does not extend [class4] because [reasoning (e.g., "A is-a-part-of B", "A has-a B", "A is-associated-with B")]], delete this inheritance.

```
Final Inheritance Relationships:
   + [child class] extends [parent class]
```

# Description:
{}

# Classes:
{}
"""

PROMPT_MODEL_REVIEW = """
# Task: 
According to <Description>, revise <Domain Model> step by step based on <Guidelines>. Output using <Format> strictly. 
If no revision is needed, JUST OUPUT the original <Domain Model> and DO NOT change anything.

# Guidelines:
1. If subclasses are generated for an inheritance hierarchy, DO NOT generate an enum for the same hierarchy. 
2. DO NOT mistake inheritance for association/aggregation/message, i.e., is-a-part-of, has-a, is-associated-with, calls.

# Description:
{description}

# Domain Model:
{classes}
{inheritances}
{associations}

# Format:
```
Enumerations:
   + enumerationName(literalName1, literalName2)

Classes:
   + className(attributeName1: attributeType1, attributeName2: attributeType2)
   
Relationships:
# Final Inheritance Relationships:
   + [child class] extends [parent class]
# Final Association Relationships:
   + [mul1] [class1] associate [mul2] [class2]
# Final Composition Relationships:
   + [mul1] [class1] contain [mul2] [class2]
```
"""
#-------------------------
# exp1: baseline prompt 
#-------------------------
PROMPT_MODEL_BASE_zero_shot ="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using format:
Enumerations:
1.enumerationName(literals)
2.enumerationName(literals)
(there might be no or multiple enumerations)

Class:
1.className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))
2.className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))
(there might be multiple classes)

Relationships:
mul1 class1 associate mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]).
(there might be multiple associations)

class1 inherit class2 (class1 and class2 are classes above)
(there might be multiple inheritance)

mul1 class1 contain mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
(there might be multiple composition)

#Description 
{}
"""
 
PROMPT_MODEL_BASE_one_shot ={
}

PROMPT_MODEL_BASE_CoT ="""

"""

#-------------------------
# exp2: baseline prompt 
#-------------------------

PROMPT_MODEL_1_ROUND= """
# Task:
Summarize and output system functional requirements with important instructions.
Generate lists of enumerations, classes and attributes based on the system functional requirements. Follow the guidelines below to ensure clarity and consistency.
 1. Identify key objects from the system description.
 2. Define classes based on the identified objects, ensuring appropriate abstraction levels.
 3. Use clear and consistent naming conventions that reflect the role or function of the class within the system.
Review and list all the classes and enumerations based on guidelines below and output using <Format>.
 1.All structural components (enumerations, classes, literals and attributes) should use Camelcase naming convention.
 2.The 'e.g.','etc','...' character cannot appear in an enumeration's literals.
 3.If an enum or class has no attributes, the output format must preserve the character '()' after the class name. For example: enumeration():[one-sentence rationale], classname():[one-sentence rationale]

# Format:
Enumerations:
1.enumeration(literals1, literals2): [one-sentence rationale]
2.enumeration(literals1, literals2): [one-sentence rationale]
...
Classes:
1.classname(attributeName1: attributeType1, attributeName2: attributeType2 ): [one-sentence rationale]
2.classname(attributeName1: attributeType1, attributeName2: attributeType2 ): [one-sentence rationale]
...

# Description:
{}

"""

#-------------------------
# exp3: baseline prompt
#-------------------------
# PROMPT_MODEL_ALL_RELATION="""
# # Task:

# Step1. To create a class model based on the <description> and the given <classes>, list all the Association relationships using the following format.

# + [mul1] [class1] associate [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options [0..*, 1, 0..1, 1..*]). 

# Step2. To create a class model based on the <description> and the given <classes>, list all the Composition relationships using the following format.

# + [mul1] [class1] contain [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options [0..*, 1, 0..1, 1..*])

# Step3. Semantically check and remove the associations relationships generated above to ensure there are no redundant bidirectional associations. There is no need to display the results of this step

# Step4. Semantically identify possible derived relations among the Association generated above. There is no need to display the results of this step.

# Step5. Delete the derived relationships.There is no need to display the results of this step.

# Step6. Clarify the difference between inheritance relationships and association relationships:
# An Association declares that there can be links between objects of the associated classes. It is a "has-a" relationship.
# Inheritance refers to the process of copying attributes and methods from the parent class to the subclass. It is an "is-a" relationship.

# Step7. To create a class model based on the <description> and the given <classes>, only list all the inheritance (is-a) relationships using the following format:
# + [class1] extends [class2] (class1 and class2 are classes above)

# Step8. There is no need to display the results of the previous steps. If one of the generated relationships is empty, there is no need to print anything. You need to list the generated relationships strictly in the following format: 
# # Final Association Relationships:
# + [mul1] [class1] associate [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
# # Final Composition Relationships:
# + [mul1] [class1] contain [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
# # Final Inheritance Relationships:
# + [class1] extends [class2] (class1 and class2 are classes above)

# # Description
# {}

# # Classes
# {}
# """
PROMPT_MODEL_ALL_RELATION="""
# Task:

Step1. To create a class model based on the <description> and the given <classes>, list all the Association relationships using the following format.

+ [mul1] [class1] associate [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options [0..*, 1, 0..1, 1..*]). 

Step2. To create a class model based on the <description> and the given <classes>, list all the Composition relationships using the following format.

+ [mul1] [class1] contain [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options [0..*, 1, 0..1, 1..*])

Step3. Semantically check and remove the associations relationships generated above to ensure there are no redundant bidirectional associations. There is no need to display the results of this step

Step4. Semantically identify possible derived relations among the Association generated above. There is no need to display the results of this step.

Step5. Delete the derived relationships.There is no need to display the results of this step.

An inheritance is a hierarchical relationship (i.e., is-a) between a general class and a sepcific class. Do not mistake inheritance for association. 
To create a class model based on the <Description> and the given <Classes>, list all the inheritances among <Classes> step by step.
Step6. Identify the inheritances according to the definition of inheritance.

Step7. Remove the incorrect inheritances that should be defined as associations. There is no need to display the results of this step.

Step8. Output using the following format strictly:
# Final Inheritance Relationships:
+ [class1] extends [class2]  (class1 and class2 are classes above)

Step9. There is no need to display the results of the previous steps. If one of the generated relationships is empty, there is no need to print anything. You need to list the generated relationships strictly in the following format: 
# Final Association Relationships:
+ [mul1] [class1] associate [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
# Final Composition Relationships:
+ [mul1] [class1] contain [mul2] [class2] (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
# Final Inheritance Relationships:
+ [class1] extends [class2] (class1 and class2 are classes above)

# Description
{}

# Classes
{}
"""


BaseDev = """
According to the system description below:
{}

As the Senior Engineer, your task is to draw a UML class mermaid diagram showcasing classes, interfaces, and their static structures and relationships. While developing this diagram, consider the following guidelines:
1. Aim for a design that demonstrates a cohesive style and approach, with all components working harmoniously together.
2. Keep the design suitably complex, reflecting the PRD's requirements. Balance the number of classes and methods per class, and be mindful of inheritance depth.
3. Strive for clarity and focus within each class and aim for minimal dependencies between different classes.
4. Ensure your design accurately and fully reflects the PRD, capturing all necessary functionalities and relationships.
5. Create a design that is easy to read and understand, which will be helpful for programming, testing, and future maintenance. Consider the practical aspects of modularity and testing strategies.
6. Remember that a well-thought-out design is the foundation for effective coding. They are interconnected but distinct processes.
7. Write the markdown file to UML_class.md, adhering to the following format:
   # UML class
   `Global_functions` is a placeholder for global functions.
   ```mermaid
   classDiagram
       ......
   ```
8. Treat functions not within a class as global functions, including them in a designated 'Global Functions' section. Detail functions with necessary parameters and data types, including output types if possible.
9. Provide a comprehensive and detailed representation, rather than a brief overview.
10. Seek a balance between accuracy, simplicity, readability, and implementability in your diagram. Consider encapsulating functions within existing classes to avoid unnecessary complexity.
"""

if __name__ == "__main__":
    pass