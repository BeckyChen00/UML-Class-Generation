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


def print2file(content,file):
    print(content,file=file)
    print(content)



def main_class_attribute(name,description,f_class_file,llm):
    
    message = []
    prompt_list = generate_class_atr_prompt(name,description)
    prompt = prompt_list['prompt']   


    for i in range(0,len(prompt)):
        message.append(prompt[i])
        AI_answer = ask_llm(llm,message,running_params['temperature_cls'])
        if i :
            print2file(f'2nd conversation AI:\n{AI_answer}\n',file=f_class_file)
        else:
            print2file(f'1st conversation AI:\n{AI_answer}\n{"-"*80}',file=f_class_file)
        message.append({"role":"assistant","content":f'{AI_answer}'})

        
    return AI_answer




def main_association_relationship(f_output_file,llm,generated_classes:List[ClassDef],matched_name,name:str,description:str)->str:

    prompt_classes = []

    prompt_classes = "\n".join(f"{i.getName()}()" for i in generated_classes)
    relation_prompt_list = generate_relation_prompt(name,prompt_classes,description)

    message = relation_prompt_list['prompt']
    AI_answer = ask_llm(llm,message,running_params['temperature_association'])
    print2file(f'AI_answer(association):\n{AI_answer}\n{"-"*80}',file = f_output_file)
    
    AI_answer = clean_text(AI_answer)
    # Cut Answer
    AI_answer1 = AI_answer.partition("Final Association Relationships:")[2].partition("# Final Composition Relationships:")[0] + AI_answer.partition("Final Composition Relationships:")[2]
    if not AI_answer1:
        AI_answer1 = AI_answer.partition("# Associations:")[2].partition("# Compositions:")[0] + AI_answer.partition("# Compositions:")[2]
    AI_answer = AI_answer1

    # Remove Duplicates
    AI_answer = remove_duplicate_lines(AI_answer)
    
    # print(f'AI_answer_after_cut(association):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    return AI_answer




def main_inherit_relationship(f_output_file,llm,generated_classes:List[ClassDef],matched_name,name,description)->str:

    prompt_classes = []
    for i in generated_classes:
        prompt_classes.append(f"{i.getName()}({','.join(j.getType() + ' ' + j.getName() for j in i.getAttributes())})")
   
    prompt_classes = "\n".join(prompt_classes)
    inheritance_relation_prompt_list = generate_inherit_relation_prompt(name,prompt_classes,description)
    message = inheritance_relation_prompt_list['prompt']
    AI_answer = ask_llm(llm,message,running_params['tempetature_inheritance'])
    
    print2file(f'AI_answer(inheritance):\n{AI_answer}\n{"-"*80}',file = f_output_file)
    AI_answer = clean_text(AI_answer)
    AI_answer = AI_answer.partition("Final Inheritance Relationships:")[2]
    
    if 'Description' in AI_answer:
        AI_answer = AI_answer.partition('Description')[0]
    if 'Class' in AI_answer:
        AI_answer = AI_answer.partition("Class")[0]
    # Remove Duplicates
    AI_answer = remove_duplicate_lines(AI_answer)

    # print(f'AI_answer_after_cut(inheritance):\n{AI_answer}\n{"-"*20}',file = f_output_file)
    return AI_answer






