import json
import os
import csv
import time
import re
import pandas as pd
import shutil
import openai
import numpy as np
import datetime
import sys
import pandas as pd
import numpy as np
from collections import Counter
from Levenshtein import distance
from Levenshtein import ratio
from openai import OpenAI
from Parser import *
from config import *
from calculation import *
from Askllm import *

client = OpenAI(
    api_key="sk-HXJ9ubNKq2k13zlfTzr1xsL35CSzXeaAxkHKE0O6jOgYZ2GO",
    base_url="https://www.dmxapi.com/v1",
)

INPUT_TOKENS  =0
OUTPUT_TOKENS = 0

task_description = """
You are a domain modeling expert and are assigned with the task of domain modeling creation.
You objective is to create a textual based domain modeling given the program description.
There are steps involved in the process. Follow the instruction for your current step.
"""

def noun_analysis(problem_description):
    noun_analysis_prompt = """
    Identify all the nouns in the description which can potentially be the class name, attribute name, role name.
    Include as much as nouns as possible and do not care about their functions for now.
    """
    format_description = """
    only output nouns and separated by , do not include any other words or symbels in your generated text.
    """
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": task_description},
          {"role": "system", "content": problem_description},
          {"role": "system", "content": noun_analysis_prompt},
          {"role": "system", "content": format_description},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step1: noun_analysis, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)
    noun_list = generated_text.split(",")
    noun_list = [i.strip() for i in noun_list if (i != "" and i != "\n" and i != None)]

    return noun_list,used_tokens

def identify_classes(problem_description, nouns_list):
    identify_classes_prompt = """
    Identify classes from the nouns list extracted from the problem description above.
    A class is the description for a set of similar objects that have the same structure and behavior, i.e., its instances
    All objects with the same features and behavior are instances of one class.
    In general, something should be a class if it could have instances.
    In general, something should be an instance if it is clearly a single member of the set defined by a class.
    Keep in mind that some of the nouns may be attributes or roles of the identified classes.
    Choose proper names for classes according the the following rules:
    1. Noun
    2. Singular
    3. Not too general, not too specific – at the right level of abstraction
    4. Avoid software engineering terms (data, record, table, information)
    5. Conventions: first letter capitalized; camel case without spaces if needed

    Example class names:
    Hospital, Doctor, PartTimeEmployee

    Constraints:
    Create classes at the right level of abstraction.
    Not all nouns in the nouns list are classes, some of them may be attributes, role names, or even not needed for diagram.
    Do NOT include all the nouns list as classes. Evaluate if it is needed to be a class.
    ONLY generate classes that are necessary to develop the system.


    Example:
    Problem Description: This system helps the Java Valley police officers keep track of the cases they are assigned to do. Officers may be assigned to investigate particular crimes, which involves interviewing victims at their homes and entering notes in the PI system.
    Identified Class List: PISystem, PoliceStation, Case, PoliceOfficer, Victim, Crime, Note
    """
    format_description = """
    only output class names and separated by , do not include any other words or symbols in your generated text.
    """
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": f"Task Description: {task_description}"},
          {"role": "system", "content": f"Problem Description: {problem_description}"},
          {"role": "system", "content": f"Nouns list: {nouns_list}"},
          {"role": "system", "content": identify_classes_prompt},
          {"role": "system", "content": format_description},
          {"role": "system", "content": f"Identified Class List: \n"},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step2: identify_classes, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_list = generated_text.split(",")
    class_list = [i.strip() for i in class_list if (i != "" and i != "\n" and i != None)]

    return class_list,used_tokens


def identify_attributes(problem_description, class_list, nouns_list):
    identify_attribute_prompt = """
    Given the current identify class list and noun list for potential class, attributes, role names.
    Identify attributes for each class.
    An attribute is a simple piece of data with a name and primitative datatype: string, int, date, time, boolean, etc
    More complex data is NOT modeled as an attribute.
    Attribute exists only when the object of the class exists.
    Conventions: first letter lower case; camel case without spaces if needed

    Notes:
    For each class, evaluate if it can be represented by an attrbute inside another class. If so, remove the class and make it an attribute.
    Do not include the class if it is not necessary in the software system.
    """
    format_description = """
    Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
    For example:
    Person(string name, string address)
    only output class with attribute in () and separated by each line. do not include any other words or symbels in your generated text.
    """
    constraint = """
    You can overwrite the current class list if some classes are not necessary or should be attributes instead.
    Only generate attributes for the current classes.
    """
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": f"Task Description: {task_description}"},
          {"role": "system", "content": f"Problem Description: {problem_description}"},
          {"role": "system", "content": f"Class list: {class_list}"},
          {"role": "system", "content": f"Noun list: {nouns_list}"},
          {"role": "system", "content": identify_attribute_prompt},
          {"role": "system", "content": constraint},
          {"role": "system", "content": format_description},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step3: identify_attributes, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_attribute_list = generated_text.split("\n")
    class_attribute_list = [i.strip() for i in class_attribute_list if (i != "" and i != "\n" and i != None)]

    return class_attribute_list,used_tokens

