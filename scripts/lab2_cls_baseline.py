import json
import os
import csv
import time
import re
from typing import Tuple
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
from Matcher import Matcher
from Parser import *
from calculation import *
from config import *
from GenPrompt import *
from Askllm import ask_llm




def remove_duplicate_lines(text):
    lines = text.split('\n')
    
    seen = {}
    for line in lines:
        if line in seen:
            seen[line] += 1
        else:
            seen[line] = 1
    
    unique_lines = [line for line in seen.keys() if line]
    
    return '\n'.join(unique_lines)


def clean_text(text):
        text = re.sub('\`','',text)
        # text = re.sub(r'\*+', '', text)  
        return text.strip()  



def main_class_attribute(name,description,f_class_file,llm,used_tokens):
    PROMPT_MODEL_1_ROUND= """
    # Task1:
    Generate lists of enumerations, classes and attributes based on <Description>. Follow <Guidelines1> below step by step to ensure clarity and consistency.

    # Guidelines1:
    1. Identify the <relevant nouns> extracted from <Description>. You need to output only the distinct class names, avoiding overly broad, vague, or redundant terms.
    2. Identify <key objects/entities> from <relevant nouns>. You need to output them (e.g., <key object1/entity1>)
    3. Define <enumerations> based on the identified <key objects/entities>. You need to output them (e.g., <enum_name>(literal1, literal2)). Avoid creating enumerations like "DayOfTheWeek(monday, tuesday, wednesday, thursday, friday)", "PickupTimeRange(8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 2PM)". 
    4. Define <classes> based on the identified <key objects/entities>, ensuring appropriate abstraction levels. You need to output them (e.g., <class_name1>, <class_name2>).
    5. Define <attributes> for each class in <classes>. You need to output them(e.g., <class_name>(attribute1: attributeType1, attribute2: attributeType2)). If the class has no attribute, you need to output them (e.g., <class_name>()).
    6. Use clear and consistent naming conventions that reflect the role or function of the class within the system. Ensure that keep the class names consistent with the words mentioned in the system description.

    # Description:
    {}

    # Task2:
    Review all the enumerations, classes and attributes based on <Guidelines2> step by step. Output the final enumerations, classes and attributes using <Format> strictly.

    # Guidelines2:
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
    message = [{"role":"user","content":f"{PROMPT_MODEL_1_ROUND.format(description)}"}]
    AI_answer,used_tokens = ask_llm(llm,message,running_params['temperature_cls'],used_tokens)
    print(AI_answer)

    print(f'AI:\n{AI_answer}\n',file=f_class_file)
    message.append({"role":"assistant","content":f'{AI_answer}'})

        
    return AI_answer,used_tokens




def main_association_relationship(f_output_file,llm,generated_classes:List[ClassDef],name:str,description:str,used_tokens:int)->str:

    prompt_classes = []

    # prompt_classes = "\n".join(f"{i.getName()}()" for i in generated_classes)

    for i in generated_classes:
        prompt_classes.append(f"{i.getName()}({','.join(j.getType() + ' ' + j.getName() for j in i.getAttributes())})")
   
    prompt_classes = "\n".join(prompt_classes)


    # message = generate_relation_prompt(name,prompt_classes,description)
    message = generate_association_prompt_one_shot(name,prompt_classes,description)
    AI_answer,used_tokens = ask_llm(llm,message,running_params['temperature_association'],used_tokens)
    print(f'AI_answer(association):\n{AI_answer}\n{"-"*80}')
    print(f'AI_answer(association):\n{AI_answer}\n{"-"*80}',file = f_output_file)
    
    AI_answer = clean_text(AI_answer)
    # Cut Answer
    AI_answer1 = AI_answer.partition("Final Association Relationships:")[2].partition("# Final Composition Relationships:")[0] + AI_answer.partition("Final Composition Relationships:")[2]
    if not AI_answer1:
        AI_answer1 = AI_answer.partition("# Associations:")[2].partition("# Compositions:")[0] + AI_answer.partition("# Compositions:")[2]
    AI_answer = AI_answer1

    # Remove Duplicates
    AI_answer = remove_duplicate_lines(AI_answer)
    
    # print(f'AI_answer_after_cut(association):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    return AI_answer,used_tokens



def main_inherit_relationship(f_output_file,llm,generated_classes:List[ClassDef],name,description,used_tokens)->str:

    prompt_classes = []
    for i in generated_classes:
        prompt_classes.append(f"{i.getName()}({','.join(j.getType() + ' ' + j.getName() for j in i.getAttributes())})")
   
    prompt_classes = "\n".join(prompt_classes)
    # message = generate_inherit_relation_prompt(name,prompt_classes,description)
    message = generate_inheritance_prompt_one_shot(name,prompt_classes,description)
     
    AI_answer,used_tokens  = ask_llm(llm,message,running_params['tempetature_inheritance'],used_tokens)
    print(f'AI_answer(inheritance):\n{AI_answer}\n{"-"*80}')
    print(f'AI_answer(inheritance):\n{AI_answer}\n{"-"*80}',file = f_output_file)
    AI_answer = clean_text(AI_answer)
    AI_answer = AI_answer.partition("Final Inheritance Relationships:")[2]
    
    if 'Description' in AI_answer:
        AI_answer = AI_answer.partition('Description')[0]
    if 'Class' in AI_answer:
        AI_answer = AI_answer.partition("Class")[0]
    # Remove Duplicates
    AI_answer = remove_duplicate_lines(AI_answer)

    # print(f'AI_answer_after_cut(inheritance):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    return AI_answer,used_tokens





def lab1_main_ours(file):
    initial_path =f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
    path = f"{initial_path}\\test"
    os.chdir(path)
    new_folder_all = str(time.time())+'-lab2-1-round-llm'+str(running_params['llm'])+'-'+str(running_params['cycle'])+'cycle-dataset'
    os.makedirs(new_folder_all)  
    os.chdir(new_folder_all)
    cycle = running_params['cycle']
    oracle_dataset = pd.read_csv(file,encoding='UTF-8')


    name_list = oracle_dataset['Name']
    system_count = len(name_list)
    description_list = oracle_dataset['Description']
    oracle_classes_list = oracle_dataset['Classes']
    oracle_relationships_list = oracle_dataset['Associations']
    #####################
    # count
    # 'all_score.csv': 
    all_score_file = f'{path}/{new_folder_all}/ours_all_score.csv' 
    a = open(all_score_file,"w",encoding='UTF-8')
    # csv title write to 'all_score.csv'
    print(f'system_name,cycle,used_tokens,class_precision,class_recall,class_f1,cls_f2,attribute_precision,attribute_recall,attribute_f1,atr_f2,rela_precision,rela_recall,rela_f1,rel_f2,association_precision,association_recall,association_f1,aso_f2,inheritance_precision,inheritance_recall,inheritance_f1,inhe_f2,Class match,Class generate,Class oracle,Attribute match,Attribute generate,Attribute oracle,Association match,Association generate,Association oracle,Inheritance match,Inheritance generate,Inheritance oracle ',file=a)
    
    # 'each_cycle_score.csv': every cycle result
    prediction_score_file = f'{path}/{new_folder_all}/ours_each_cycle_score.csv'     
    ps=open(prediction_score_file,"w",encoding='UTF-8')
    print(f'system_name,cycle,used_tokens,class_precision,class_recall,class_f1,cls_f2,attribute_precision,attribute_recall,attribute_f1,atr_f2,rela_precision,rela_recall,rela_f1,rel_f2,association_precision,association_recall,association_f1,aso_f2,inheritance_precision,inheritance_recall,inheritance_f1,inhe_f2,Class match,Class generate,Class oracle,Attribute match,Attribute generate,Attribute oracle,Association match,Association generate,Association oracle,Inheritance match,Inheritance generate,Inheritance oracle ',file=ps)
    
    overall_sum_result = [0] *33
    sys_number = 0
    

    # 方法二的计算initial
    overall_accumulators = [0]*13  # cls,atr,asso,inhe, [gen,mat,ora]
        
    overall_gen_relas_count,overall_match_relas_count,overall_oracle_relas_count=0,0,0

    for name,description,oracle_classes,oracle_relationships in zip(name_list,description_list,oracle_classes_list,oracle_relationships_list):
        sys_number+=1
        output_file = f'{path}/{new_folder_all}/{name}.txt'
        f_output_file = open(output_file,'w',encoding='UTF-8')
        
        # prepare map_file
        map_file = f"{initial_path}\map_file\dataset_1\{name}.json"
        if not os.path.exists(map_file):
            empty_data = {
                "mapMatched": {},
                "mapUnmatched": {}
            }
            with open(map_file, 'w') as f:
                json.dump(empty_data, f, indent=4)

        
        # Prepocessing oracle 
        oracle_model_text = oracle_classes + "\nRelationships:\n"+ oracle_relationships
        o_file_parser = FileParser()
        model_oracle = o_file_parser.parseLines(oracle_model_text)  # Returns an instance of ModelDef

        # oracle_relationships_parser = RelationshipParser()
        # after_parse_oracle_relationships_list = []
        # for i in oracle_relationships.split('\n'):
        #     if i == '':
        #         continue
        #     i = i.strip()
        #     oracle_relationship = oracle_relationships_parser.parse(i)
        #     if oracle_relationship is None:
        #         print('Oracle中未被解析成对象的i:  ',i)
        #     after_parse_oracle_relationships_list.append(oracle_relationship)
            
            
        
        sum_test_result = [0]*33
        
        oracle_classes,oracle_relationships = model_oracle.get_all_classes(),model_oracle.get_all_relationships()
        
        
        accumulators = [0]*13  # cls,atr,asso,inhe, [gen,mat,ora]
        
        gen_relas_count,match_relas_count,oracle_relas_count=0,0,0

        for c in range(1,cycle+1):
            used_tokens = 0
            print(f'{"-"*60}\n---------------------{c}/{cycle}------{name}:\n{"-"*60}',file=f_output_file)

            classes_AI_answer,used_tokens = main_class_attribute(name,description,f_output_file,running_params['llm'],used_tokens)
            # classes_AI_answer,used_tokens = main_class_attribute_one_shot(name,description,f_output_file,running_params['llm'],used_tokens)
            classes_AI_answer = classes_AI_answer.partition('```')[2].partition('```')[0].strip()
            classes_AI_answer = clean_text(classes_AI_answer)
            class_gen_parse = FileParser()
            # ModelDef
            model_gen:ModelDef
            model_gen = class_gen_parse.parseLines(classes_AI_answer)

            
            
            Ma = Matcher(map_file)
            matched_classes_name = {}
            # matched_class = {}
            # unmatched_class = []
            generated_classes = model_gen.get_all_classes()
            # matched_classes_name, matched_classes =Ma.matchClasses(model_gen,model_oracle)
            
            # asso_AI_answer,used_tokens =main_association_relationship(f_output_file,running_params['llm'],filter(lambda x:x.kind== KIND_CLASS,generated_classes),name,description,used_tokens)
            # inheri_AI_answer,used_tokens = main_inherit_relationship(f_output_file,running_params['llm'],filter(lambda x:x.kind== KIND_CLASS,generated_classes),name,description,used_tokens)
            
            asso_AI_answer,used_tokens = """ """,0

            inheri_AI_answer,used_tokens = """ """,0
            # # message = generate_review_prompt(name,description,classes_AI_answer,asso_AI_answer,inheri_AI_answer)
            # print(message)
            # Rviewed_answer,used_tokens = ask_llm(running_params['llm'],message,0.7,used_tokens)
            # print(f'\n{"-"*80}\nAI_review:\n{Rviewed_answer}\n{"-"*80}')
            # print(f'\n{"-"*80}\nAI_review:\n{Rviewed_answer}\n{"-"*80}',file=f_output_file)
            print(f'-{sys_number}/{system_count} system--{c}/{cycle} cycle--{name} Prediction have done!')
            
            """
            rel_gen_text = "\n".join(["Relationships:\n",asso_AI_answer,inheri_AI_answer])
            rel_gen_text_parse = FileParser()
            model_gen2:ModelDef = rel_gen_text_parse.parseLines(rel_gen_text)
            model_gen.set_relationships(model_gen2.get_all_relationships())
            """
            # Rviewed_answer = re.findall(r'```\n.*?\n```', Rviewed_answer,re.S)[0].strip()
            # if '```' in Rviewed_answer:
            #     Rviewed_answer = Rviewed_answer.partition('```')[2].partition('```')[0].strip()
            # model_gen = class_gen_parse.parseLines(Rviewed_answer)
            print(f"Structure Model_Gen:\n Classes:",file=f_output_file)
            for cls in model_gen.get_all_classes():
                print(cls,file=f_output_file)
            # print("Relationships:",file=f_output_file)
            # for rel in model_gen.get_all_relationships():
            #     print(rel,file=f_output_file)
            
            matched_classes,matched_attributes_name,matched_relationships = Ma.matchModel(model_gen,model_oracle)
            # matched_classes_name, matched_classes = Ma.matchClasses(model_gen,model_oracle)
            # matched_relationships = Ma.matchRelationships(model_gen,model_oracle,matched_classes_name)
            # matched_attributes_name, matched_attributes = Ma.matchAttributes(model_gen,model_oracle,matched_classes)
            # Ma.update_map()
            
            print(f'{"-"*80}\n--{c}/{cycle}--Classes and attributes matching process:',file=f_output_file)
            
            # match result output
            print('-Class:',file=f_output_file)
            for cls in matched_classes.keys():
                print(f" '{cls.getName()}({cls.getKind()})' - '{matched_classes[cls].getName()}({matched_classes[cls].getKind()})'",file=f_output_file)
            for cls in generated_classes:
                if cls not in matched_classes.keys():
                    print(f" '{cls.getName()}({cls.getKind()})'")
            print('-Attributes:',file=f_output_file)
            for attr in matched_attributes_name.keys():
                print(f" '{attr}' - '{matched_attributes_name[attr]}'",file=f_output_file)
            # print('-Relationships:',file=f_output_file)
            # for rel in matched_relationships.keys():
            #     print(f" '{rel}' - '{matched_relationships[rel]}'",file=f_output_file)
            print('-' * 80,file=f_output_file)


            
            final_output = [
            f'{name}, matching result',
            '-' * 80,  # Separator line
            f'{"Metric":<20}{"Generate":<20}{"Match":<20}{"Oracle":<20}',  # Headers for columns
            '-' * 80,  # Separator line
            f'{"Classes":<20}{Ma.generated_classes_count:<20}{Ma.matched_classes_count:<20}{Ma.oracle_classes_count:<20}',  # Classes metrics
            f'{"Attributes":<20}{Ma.generated_attributes_count:<20}{Ma.matched_attributes_count:<20}{Ma.oracle_attributes_count:<20}',  # Attributes metrics
            # f'{"Associations":<20}{Ma.gen_associations_count:<20}{Ma.matched_associations_count:<20}{Ma.oracle_associations_count:<20}',  # Associations metrics
            # f'{"Inheritances":<20}{Ma.gen_inheritances_count:<20}{Ma.matched_inheritances_count:<20}{Ma.oracle_inheritances_count:<20}',  # Inheritances metrics
            '-' * 80,  # Separator line
            ]

            # # Write output to the file
            for line in final_output:
                print(line, file=f_output_file)

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
        # # Prepare a formatted output string
        # final_output = [
        #     f'{name}, avg-method2',
        #     '-' * 80,  # Separator line
        #     f'{"Metric":<20}{"Precision":<15}{"Recall":<15}{"F1":<15}{"F2":<15}',  # Headers for columns
        #     '-' * 80,  # Separator line
        #     f'{"Classes":<20}{classes_precision:.3f}          {classes_recall:.3f}          {classes_f1:.3f}          {classes_f2:.3f}',  # Classes metrics
        #     f'{"Attributes":<20}{atr_precision:.3f}          {atr_recall:.3f}          {atr_f1:.3f}          {atr_f2:.3f}',  # Attributes metrics
        #     f'{"Associations":<20}{associations_precision:.3f}          {associations_recall:.3f}          {associations_f1:.3f}          {associations_f2:.3f}',  # Associations metrics
        #     f'{"Inheritances":<20}{inheritances_precision:.3f}          {inheritances_recall:.3f}          {inheritances_f1:.3f}          {inheritances_f2:.3f}',  # Inheritances metrics
        #     '-' * 80,  # Separator line
        # ]

        # # # Write output to the file
        # for line in final_output:
        #     print(line, file=f_output_file)
        
        # print(f'{name},method2_final_average_score,'
        #         f'{classes_precision:3f},{classes_recall:3f},{classes_f1:3f},{classes_f2:3f},'
        #         f'{atr_precision:3f},{atr_recall:3f},{atr_f1:3f},{atr_f2:3f},'
        #         f'{rel_precision:3f},{rela_recall:3f},{rela_f1:3f},{rela_f2:3f},'
        #         f'{associations_precision:3f},{associations_recall:3f},{associations_f1:3f},{associations_f2:3f},'
        #         f'{inheritances_precision:3f},{inheritances_recall:3f},{inheritances_f1:3f},{inheritances_f2:3f},'
        #         f'{accumulators1sys[0]:3f},{accumulators1sys[1]:3f},{accumulators1sys[2]:3f},'
        #         f'{accumulators1sys[3]:3f},{accumulators1sys[4]:3f},{accumulators1sys[5]:3f},'
        #         f'{accumulators1sys[6]:3f},{accumulators1sys[7]:3f},{accumulators1sys[8]:3f},'
        #         f'{accumulators1sys[9]:3f},{accumulators1sys[10]:3f},{accumulators1sys[11]:3f}',
        #         file=a)
        

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
        lab1_main_ours(file_path)