def lab1_main_ours():
    initial_path =f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
    path = f"{initial_path}\\test"
    os.chdir(path)
    new_folder_all = str(time.time())+'-lab1-our-approach-llm'+str(running_params['llm'])+'-'+str(running_params['cycle'])+'cycle'
    os.makedirs(new_folder_all)  
    os.chdir(new_folder_all)
    cycle = running_params['cycle']
    oracle_dataset = pd.read_csv(file['model_file'],encoding='UTF-8')


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
    print(f'system,{cycle} times,Ave_class_precision,Ave_class_recall,Ave_class_f1,Ave_attribute_precision,Ave_attribute_recall,Ave_attribute_f1,Ave_rela_precision,Ave_rela_recall,Ave_rela_f1,Ave_association_precision,Ave_association_recall,Ave_association_f1,Ave_inheritance_precision,Ave_inheritance_recall,Ave_inheritance_f1,Ave_Class match,Ave_Class generate,Ave_Class oracle,Ave_Attribute match,Ave_Attribute generate,Ave_Attribute oracle,Ave_Association match,Ave_Association generate, Ave_Association oracle,Ave_Inheritance match,Ave_Inheritance generate, Ave_Inheritance oracle',file=a)

    # 'each_cycle_score.csv': every cycle result
    prediction_score_file = f'{path}/{new_folder_all}/ours_each_cycle_score.csv'     
    ps=open(prediction_score_file,"w",encoding='UTF-8')
    print(f'system_name,cycle,class_precision,class_recall,class_f1,cls_f2,attribute_precision,attribute_recall,attribute_f1,atr_f2,rela_precision,rela_recall,rela_f1,rel_f2,association_precision,association_recall,association_f1,aso_f2,inheritance_precision,inheritance_recall,inheritance_f1,inhe_f2,Class match,Class generate,Class oracle,Attribute match,Attribute generate,Attribute oracle,Association match,Association generate,Association oracle,Inheritance match,Inheritance generate,Inheritance oracle ',file=ps)
    overall_sum_result = [0] *32
    # count 

    #####################
    sign = 0
    
    cycle =running_params['cycle']
    for name,description,oracle_classes,oracle_relationships in zip(name_list,description_list,oracle_classes_list,oracle_relationships_list):
        sign+=1
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

        Ma = Matcher(map_file)
        
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
            
            
        
        sum_test_result = [0]*32

        
        
        oracle_classes,oracle_relationships = model_oracle.get_all_classes(),model_oracle.get_all_relationships()
        
        # 方法二的计算initial
        
        accumulators = [0]*13  # cls,atr,asso,inhe, [gen,mat,ora]
        
        gen_relas_count,match_relas_count,oracle_relas_count=0,0,0

        for c in range(1,cycle+1):
            
            print(f'{"-"*60}\n---------------------{c}/{cycle}------{name}:\n{"-"*60}',file=f_output_file)

            classes_AI_answer = main_class_attribute(name,description,f_output_file,running_params['llm'])
            
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
            matched_classes_name, matched_classes =Ma.matchClasses(model_gen,model_oracle)
            
            asso_AI_answer =main_association_relationship(f_output_file,running_params['llm'],filter(lambda x:x.kind== KIND_CLASS,generated_classes),matched_classes_name,name,description)
            inheri_AI_answer = main_inherit_relationship(f_output_file,running_params['llm'],filter(lambda x:x.kind== KIND_CLASS,generated_classes),matched_classes_name,name,description)
            # add review 代码
            message = generate_review_prompt(name,description,"\n".join(["class:\n\n",classes_AI_answer,"relationships:\n\n",asso_AI_answer,inheri_AI_answer]))
            print("ai4review:",ask_llm(1,message,0.7))

            print(f'-{sign}/{system_count} system--{c}/{cycle} cycle--{name} Prediction have done!')

            rel_gen_text = "\n".join(["Relationships",asso_AI_answer,inheri_AI_answer])
            rel_gen_text_parse = FileParser()
            model_gen2:ModelDef = rel_gen_text_parse.parseLines(rel_gen_text)
            model_gen.set_relationships(model_gen2.get_all_relationships())
            
            print2file(f"Structure Model_Gen:\n Classes:",file=f_output_file)
            for cls in model_gen.get_all_classes():
                print2file(cls,file=f_output_file)
            print2file("Relationships:",file=f_output_file)
            for rel in model_gen.get_all_relationships():
                print2file(rel,file=f_output_file)
            
            # matched_classes,matched_attributes_name,matched_relationships = MMatch.matchModel(model_gen,model_oracle)
            matched_relationships = Ma.matchRelationships(model_gen,model_oracle,matched_classes_name)
            matched_attributes_name, matched_attributes = Ma.matchAttributes(model_gen,model_oracle,matched_classes)

            Ma.update_map()

            print2file(f'{"-"*80}\n--{c}/{cycle}--Classes and attributes matching process:',file=f_output_file)
            
            # match result output
            print2file('-Class:',file=f_output_file)
            for cls in matched_classes.keys():
                print2file(f" '{cls.getName()}({cls.getKind()})' - '{matched_classes[cls].getName()}({matched_classes[cls].getKind()})'",file=f_output_file)
            print2file('-Attributes:',file=f_output_file)
            for attr in matched_attributes_name.keys():
                print2file(f" '{attr}' - '{matched_attributes_name[attr]}'",file=f_output_file)
            print2file('-Relationships:',file=f_output_file)
            for rel in matched_relationships.keys():
                print2file(f" '{rel}' - '{matched_relationships[rel]}'",file=f_output_file)
            print2file('-' * 80,file=f_output_file)
            #     f'matching result:\n Gen:Class:{Ma.generated_classes_count},Attr:{Ma.generated_attributes_count},Asso:{Ma.gen_associations_count},Inhe:{Ma.gen_inheritances_count}',
            #     f'\n Matched:Class:{Ma.matched_classes_count},Attr:{Ma.matched_attributes_count},Asso:{Ma.matched_associations_count},Inhe:{Ma.matched_inheritances_count}',
            #     f'\n Oracle:Class:{Ma.oracle_classes_count},Attr:{Ma.oracle_attributes_count},Asso:{Ma.oracle_associations_count},Inhe:{Ma.oracle_inheritances_count}',file=f_output_file)
            # print('matched finish',file=f_output_file)
            
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

            # Write output to the file
            for line in final_output:
                print2file(line, file=f_output_file)


            time.sleep(0.5)
            # method 1: count each pre/recall/f1, count average            
            sum_test_result = print_metrics_1(Ma,ps,name,c,sum_test_result)
            

            # method 2 : sum all cycle results, average gen/matched/oracle number, then count metric pre/reecall/f1/f2
            
            accumulators,gen_relas_count,match_relas_count,oracle_relas_count = print_metrics_2(Ma,ps,name,c,accumulators,gen_relas_count,match_relas_count,oracle_relas_count)


        ave_final_count = list(map(lambda x: x / cycle, sum_test_result))
        print(f'{name},method_1_final_average_score,'
                f'{ave_final_count[0]:4f},{ave_final_count[1]:4f},{ave_final_count[2]:4f},'
                f'{ave_final_count[3]:4f},{ave_final_count[4]:4f},{ave_final_count[5]:4f},'
                f'{ave_final_count[6]:4f},{ave_final_count[7]:4f},{ave_final_count[8]:4f},'
                f'{ave_final_count[9]:4f},{ave_final_count[10]:4f},{ave_final_count[11]:4f},'
                f'{ave_final_count[12]:4f},{ave_final_count[13]:4f},{ave_final_count[14]:4f},'
                f'{ave_final_count[15]:4f},{ave_final_count[16]:4f},{ave_final_count[17]:4f},'
                f'{ave_final_count[18]:4f},{ave_final_count[19]:4f},{ave_final_count[20]:4f},'
                f'{ave_final_count[21]:4f},{ave_final_count[22]:4f},{ave_final_count[23]:4f},'
                f'{ave_final_count[24]:4f},{ave_final_count[25]:4f},{ave_final_count[26]:4f},'
                f'{ave_final_count[27]:4f},{ave_final_count[28]:4f},{ave_final_count[29]:4f},'
                f'{ave_final_count[30]:4f},{ave_final_count[31]:4f}',
                file=ps)
        
        
        overall_sum_result = list(map(lambda x,y : x + y, ave_final_count, overall_sum_result))

        
        ave_accumulators = list(map(lambda x : x/cycle, accumulators))
        classes_precision, classes_recall, classes_f1, classes_f2 = count_metric( ave_accumulators[1],ave_accumulators[0], ave_accumulators[2])
        atr_precision, atr_recall, atr_f1, atr_f2 = count_metric_atr( ave_accumulators[4],ave_accumulators[3],ave_accumulators[12], ave_accumulators[5])
        inheritances_precision, inheritances_recall, inheritances_f1, inheritances_f2 = count_metric(ave_accumulators[10],ave_accumulators[9],  ave_accumulators[11])
        associations_precision, associations_recall, associations_f1, associations_f2 = count_metric( ave_accumulators[7],ave_accumulators[6], ave_accumulators[8])
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
        
        print(f'{name},method2_final_average_score,'
                f'{classes_precision}, {classes_recall}, {classes_f1}, {classes_f2},'
                f'{atr_precision}, {atr_recall}, {atr_f1}, {atr_f2},'
                f'{rel_precision}, {rela_recall}, {rela_f1}, {rela_f2},'
                f'{associations_precision}, {associations_recall}, {associations_f1}, {associations_f2},'
                f'{inheritances_precision}, {inheritances_recall}, {inheritances_f1}, {inheritances_f2},'
                f'{ave_accumulators[0]:4f},{ave_accumulators[1]:4f},{ave_accumulators[2]:4f},'
                f'{ave_accumulators[3]:4f},{ave_accumulators[4]:4f},{ave_accumulators[5]:4f},'
                f'{ave_accumulators[6]:4f},{ave_accumulators[7]:4f},{ave_accumulators[8]:4f},'
                f'{ave_accumulators[9]:4f},{ave_accumulators[10]:4f},{ave_accumulators[11]:4f}',
                file=ps)
        

        print(f'--{sign}/{system_count} system-{name}: All round have done!')
        time.sleep(0.5)
    

    print('Prediction Finish!')


if __name__ == '__main__':
    lab1_main_ours()