def identify_enumeration_classes(problem_description, class_list, nouns_list):
    identify_classes_prompt = """
    Identify enumeration classes from the current class.
    An enumeration class specifies a predefined list of choices, known as literals.
    Use the keyword "enum" to represent the class is an enumeration class
    For each literal, it consists of mainly one word, without any type.
    Do not show association with an enumeration, indicate as type of attribute.
    Often, the enumeration is defined as a single class, but is referenced for each of the class that needs the enumeration.
    In this case, it is used as an attribute, with the lower case of class name as attribute name and class name as attribute type.

    for example:
    enum PatronType(Student, Adult, Senior)
    LibyaryPatron(PatronType patronType)
    """

    format_description = """
    Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
    Follow the format for each enumeration class with its literal: enum ClassName(Literal1, Literal2)
    For example:
    Person(string name, string address)
    enum Cake(WeddingCake, BirthdayCake)

    only output class with attribute in () and separated by each line. do not include any other words or symbels in your generated text.
    """

    constraint = """
    Only add the keyword enum if the original class should be an enumeration class
    Output all classes, including enumeration class and normal class
    """

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": task_description},
          {"role": "system", "content": problem_description},
          {"role": "system", "content": f"Class list: {class_list}"},
          {"role": "system", "content": f"Nouns list: {nouns_list}"},
          {"role": "system", "content": identify_classes_prompt},
          {"role": "system", "content": constraint},
          {"role": "system", "content": format_description},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step4: identify_enumeration_classes, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_list = generated_text.split("\n")
    class_list = [i.strip() for i in class_list if (i != "" and i != "\n" and i != None)]

    return class_list, used_tokens

def identify_abstract_classes(problem_description, class_list, nouns_list):
    identify_classes_prompt = """
    Identify abstract classes from the current class.
    Abstract classes cannot be instantiated, i.e. the object of such class cannot be created directly using the new keyword

    We can treat an abstract class as a superclass and extend it:
    Structure and behavior specified for a superclass also applies to the subclass
    Subclass inherits from superclass

    for example:
    abstract Cake(int price)
    BirthdayCake(int numberOfCandles)
    WeddingCake(int numberOfTiers)

    for example:
    abstract Account(int balance, date openedDate, int creditorOverdraftLimit)
    MortgageAccount(int collateralValue)
    SavingsAccount()
    checkingAccount(int highestCheckNumber)

    use the keyword "abstract" to represent the class is abstract
    """

    format_description = """
    Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
    For example:
    Person(string name, string address)
    abstract Account(int amount)
    only output class with attribute in () and separated by each line. do not include any other words or symbels in your generated text.
    """

    constraint = """
    Only add the keyword abstract if the original class should be an abstract class
    You can adjust the attributes within the subclass if the super class already contain the attribute
    Output all classes, including abstract classes, normal classes, and enumeration class
    """

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": task_description},
          {"role": "system", "content": problem_description},
          {"role": "system", "content": f"Class list: {class_list}"},
          {"role": "system", "content": f"Nouns list: {nouns_list}"},
          {"role": "system", "content": identify_classes_prompt},
          {"role": "system", "content": constraint},
          {"role": "system", "content": format_description},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step5: identify_abstract_classes, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_list = generated_text.split("\n")
    class_list = [i.strip() for i in class_list if (i != "" and i != "\n" and i != None)]

    return class_list, used_tokens
def get_partial_model(problem_description):
  used_tokens =[0,0,0,0,0]
  # step 1. Noun analysis
  noun_list, used_tokens[0] = noun_analysis(problem_description)

  # step 2. Identify classes and choose propoer names for the class
  class_list,used_tokens[1] = identify_classes(problem_description, noun_list)

  # step 3. Identify Attributes for each class
  class_attribute_list,used_tokens[2] = identify_attributes(problem_description, class_list, noun_list)

  # step 4. Identify Enumeration class
  class_attribute_enum_list,used_tokens[3] = identify_enumeration_classes(problem_description, class_attribute_list, noun_list)

  # step 5. Identify abstract class
  partial_model,used_tokens[4] = identify_abstract_classes(problem_description, class_attribute_enum_list, noun_list)

  sum_tokens = sum(used_tokens)
  print(f"### get_partial_model ### Total tokens used: {sum_tokens}")
  
  return partial_model,sum_tokens

def identify_player_role_pattern_experiment(description, class_attribute):
    identify_classes_prompt = """
    identify the Player-Role pattern within the current classes
    for the classes Student, FullTimeStudent, PartTimeStudent, with the normal super class and subclass relationship,
    an instance of the Student cannot switch from FullTimeStudent to PartTimeStudent, as the instance cannot change type.
    So we need the player role pattern as following:

    Student(string name, string id)
    abstract AttendanceRole()
    FullTimeStudent(int fullTimeCredit) inherit AttendenceRole()
    PartTimeStudent(int partTimeCredit) inherit AttendenceRole()

    Here are more examples:

    Example 1. Within the school system, the student has two roles, graduate student and undergraduate student.
    The student can be a undergrad student at some point, and then switch to the role of graduate student.
    The student class saved information shared by both roles and is associated to the LevelRole.
    Both GraduateStudent and UndergradStudent inherit from the LevelRole class.

    Student(string name)
    abstract LevelRole()
    GraduateStudent(float graduateGpa) inherit LevelRole()
    UndergradStudentfloat undergradGpa inherit LevelRole()

    Example 2. Within the company system, each person has two roles, employee and manager.
    The Person can be an employee at some point, and then switch to the manager role later.

    Person(string name, string email, string address)
    abstract PersonRole()
    Employee(string employeeID) inherit PersonRole()
    Manager(string title) inherit PersonRole()

    Example 3. Within the system, each user has two roles, administrator and player.
    The user can be an administrator at some point, and then switch to the player role, or each user can have two roles at the same time.

    User(string userEmail, string userId)
    abstract UserRole()
    Administrator(string adminName, string adminPassword) inherit UserRole()
    Player(string playAccountName) inherit UserRole()

    Example 4. Within the conference system, each user has three roles: author, program chair, and reviewer.
    The user can have 1-3 roles at the same time. For example, the user can publish a paper as the author, work as a program chair, and review other papers at the same time.

    User(string username, string password)
    abstract UserRole()
    AuthorRole(string authorId) inherit UserRole()
    ProgramChairRole(string programCategory) inherit UserRole()
    ReviewerRole(string averageRating) inherit UserRole()

    Example 5. Within the company system, each person has at most 2 roles: a client, and an employee.
    The person can switch from a client to an employee, or keep two roles at the same time.
    For the role of employee, there are two types, lawer and low clerk. Both roles inherit from the employee role.

    Person(string name, string email)
    abstract UserRole()
    Client(string slientId) inherit UserRole()
    abstract Employee(string employeeId) inherit UserRole()
    Lawyer(string layerCategory) inherit Employee()
    LawClerk(string level) inherit Employee()
    """

    constraint = """
    Only output the classes that are within the Player-Role pattern.
    Do NOT include other classes.
    You may add new classes only if they are part of the Player-Role pattern.
    If there isn't any Player-Role pattern, simply say "No Player-Role pattern identified"
    Only generate Player-Role pattern within the description. Do not repeat the example.
    Ony use the Player-Role pattern when necessary according to the description.
    """

    format_description = """
    Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
    Use the keyword "abstract" to represent the abstract class
    Use the keyword "inherit" to represent the subclass inherit attributes and relations from the super class
    """

    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": task_description},
          {"role": "system", "content": description},
          {"role": "system", "content": f"Class and attribute list: {class_attribute}"},
          {"role": "system", "content": identify_classes_prompt},
          {"role": "system", "content": constraint},
          {"role": "system", "content": format_description},
      ],
      temperature=0.7,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step6: identify_player_role_pattern_experiment, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_list = generated_text.split("\n")
    class_list = [i.strip() for i in class_list if (i != "" and i != "\n" and i != None)]

    return class_list, used_tokens

def summarize_player_role_pattern(description, result_list, class_attribute):
  summarize_prompt = """Identify the Player-Role pattern from the descriotion provided with reference to five result list.
  Output the mostly like Player-Role pattern according to 5 result you have.
  You do not need to included everything from the 5 result you have, only include the classes you think it is correct.
  Combine the 5 result you have and make the final solution that make sense to you.
  Do not output other classes that are not included in the Player-Role pattern.
  If there isn't any Player-Role pattern, simply say "No Player-Role pattern identified"
  """

  format_description = """
  Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
  Use the keyword "abstract" to represent the abstract class
  Use the keyword "inherit" to represent the subclass inherit attributes and relations from the super class.
  for example:
  Person(string name, string email, string address)
  abstract PersonRole()
  Employee(string employeeID) inherit PersonRole()
  Manager(string title) inherit PersonRole()
  """

  response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
      {"role": "system", "content": f"Task description: {task_description}"},
      {"role": "system", "content": summarize_prompt},
      {"role": "system", "content": f"Description: {description}"},
      {"role": "system", "content": f"5 solution list {result_list}"},
      {"role": "system", "content": f"Class and attribute list: {class_attribute}"},
      {"role": "system", "content": f"Format description: {format_description}"},
  ],
  temperature=0,
  )
  generated_text = response.choices[0].message.content
  used_tokens = response.usage.total_tokens
  global INPUT_TOKENS
  INPUT_TOKENS += response.usage.prompt_tokens
  global OUTPUT_TOKENS
  OUTPUT_TOKENS += response.usage.completion_tokens
  print("step7: summarize_player_role_pattern, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
  print(generated_text)
  return generated_text,used_tokens
def class_integrater(description, generated_class_list, player_role_pattern):
  checker_prompt = """Using the current generated classes and identified player role pattern,
  combine the two versions and generate the final version of classes.

  Do the following things:
  1. analysis the generated classes to see if they are needed.
  Some generated classes may not be the right level of abstraction.
  Drop the classes if there are not necessary to describe the system.
  2. evaluate the player-role pattern to see if they are necessary.
  Not all system need the player-role pattern.
  Since player-role pattern can be complex in implementation, only use it if it is necessary.
  if the abstract classes and their subclasses are necessary, do not use player-role pattern.
  3. Combine the two version and make a solution that is consistent with both versions.
  Do not have duplicate classes in the final solution
  """

  format_description = """
  Do not generate other phrases besides the classes.
  Do not generate number for the classes.
  Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
  Use the keyword "abstract" to represent the abstract class
  Use the keyword "inherit" to represent the subclass inherit attributes and relations from the super class.
  for example:
  Person(string name, string email, string address)
  abstract PersonRole()
  Employee(string employeeID) inherit PersonRole()
  Manager(string title) inherit PersonRole()
  """

  response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
      {"role": "system", "content": f"Task description: {task_description}"},
      {"role": "system", "content": checker_prompt},
      {"role": "system", "content": f"Description: {description}"},
      {"role": "system", "content": f"Generated classes list {generated_class_list}"},
      {"role": "system", "content": f"Player-role pattern: {player_role_pattern}"},
      {"role": "system", "content": f"Format description: {format_description}"},
      {"role": "system", "content": f"Integrated classes with attributes: \n"},
  ],
  temperature=0,
  )
  generated_text = response.choices[0].message.content
  used_tokens = response.usage.total_tokens
  global INPUT_TOKENS
  INPUT_TOKENS += response.usage.prompt_tokens
  global OUTPUT_TOKENS
  OUTPUT_TOKENS += response.usage.completion_tokens
  print("step8: class_integrater, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
  print(generated_text)
  class_list = generated_text.split("\n")
  class_list = [i.strip() for i in class_list if (i != "" and i != "\n" and i != None)]

  return class_list,used_tokens




def checker(problem_description, class_list):
    checker_prompt = """
    Given the class list for the problem description, write comment for each class with its attribute.
    Evaluate if it is at the correct level of abstraction to be included in the software system.
    Many classes may not be needed and may not be necessary, example cases:
    - if class A is too detailed to be included in the system, consider removing it.
    - if class A does not contain any attributes or only contains 1 attribute, consider moving the attribute of class A to another class and removing class A
    - For the enumeration class, evaluate if it should be captured by an attribute and if its literals are necessary
    - For the subclasses, evaluate if they are necessary to be present in the system.

    You can write general comments and comments to each class, evaluate if the class is necessary. If not, provide a solution to change it.
    """
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
          {"role": "system", "content": f"Task Description: {task_description}"},
          {"role": "system", "content": f"Problem Description: {problem_description}"},
          {"role": "system", "content": f"Class list: {class_list}"},
          {"role": "system", "content": checker_prompt},
          {"role": "system", "content": f"Generated comments: \n"},
      ],
      temperature=0,
    )
    generated_text = response.choices[0].message.content
    used_tokens = response.usage.total_tokens
    global INPUT_TOKENS
    INPUT_TOKENS += response.usage.prompt_tokens
    global OUTPUT_TOKENS
    OUTPUT_TOKENS += response.usage.completion_tokens
    print("step9: checker, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
    print(generated_text)

    class_attribute_list = generated_text.split("\n")
    class_attribute_list = [i for i in class_attribute_list if (i != "" and i != "\n" and i != None)]

    return class_attribute_list,used_tokens







def identify_relationship(description, class_list, player_role):
  relationship_prompt = """
  Identify relationships between classes. There are three types of relationships:

  1. Composition with the keyword "contain"
  example format: mul1 Class1 contain mul2 Class2
  Class1 and Class2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]
  there might be multiple compositions
  In a typical domain model, there is usually a "system class" that contain most of the classes within the system
  For example:
  1 SchoolSystem contain 0..* UserRole
  1 SchoolSystem contain 0..* User
  1 SchoolSystem contain 0..* Course
  1 SchoolSystem contain 0..* Registration
  1 SchoolSystem contain 0..* StudentProfile

  2. Inheritance with the keyword "inherit"
  example format: Class1 inherit Class2
  Class1 and Class2 are classes above. there might be multiple inheritance
  Consider the inheritance relationship within the Player-Role pattern
  For example:
  Student inherit PersonRole
  Professor inherit PersonRole

  3. Association with the keyword "associate"
  example format: mul1 Class1 associate mul2 Class2
  Class1 and Class2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]
  there might be multiple associations
  For example:
  0..* Student associate 0..5 Registration
  1 Student associate 0..1 StudentProfile

  Note:
  1. Use the classes in the given generated classes list, generate the classes and their relationships.
  2. Only add the system class if the existing class diagram misses the system class.
  3. Do NOT change existing classes or add other classes besides the system class.
  4. In most of the cases, there is only 1 relationship within the same two classes.
  """

  format_description = """
  Generate the complete class diagram according to the class list using the following format:

  Classes:
  <put the origianl input class list here, do not modify existing classes>

  Relatipnships:
  Composition:
  <put composition relationship here using the format: mul1 Class1 contain mul2 Class2>
  Inheritance:
  <put inheritance relationship here using the format: Class1 inherit Class2>
  Association:
  <put association relationship here using the format: mul1 Class1 associate mul2 Class2>

  Make sure the generated text can be processed by text.split("\n") and then [text.strip()] into a list of processed classes and relationships
  """

  response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
      {"role": "system", "content": relationship_prompt},
      {"role": "system", "content": f"Description: {description}"},
      {"role": "system", "content": f"Generated classes list: {class_list}"},
      {"role": "system", "content": f"Player-role pattern: {player_role}"},
      {"role": "system", "content": f"Format description: {format_description}"},
  ],
  temperature=0,
  )
  generated_text = response.choices[0].message.content
  used_tokens = response.usage.total_tokens
  global INPUT_TOKENS
  INPUT_TOKENS += response.usage.prompt_tokens
  global OUTPUT_TOKENS
  OUTPUT_TOKENS += response.usage.completion_tokens
  print("step10: identify_relationship, tokens: ",used_tokens,response.usage.prompt_tokens,response.usage.completion_tokens)
  print(generated_text)

#   complete_class_diagram = generated_text.split("\n")
#   complete_class_diagram = [i.strip() for i in complete_class_diagram if (i != "" and i != "\n" and i != None)]

  return generated_text,used_tokens

def integrate_feedback_from_checker(problem_description, class_attribute_list, checker_comment):
  integrate_prompt = """
  integrate the feedback given by the checker to finish the class diagram according to the problem description.
  """

  format_description = """
  Do not generate other phrases besides the classes.
  Do not generate number for the classes.
  Follow the format for each class with its attribute: ClassName(type attributeName1, type attributeName2)
  For example:
  Person(string name, string address)
  only output class with attribute in () and separated by each line. do not include any other words or symbels in your generated text.
  """

  response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=[
      {"role": "system", "content": f"Task Description: {task_description}"},
      {"role": "system", "content": f"Problem Description: {problem_description}"},
      {"role": "system", "content": f"Class list: {class_attribute_list}"},
      {"role": "system", "content": f"Feedback from checker: {checker_comment}"},
      {"role": "system", "content": integrate_prompt},
      {"role": "system", "content": format_description},
      {"role": "system", "content": "Revised class diagram: "},
  ],
  temperature=0,
  )
  generated_text = response.choices[0].message.content
  used_tokens = response.usage.total_tokens
  global INPUT_TOKENS
  INPUT_TOKENS += response.usage.prompt_tokens
  global OUTPUT_TOKENS
  OUTPUT_TOKENS += response.usage.completion_tokens
  print(  "step11: integrate_feedback_from_checker, tokens: ",used_tokens)
  print(generated_text)

  class_attribute_list = generated_text.split("\n")
  class_attribute_list = [i for i in class_attribute_list if (i != "" and i != "\n" and i != None)]

  return class_attribute_list,used_tokens

def domain_model_generation(problem_description):
  used_tokens = [0]*7
  # step 1 identify classes and attributes
  partial_model,used_tokens[0] = get_partial_model(problem_description)

  # step 2 identify the player-role pattern
  iteration_list = []
  for i in range(1):
    player_role_pattern,used_token = identify_player_role_pattern_experiment(problem_description, partial_model)
    iteration_list.append(player_role_pattern)
    used_tokens[1] += used_token

  player_role_pattern,used_tokens[2] = summarize_player_role_pattern(problem_description, iteration_list, partial_model)

  completed_class_diagram ,used_tokens[3]= class_integrater(problem_description, partial_model, player_role_pattern)

  # step 3 self-reflection
  comment,used_tokens[4] = checker(problem_description, completed_class_diagram)
  revised_result ,used_tokens[5]= integrate_feedback_from_checker(problem_description, completed_class_diagram, comment)

  # step 4 identify relationships
  final_result,used_tokens[6] = identify_relationship(problem_description, revised_result, player_role_pattern)
  sum_tokens = sum(used_tokens)
  print(f"### domain_model_generation ### Total tokens used: {sum_tokens},{INPUT_TOKENS},{OUTPUT_TOKENS}")
  return final_result,sum_tokens

def remove_duplicate_lines(text):
    # print(text)
    # text = '\n'.join(re.findall(r'```?(.*?)```?', text, flags=re.DOTALL))

    lines = text.split('\n')
    
    seen = {}
    for line in lines:
        if line in seen:
            seen[line] += 1
        else:
            seen[line] = 1
    
    unique_lines = [line for line in seen.keys()]
    
    return '\n'.join(unique_lines)



def main_association_relationship(f_output_file,AI_answer):
    AI_answer = AI_answer.partition("Relationships")[2]
    print(f'AI_answer(association):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    # AI_answer = clean_text(AI_answer)
    generated_relationship_parser = RelationshipParser()
    generated_relationships_list = []
    
    # Remove_decuplicates
    AI_answer = remove_duplicate_lines(AI_answer)

    print(f'AI_answer_after_cut(association):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    for i in AI_answer.split('\n'):
        if i == '':
            continue
        generated_relationships = generated_relationship_parser.parse(i)
        if generated_relationships is None:
                print(f'(association) Not parsed successfully:{i}',file=f_output_file)
                continue
        generated_relationships_list.append(generated_relationships)

    return  AI_answer




def main_inherit_relationship(f_output_file,AI_answer):

    AI_answer=AI_answer.partition("Relationships")[2]
    print(f'AI_answer(inheritance):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    # AI_answer = clean_text(AI_answer)
    generated_relationship_parser = RelationshipParser()
    generated_relationships_list = []
    # Remove Duplicates
    AI_answer = remove_duplicate_lines(AI_answer)
    print(f'AI_answer_after_cut(inheritance):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    for i in AI_answer.split('\n'):
        if i == '':
            continue
        generated_relationships = generated_relationship_parser.parse(i)
        if generated_relationships is None:
                print(f'(inheritance) Not parsed successfully:{i}',file=f_output_file)
                continue
        generated_relationships_list.append(generated_relationships)

    return AI_answer





def lab1_main_base(file_path):
    temperature = 0.7
    initial_path =f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
    path = f"{initial_path}/test"
    os.chdir(path)
    new_folder_all = str(time.time())+'-lab1-baseline-llm'+str(running_params['llm'])+'-'+str(running_params['cycle'])+'cycle-iliteral'
    os.makedirs(new_folder_all)
    os.chdir(new_folder_all)
    cycle = running_params['cycle']
    oracle_dataset = pd.read_csv(file_path,encoding='latin1')

    # Read Oracle models
    name_list = oracle_dataset['Name']
    system_count = len(name_list)
    description_list = oracle_dataset['Description']
    oracle_classes_list = oracle_dataset['Classes']
    oracle_relationships_list = oracle_dataset['Associations']
    
    # "all_score_file (a)": store all system's final score
    all_score_file = f'{path}/{new_folder_all}/base_all_score.csv' 
    a = open(all_score_file,"w",encoding='UTF-8')
    print(f'system_name,cycle,used_tokens,class_precision,class_recall,class_f1,cls_f2,attribute_precision,attribute_recall,attribute_f1,atr_f2,rela_precision,rela_recall,rela_f1,rel_f2,association_precision,association_recall,association_f1,aso_f2,inheritance_precision,inheritance_recall,inheritance_f1,inhe_f2,Class match,Class generate,Class oracle,Attribute match,Attribute generate,Attribute oracle,Association match,Association generate,Association oracle,Inheritance match,Inheritance generate,Inheritance oracle ',file=a)
    
    # 'prediction_score_file (ps)': store each system's every cycle result
    prediction_score_file = f'{path}/{new_folder_all}/base_each_ex_score.csv' 
    ps=open(prediction_score_file,"w",encoding='UTF-8')
    print(f'system_name,cycle,used_tokens,class_precision,class_recall,class_f1,cls_f2,attribute_precision,attribute_recall,attribute_f1,atr_f2,rela_precision,rela_recall,rela_f1,rel_f2,association_precision,association_recall,association_f1,aso_f2,inheritance_precision,inheritance_recall,inheritance_f1,inhe_f2,Class match,Class generate,Class oracle,Attribute match,Attribute generate,Attribute oracle,Association match,Association generate,Association oracle,Inheritance match,Inheritance generate,Inheritance oracle ',file=ps)
    
    overall_sum_result = [0] *33
    sign = 0
    sys_number = 0
    

    # 方法二的计算initial
    overall_accumulators = [0]*13  # cls,atr,asso,inhe, [gen,mat,ora]
        
    overall_gen_relas_count,overall_match_relas_count,overall_oracle_relas_count=0,0,0

    for name,description,oracle_classes,oracle_relationships in zip(name_list,description_list,oracle_classes_list,oracle_relationships_list):
        # generate prompt 
        # base_prompt_list = generate_baseline_prompt(name,description)
        # message = generate_prompt_base_zero_shot(description)
        # message = generate_prompt_base_one_shot_H2S(description)
        # message = generate_prompt_base_CoT(description)
        # message = generate_prompt_base_one_shot(description)

        # prepare output file
        sign+=1
        output_file = f'{path}/{new_folder_all}/{name}.txt'
        f_output_file = open(output_file,'w',encoding='UTF-8')

        # prepare map_file to store the map result
        map_file = f"{initial_path}\map_file\dataset_1\{name}.json"
        if not os.path.exists(map_file):
            empty_data = {
                "mapMatched": {},
                "mapUnmatched": {}
            }
            with open(map_file, 'w') as f:
                json.dump(empty_data, f, indent=4)


        # prepare oracle model
        oracle_model_text = oracle_classes + "\nRelationships:\n"+ oracle_relationships
        o_file_parser = FileParser()
        model_oracle = o_file_parser.parseLines(oracle_model_text)  # Returns an instance of ModelDef

        # prepare model_gen to store the generated model
        sum_test_result = [0]*33
        oracle_classes,oracle_relationships = model_oracle.get_all_classes(),model_oracle.get_all_relationships()    
        
        accumulators = [0]*13  # cls,atr,asso,inhe, [gen,mat,ora]
        
        gen_relas_count,match_relas_count,oracle_relas_count=0,0,0

        
        sys_number+=1
        
        for c in range(1,cycle+1):
            print2file_List = []
            # Base_AI_answer,used_tokens = ask_llm(running_params['llm'],message,temperature,used_tokens=0)
            Base_AI_answer,used_tokens = domain_model_generation(description)
            print(Base_AI_answer)
            print(f'-{sign}/{system_count} system--{c}/{cycle} cycle--{name} Prediction have done!')

            print2file_List.append(f'{"-"*60}\n---------------------{c}/{cycle}------{name}:\n{"-"*60}')
            print2file_List.append(f'AI:\n{Base_AI_answer}\n')
            Base_AI_answer = remove_duplicate_lines(Base_AI_answer)
            
            # parser AI answer
            g_file_parser = FileParser()
            model_gen = g_file_parser.parseLines(Base_AI_answer)
            print2file_List.append(f"{'-'*60}\n(Baseline) Structure Model_Gen:\n Classes:")

            # print2file(f"(Baseline) Structure Model_Gen:\n Classes:",file=f_output_file)
            for cls in model_gen.get_all_classes():
                print2file_List.append(str(cls))
            print2file_List.append("Relationships:")
            for rel in model_gen.get_all_relationships():
                print2file_List.append(str(rel))

            # Match phase: match classes, attributes, relationships 
            Ma = Matcher(map_file)
            matched_classes_name, matched_classes =Ma.matchClasses(model_gen,model_oracle)
            matched_relationships = Ma.matchRelationships(model_gen,model_oracle,matched_classes_name)
            matched_attributes_name, matched_attributes = Ma.matchAttributes(model_gen,model_oracle,matched_classes)
            Ma.update_map()
            
            print2file_List.append(f'{"-"*80}\n--{c}/{cycle}--Classes and attributes matching process:')
            print2file_List.append(f'-Classes:')
            for cls in matched_classes.keys():
                print2file_List.append(f" '{cls.getName()}({cls.getKind()})'\t-\t'{matched_classes[cls].getName()}({matched_classes[cls].getKind()})'")
            print2file_List.append(f'-Attributes:')
            for attr in matched_attributes_name.keys():
                print2file_List.append(f" '{attr}'\t-\t'{matched_attributes_name[attr]}'")
            print2file_List.append(f'-Relationships:')
            for rel in matched_relationships.keys():
                print2file_List.append(f" '{rel}'\t-\t'{matched_relationships[rel]}'")
            print2file_List.append(f'{"-"*80}')

            final_output = [
                        f'{name}, matching result',
                        '-' * 80,  # Separator line
                        f'{"Metric":<20}{"Generate":<20}{"Match":<20}{"Oracle":<20}',  # Headers for columns
                        '-' * 80,  # Separator line
                        f'{"Classes":<20}{Ma.generated_classes_count:<20}{Ma.matched_classes_count:<20}{Ma.oracle_classes_count:<20}',  # Classes metrics
                        f'{"Attributes":<20}{Ma.generated_attributes_count:<20}{Ma.matched_attributes_count:<20}{Ma.oracle_attributes_count:<20}',  # Attributes metrics
                        f'{"Associations":<20}{Ma.gen_associations_count:<20}{Ma.matched_associations_count:<20}{Ma.oracle_associations_count:<20}',  # Associations metrics
                        f'{"Inheritances":<20}{Ma.gen_inheritances_count:<20}{Ma.matched_inheritances_count:<20}{Ma.oracle_inheritances_count:<20}',  # Inheritances metrics
                        '-' * 80,  # Separator line
                        ]
            print2file_List.extend(final_output)

            # Write output to the file
            print("\n".join(print2file_List),file=f_output_file)

            # method 1: count each pre/recall/f1, count average            
            sum_test_result = print_metrics_1(Ma,ps,name,c,sum_test_result,used_tokens)
            

            # method 2 : sum all cycle results, average gen/matched/oracle number, then count metric pre/reecall/f1/f2
            
            accumulators,gen_relas_count,match_relas_count,oracle_relas_count = print_metrics_2(Ma,ps,name,c,accumulators,gen_relas_count,match_relas_count,oracle_relas_count)
            overall_accumulators,overall_gen_relas_count,overall_match_relas_count,overall_oracle_relas_count = print_metrics_2(Ma,ps,name,c,overall_accumulators,overall_gen_relas_count,overall_match_relas_count,overall_oracle_relas_count)

        ave_final_count = list(map(lambda x: x / cycle, sum_test_result)) # ave_final_count: 每个系统的均值
        print(f'{name},method_1_final_average_score,'
                f'{ave_final_count[32]:3f},'
                f'{ave_final_count[0]:3f},{ave_final_count[1]:3f},{ave_final_count[2]:3f},'
                f'{ave_final_count[3]:3f},{ave_final_count[4]:3f},{ave_final_count[5]:3f},'
                f'{ave_final_count[6]:3f},{ave_final_count[7]:3f},{ave_final_count[8]:3f},'
                f'{ave_final_count[9]:3f},{ave_final_count[10]:3f},{ave_final_count[11]:3f},'
                f'{ave_final_count[12]:3f},{ave_final_count[13]:3f},{ave_final_count[14]:3f},'
                f'{ave_final_count[15]:3f},{ave_final_count[16]:3f},{ave_final_count[17]:3f},'
                f'{ave_final_count[18]:3f},{ave_final_count[19]:3f},{ave_final_count[20]:3f},'
                f'{ave_final_count[21]:3f},{ave_final_count[22]:3f},{ave_final_count[23]:3f},'
                f'{ave_final_count[24]:3f},{ave_final_count[25]:3f},{ave_final_count[26]:3f},'
                f'{ave_final_count[27]:3f},{ave_final_count[28]:3f},{ave_final_count[29]:3f},'
                f'{ave_final_count[30]:3f},{ave_final_count[31]:3f}',
                file=a)
        
        overall_sum_result = list(map(lambda x,y : x + y, ave_final_count, overall_sum_result)) # overall_sum_result: 所有系统的均值

        
        accumulators1sys = list(map(lambda x : x/cycle, accumulators))
        classes_precision, classes_recall, classes_f1, classes_f2 = count_metric( accumulators1sys[1],accumulators1sys[0], accumulators1sys[2])
        atr_precision, atr_recall, atr_f1, atr_f2 = count_metric_atr( accumulators1sys[4],accumulators1sys[3],accumulators1sys[12], accumulators1sys[5])
        inheritances_precision, inheritances_recall, inheritances_f1, inheritances_f2 = count_metric(accumulators1sys[10],accumulators1sys[9],  accumulators1sys[11])
        associations_precision, associations_recall, associations_f1, associations_f2 = count_metric( accumulators1sys[7],accumulators1sys[6], accumulators1sys[8])
        rel_precision, rela_recall,rela_f1,rela_f2=count_metric(gen_relas_count,match_relas_count,oracle_relas_count)
        # Prepare a formatted output string
        final_output = [
            f'{name}, avg-method2',
            '-' * 80,  # Separator line
            f'{"Metric":<20}{"Precision":<15}{"Recall":<15}{"F1":<15}{"F2":<15}',  # Headers for columns
            '-' * 80,  # Separator line
            f'{"Classes":<20}{classes_precision:.3f}          {classes_recall:.3f}          {classes_f1:.3f}          {classes_f2:.3f}',  # Classes metrics
            f'{"Attributes":<20}{atr_precision:.3f}          {atr_recall:.3f}          {atr_f1:.3f}          {atr_f2:.3f}',  # Attributes metrics
            f'{"Associations":<20}{associations_precision:.3f}          {associations_recall:.3f}          {associations_f1:.3f}          {associations_f2:.3f}',  # Associations metrics
            f'{"Inheritances":<20}{inheritances_precision:.3f}          {inheritances_recall:.3f}          {inheritances_f1:.3f}          {inheritances_f2:.3f}',  # Inheritances metrics
            '-' * 80,  # Separator line
        ]

        # Write output to the file
        for line in final_output:
            print(line, file=f_output_file)
        

        print(f'--{sys_number}/{system_count} system-{name}: All round have done!')
        time.sleep(0.5)
    
    
    overall_sum_result = list(map(lambda x : x/system_count, overall_sum_result)) # overall_sum_result: 所有系统的均值
    print(f'method_1, ave_score_allsys,'
          f'{overall_sum_result[32]:3f},'
                f'{overall_sum_result[0]:3f},{overall_sum_result[1]:3f},{overall_sum_result[2]:3f},'
                f'{overall_sum_result[3]:3f},{overall_sum_result[4]:3f},{overall_sum_result[5]:3f},'
                f'{overall_sum_result[6]:3f},{overall_sum_result[7]:3f},{overall_sum_result[8]:3f},'
                f'{overall_sum_result[9]:3f},{overall_sum_result[10]:3f},{overall_sum_result[11]:3f},'
                f'{overall_sum_result[12]:3f},{overall_sum_result[13]:3f},{overall_sum_result[14]:3f},'
                f'{overall_sum_result[15]:3f},{overall_sum_result[16]:3f},{overall_sum_result[17]:3f},'
                f'{overall_sum_result[18]:3f},{overall_sum_result[19]:3f},{overall_sum_result[20]:3f},'
                f'{overall_sum_result[21]:3f},{overall_sum_result[22]:3f},{overall_sum_result[23]:3f},'
                f'{overall_sum_result[24]:3f},{overall_sum_result[25]:3f},{overall_sum_result[26]:3f},'
                f'{overall_sum_result[27]:3f},{overall_sum_result[28]:3f},{overall_sum_result[29]:3f},'
                f'{overall_sum_result[30]:3f},{overall_sum_result[31]:3f}',
                file=a)
        
    classes_precision, classes_recall, classes_f1, classes_f2 = count_metric( overall_accumulators[1],overall_accumulators[0], overall_accumulators[2])
    atr_precision, atr_recall, atr_f1, atr_f2 = count_metric_atr( overall_accumulators[4],overall_accumulators[3],overall_accumulators[12], overall_accumulators[5])
    inheritances_precision, inheritances_recall, inheritances_f1, inheritances_f2 = count_metric(overall_accumulators[10],overall_accumulators[9],  overall_accumulators[11])
    associations_precision, associations_recall, associations_f1, associations_f2 = count_metric( overall_accumulators[7],overall_accumulators[6], overall_accumulators[8])
    rel_precision, rela_recall,rela_f1,rela_f2=count_metric(overall_gen_relas_count,overall_match_relas_count,overall_oracle_relas_count)
        
    print(f'method2,ave_score_allsys,' 
          f'{overall_sum_result[32]:3f},'
                f'{classes_precision:3f},{classes_recall:3f},{classes_f1:3f},{classes_f2:3f},'
                f'{atr_precision:3f},{atr_recall:3f},{atr_f1:3f},{atr_f2:3f},'
                f'{rel_precision:3f},{rela_recall:3f},{rela_f1:3f},{rela_f2:3f},'
                f'{associations_precision:3f},{associations_recall:3f},{associations_f1:3f},{associations_f2:3f},'
                f'{inheritances_precision:3f},{inheritances_recall:3f},{inheritances_f1:3f},{inheritances_f2:3f},'
                f'{overall_accumulators[0]:3f},{overall_accumulators[1]:3f},{overall_accumulators[2]:3f},'
                f'{overall_accumulators[3]:3f},{overall_accumulators[4]:3f},{overall_accumulators[5]:3f},'
                f'{overall_accumulators[6]:3f},{overall_accumulators[7]:3f},{overall_accumulators[8]:3f},'
                f'{overall_accumulators[9]:3f},{overall_accumulators[10]:3f},{overall_accumulators[11]:3f}',
                file=a)
    ps.close()
    a.close()  

    print('Prediction Finish!')



if __name__ == '__main__':
    for file_path in file['model_file']:
        lab1_main_base(file_path)