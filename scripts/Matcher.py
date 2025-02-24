import json
import queue
import threading
from structure import KIND_AGGREGATION, KIND_ASSOCIATION, KIND_INHERITANCE,ClassDef,AttributeDef, ModelDef,RelationshipDef
from typing import Dict,List,Tuple,Callable
from Levenshtein import ratio


class Matcher:
    matched_classes_count = 0
    matched_attributes_count = 0
    matched_attributes_count4recall = 0
    matched_associations_count = 0
    matched_inheritances_count = 0

    generated_classes_count = 0
    generated_attributes_count = 0
    gen_associations_count = 0
    gen_inheritances_count = 0

    oracle_classes_count = 0
    oracle_attributes_count = 0
    oracle_associations_count = 0
    oracle_inheritances_count = 0


    # these two mapMatched :
    #  mapMatched:key: matched_gen_cls_name, value:matched_oracle_cls_name
    #  mapUnmatched: key: unmatched_gen_cls_name, value: a list of unmatched_oracle_cls_names
    # when new a Matcher, this class will read this two maps, please code read_map?:
    mapMatched:Dict[str,str]
    mapUnmatched:Dict[str,List[str]]

    map_file:str=None

    def __init__(self,map_file:str):
        self.mapMatched={}
        self.mapUnmatched={}
        self.map_file=map_file
        self.read_map()

    def update_map(self):
        # write mapMatched and mapUnmatched into map_file by json
        map_data = {
            "mapMatched": self.mapMatched,
            "mapUnmatched": self.mapUnmatched
        }
        with open(self.map_file,'w') as f:
            json.dump(map_data,f,indent=4)
        print(f"//// Map has been successfully updated in {self.map_file}")
        

    def read_map(self ):
        """
        Read the mapMatched and unmatched from a Json file.
        {
            "mapMatched": {
                "ClassA": "ClassA_Oracle",
                "ClassB": "ClassB_Oracle"
            },
            "mapUnmatched": {
                "ClassC": ["ClassC_Oracle_1", "ClassC_Oracle_2"]
            }
        }

        """
        try:
            with open(self.map_file,'r') as f:
                data = json.load(f)
                self.mapMatched =data['mapMatched']
                self.mapUnmatched = data['mapUnmatched']
        except FileNotFoundError:
            print(f'Warning:{self.map_file} not found. Starting with empty maps')
        except json.JSONDecodeError:
            print(f"Error: {self.map_file} is not a valid JSON file.")
        except Exception as e:
            print(f"An error occurred while reading the map file: {e}")


    def isNameMatch(self,NameGen:str,NameOracle:str)-> bool:
        if ratio(NameGen.strip().lower(),NameOracle.strip().lower()) >= 0.9:
            return True


    def isClassJaccMatch(self,ClassGen:ClassDef,ClassOracle:ClassDef)->bool:
        cand=list(ClassOracle.attributes)
        matched = 0
        for attr in ClassGen.attributes:
            for i in range(len(cand)):
                if self.isNameMatch( attr.getName(), cand[i].getName()):
                    matched += 1
                    cand.pop(i)
                    break
        union = len(ClassGen.attributes) + len(ClassOracle.attributes) - matched
        if union:
            jacc = matched / (len(ClassGen.attributes) + len(ClassOracle.attributes) - matched)
        else:
            jacc = 0
        
        if jacc>=0.6:
            self.mapMatched[ClassGen.getName().strip()] = ClassOracle.getName().strip()
            return True
        else:
            return False


    # def timed_input(self,prompt, timeout):
    #     print(prompt, end='', flush=True)  # 打印提示信息，并确保立即刷新输出
    #     result = [None]  # 使用列表来封装结果，因为列表是可变的，可以在另一个线程中修改
        
    #     def input_thread():
    #         result[0] = input().strip()  # 读取用户输入并去除空白字符
        
    #     t = threading.Thread(target=input_thread)
    #     t.start()  # 启动输入线程
    #     t.join(timeout)  # 等待线程完成，最多等待timeout秒
        
    #     if t.is_alive():  # 如果线程仍然活着，说明超时了
    #         return 'N'  # 返回默认输入'N'
    #     else:
    #         return result[0]  # 返回用户输入的结果
    

    def isNameMatchByDict(self,ClassGen:ClassDef,ClassOracle:ClassDef)-> bool:
        NameGen=ClassGen.getName()
        NameOracle=ClassOracle.getName()

        # check if the name is already matched in mapMatched
        storedName= self.mapMatched.get(NameGen)
        if storedName == NameOracle:
            return True
        
        storedUnmatchedNames = self.mapUnmatched.get(NameGen, [])
    
        if NameOracle in storedUnmatchedNames:
            return False
        print(f"------------")
        print(f"{NameGen}({ClassGen.getKind()}):{[attr.getName() for attr in ClassGen.getAttributes()]}")
        print(f"{NameOracle}({ClassOracle.getKind()}):{[attr.getName() for attr in ClassOracle.getAttributes()]}")
        print(f"------------")
        
        # user_input = input((f"Does {NameGen} match {NameOracle}? (Y/N): ").strip())
        user_input = 'N'
        # user_input = self.timed_input(f"Does {NameGen} match {NameOracle}? (Y/N): ", 5)
        
        if user_input.upper() == 'Y':
            self.mapMatched[NameGen] = NameOracle
            return True
        elif user_input.upper() == 'N':
            storedUnmatchedNames.append(NameOracle)
            self.mapUnmatched[NameGen] = storedUnmatchedNames
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
            return self.isNameMatchByDict(ClassGen, ClassOracle)  # Recurse until valid input is given
        
           
            # # storedUnmatchedNames stores one or many unmatched classes_Oracle. 
            # storedUnmatchedNames=self.mapUnmatched.get(NameGen)
            # if storedUnmatchedNames is None:
            #     storedUnmatchedNames = []
            #     # self.mapUnmatched[NameGen] = storedUnmatchedNames
            
            # if storedUnmatchedNames.count(NameOracle) >0:
            #     return False
            # else:
            #     user_input = input(f"Does {NameGen} match {NameOracle}? (Y/N)")
            #     if user_input == 'Y':
            #         self.mapMatched[NameGen] = NameOracle
            #         return True
            #     else:
            #         storedUnmatchedNames.append(NameOracle)
            #         self.mapUnmatched[NameGen] = storedUnmatchedNames

    def _matchInClassList(self, candidates:List[ClassDef], oracles:List[ClassDef], cond:Callable[[ClassDef,ClassDef],bool], matched_name:Dict[str,str], matched_classes:Dict[ClassDef,ClassDef]) -> Tuple[int,List[ClassDef]]:
        correct_counts = 0
        unmatched = []

        matched_oracle_names = set()  # To track already matched oracle names
    
        for cls in candidates:
            flag = False
            # 需要通过matched_classes 排除已经匹配的类class
            o_clses_have_matched = set(matched_classes.values())
            oracle_candidates = [cls for cls in oracles if cls not in o_clses_have_matched]
            for ora in oracle_candidates:
                if ora.getName().strip() in matched_oracle_names:
                    continue

                if cond(cls,ora):
                    flag = True
                    matched_name[cls.getName().strip()] = ora.getName().strip()
                    self.mapMatched[cls.getName().strip()] = ora.getName().strip()
                    matched_classes[cls] = ora
                    # oracles.pop(i)
                    matched_oracle_names.add(ora.getName().strip())
                    correct_counts += 1
                    break
                
            if flag == False:
                unmatched.append(cls)
        
        return correct_counts, unmatched
    

    
    def matchClasses(self,model_gen:ModelDef,model_oracle:ModelDef)->Tuple[Dict[str,str],Dict[ClassDef,ClassDef]]:
        generated_classes = model_gen.get_all_classes()
        oracle_classes = model_oracle.get_all_classes()
        
        classes = generated_classes.copy()
        oracles = oracle_classes.copy()

        generated_counts = len(classes)
        oracle_counts = len(oracles)
        correct_counts = 0


        matched_names : Dict[str,str] = {}
        matched_classes : Dict[ClassDef,ClassDef] = {}
        unmatched_classes = []

        # for cls in oracle:
        #     for str in cls.getAttributes():
        #         self.oracle_attributes_count +=1

        # for cls in classes:
        #     for str in cls.getAttributes():
        #         self.generated_attributes_count +=1

        c,unmatched_classes = self._matchInClassList(classes, oracles, lambda c,o: self.isNameMatch(c.getName(), o.getName()), matched_names, matched_classes)
        correct_counts += c

        c,unmatched_classes = self._matchInClassList(unmatched_classes, oracles, lambda c,o: self.isClassJaccMatch(c, o), matched_names, matched_classes)
        correct_counts += c

        c,unmatched_classes = self._matchInClassList(unmatched_classes, oracles, lambda c,o: self.isNameMatchByDict(c, o), matched_names, matched_classes)
        correct_counts += c


        # for cls in classes:
        #     flag = False
        #     for i in range(len(oracle)):
        #         if self.isNameMatched(cls,oracle[i]):
        #             flag = True
        #             matched_name[cls.getName().strip()] = oracle[i].getName().strip()
        #             matched_class[cls] = oracle[i]
        #             # print(f' O  Class:{cls.getName()}  Oracle:{oracle[i].getName()}',file=f_class_file)
        #             # matched_attr = self.matchAttributes(f_class_file,cls.getAttributes(),oracle[i].getAttributes())
        #             correct_counts += 1
        #             oracle.pop(i)
        #             break
        #     if not flag:
        #         unmatched.append(cls)

        # for cls in unmatched:
        #     flag = False
        #     for i in range(len(oracle)):
        #         if cls.isMatched(oracle[i]):
        #             flag = True
        #             matched_name[cls.getName().strip()] = oracle[i].getName().strip()
        #             matched_class[cls] = oracle[i]
        #             # print(f' O  Class:{cls.getName()}  Oracle:{oracle[i].getName()} ',file=f_class_file)
        #             # matched_attr = self.matchAttributes(f_class_file,cls.getAttributes(),oracle[i].getAttributes())
        #             correct_counts += 1
        #             oracle.pop(i)
        #             break
        #     if not flag:
        #         final_unmatched.append(cls)
        #         matched_name[cls.getName().strip()] = cls.getName().strip()
        #         print(f' X  Class:{cls.getName()}',file=f_class_file)
        #         # log_info.append(str)
        #         for str in cls.getAttributes():
        #             print(f'   X  Attribute:{str.getName()} ',file=f_class_file)

        

        self.matched_classes_count = correct_counts
        self.generated_classes_count = generated_counts
        self.oracle_classes_count = oracle_counts


        return matched_names,matched_classes

    # def matchClassesMaually(self,f_class_file,generated_classes,oracle_classes,classes_map):
    #     classes = generated_classes.copy()
    #     oracle = oracle_classes.copy()

    #     generated_counts = len(classes)
    #     oracle_counts = len(oracle)
    #     correct_counts = 0


    #     matched_name = {}
    #     matched_class = {}
    #     unmatched = []
    #     final_unmatched = []

    #     for cls in oracle:
    #         for str in cls.getAttributes():
    #             self.oracle_attributes_count +=1

    #     for cls in classes:
    #         for str in cls.getAttributes():
    #             self.generated_attributes_count +=1

    #     for cls in classes:
    #         flag = False
    #         for i in range(len(oracle)):
    #             if classes_map[cls.getName().strip()] and (oracle[i].getName().strip() == classes_map[cls.getName().strip()]):
    #                 flag = True
    #                 matched_name[cls.getName().strip()] = oracle[i].getName().strip()
    #                 # print(f'matched_name{[cls.getName().strip()]} = {oracle[i].getName().strip()}')
    #                 matched_class[cls] = oracle[i]
    #                 print(f' O  Class:{cls.getName()}  Oracle:{oracle[i].getName()}',file=f_class_file)
    #                 matched_attr = self.matchAttributes(f_class_file,cls.getAttributes(),oracle[i].getAttributes())
    #                 correct_counts += 1
    #                 oracle.pop(i)
    #                 break
    #         if not flag:
    #             unmatched.append(cls)

    #     for cls in unmatched:
    #         flag = False
    #         for i in range(len(oracle)):
    #             if cls.isMatched(oracle[i]):
    #                 flag = True
    #                 matched_name[cls.getName().strip()] = oracle[i].getName().strip()
    #                 matched_class[cls] = oracle[i]
    #                 print(f' O  Class:{cls.getName()}  Oracle:{oracle[i].getName()} ',file=f_class_file)
    #                 matched_attr = self.matchAttributes(f_class_file,cls.getAttributes(),oracle[i].getAttributes())
    #                 correct_counts += 1
    #                 oracle.pop(i)
    #                 break
    #         if not flag:
    #             final_unmatched.append(cls)
    #             matched_name[cls.getName().strip()] = cls.getName().strip()
    #             print(f' X  Class:{cls.getName()}',file=f_class_file)
    #             # log_info.append(str)
    #             for str in cls.getAttributes():
    #                 print(f'   X  Attribute:{str.getName()} ',file=f_class_file)


    #     self.matched_classes_count = correct_counts
    #     self.generated_classes_count = generated_counts
    #     self.oracle_classes_count = oracle_counts
    #     return matched_name,matched_class,final_unmatched


    


    def matchAttributes(self,model_gen:ModelDef,model_oracle:ModelDef,matched_classes:Dict[ClassDef,ClassDef])->Tuple[Dict[str,str],Dict[AttributeDef,AttributeDef],int]:
        """
        return xxx jsut print to store in log.  
        loop oracle_cls:
        1. find class_gen, oracle_cls 
        2. match attribute_gen with attributes_oracle , make List:unmatched_attr
        3. update self.attributes_gen_count, self.attributes_matched_count, self.attributes_oracle_count, 
        3. find oracle_cls's all parent class
        2. make an attributes_list for a oracle_cls's all parent class
        3. match unmatched_atttr (attributes_gen) of a cls_gen with attributes_list of a cls_oracle 
        """
        classes_gen = model_gen.get_all_classes()
        classes_oracle = model_oracle.get_all_classes()

        for cls_gen in classes_gen:
            self.generated_attributes_count += len(cls_gen.getAttributes())
        for cls_ora in classes_oracle:
            self.oracle_attributes_count += len(cls_ora.getAttributes())
        
        #  Preprocess attributes for oracle classes and their parent classes
        attributes_of_classes_oracle:Dict[ClassDef,List[AttributeDef]] ={} # {"classA_oracle":List[attr],...}


        for cls_oracle in classes_oracle:
            attributes_of_classes_oracle[cls_oracle]=[]
            all_parents = model_oracle.get_all_parent_classes(cls_oracle)
            for parent_cls in all_parents:
                attributes_of_classes_oracle[cls_oracle].extend(parent_cls.getAttributes())
        

        matched_attributes_name:Dict[str,str] = {}
        matched_attributes:Dict[AttributeDef,AttributeDef] = {}
        correct_counts = 0
        matched_attrs_counts_4recall = 0
        
        # Match attributes if their classes match
        for cls_gen,cls_ora in matched_classes.items():
            attirbutes_cls_gen = cls_gen.getAttributes()
            attributes_cls_oracle = attributes_of_classes_oracle[cls_ora]

            if not attributes_cls_oracle:
                continue  

        
            for attr_cls_gen in attirbutes_cls_gen:
                for attr_cls_oracle in attributes_cls_oracle:
                    if self.isNameMatch(attr_cls_gen.getName(), attr_cls_oracle.getName()):
                        matched_attributes_name[f'{cls_gen.getName()}({cls_gen.getKind()}):{attr_cls_gen.getName()}']= attr_cls_oracle.getName()
                        matched_attributes[attr_cls_gen]=attr_cls_oracle
                        correct_counts+=1
                        # if attr_cls_oracle in matched_cls_o.getAttributes():
                        #     correct_counts+=1
                        # else:
                        #     correct_counts +=1
                        #     self.oracle_attributes_count+=1
                            
                        break
            
            # 请计算这两个list中的交集：number
            cls_ora_attributes  = set(str.getName() for str in cls_ora.getAttributes()) # attributes of oracle class
            cls_matched_ora_attributes= set(str.getName() for str in matched_attributes.values()) # matched attributes in this <class_gen, class_oracle> pair
            intersection_attributes= list(cls_ora_attributes & cls_matched_ora_attributes)
            # print(f"{'-'*80}\nOracle Classes matched:\n{cls_ora.getName()}:{intersection_attributes}")
            matched_attrs_counts_4recall += len(intersection_attributes)
        self.matched_attributes_count = correct_counts
        self.matched_attributes_count4recall = matched_attrs_counts_4recall
        return matched_attributes_name, matched_attributes
        

        
        # # attributes_gen =
        # attribute = generated_attributes.copy()
        # oracle = oracle_attributes.copy()

        # generated_counts = len(attribute)
        # oracle_counts = len(oracle)
        # correct_counts = 0

        # for attr in generated_attributes:
        #     flag = False
        #     if 'etc' in attr.getName() or '...' in attr.getName():
        #         continue
        #     for i in range(len(oracle)):
        #         if self.isNameMatched(oracle[i]):
        #             matched_attributes[attr.getName()] = oracle[i].getName()
        #             # print(f'   O  Attribute:{attr.getName()}  Oracle:{oracle[i].getName()} ',file=f_class_file)

        #             correct_counts += 1
        #             flag = True
        #             oracle.pop(i)
        #             break
        #     if not flag:
        #         # print(f'   X  Attribute:{attr.getName()} ',file=f_class_file)

        # # self.matched_attributes_count += correct_counts

        # return matched_attributes_name,matched_attributes



    def isRelationshipMatched(self,relationship_gen:RelationshipDef,relationship_oracle:RelationshipDef,class_name_map:Dict[str,str])->bool:
        # solve bug:  AttributeError: 'NoneType' object has no attribute 'getKind'
        if relationship_gen is None or relationship_oracle is None:
            print("One of the relationships is None.")
            return False
        
        kind_gen = relationship_gen.getKind()
        kind_oracle = relationship_oracle.getKind()

        source_gen = class_name_map.get(relationship_gen.getSource())
        target_gen = class_name_map.get(relationship_gen.getTarget())
        source_oracle = relationship_oracle.getSource()
        target_oracle = relationship_oracle.getTarget()

        # if any source or target is not in the class name map, return false
        if not source_gen or not target_gen:
            return False
        
        # handle different relationship kinds
        # inheritance and aggregation need match source_gen with source_oracle, and target_gen with target_oracle
        if kind_gen in {KIND_AGGREGATION,KIND_INHERITANCE}:
            if kind_gen != kind_oracle:
                return False
            
            if source_gen == source_oracle and target_gen ==target_oracle:
                return True
            return False
        # association 
        if kind_gen ==KIND_ASSOCIATION:
            # ???
            if kind_oracle==KIND_INHERITANCE:
                return False
            
            if (source_gen == source_oracle and target_gen ==target_oracle) or (source_gen==target_oracle and target_gen ==source_oracle):
                return True
            
            return False

        
        # if relationship_gen.getKind() == KIND_INHERITANCE or relationship_gen.getKind() == KIND_AGGREGATION:
        #     if relationship_gen.getKind() != relationship_oracle.getKind():
        #         return False
        #     if  class_name_map[relationship_gen.getSource()] == relationship_oracle.getSource() and class_name_map[relationship_gen.getTarget()] == relationship_oracle.getTarget():
        #         return True
        #     return False
        # if relationship_gen.getKind() == KIND_ASSOCIATION :
        #     if relationship_oracle.getKind() == KIND_INHERITANCE:
        #         return False
        #     # print(f'{relationship_gen.getSource()}/{classMap[relationship_gen.getSource()]}--{relationship_gen.getTarget()}/{classMap[relationship_gen.getTarget()]}// {oracle.getSource()} --{oracle.getTarget()}')
        #     if class_name_map[relationship_gen.getSource()] == relationship_oracle.getSource() and class_name_map[relationship_gen.getTarget()] == relationship_oracle.getTarget():
        #         # print('1')
        #         return True
        #     if class_name_map[relationship_gen.getSource()] == relationship_oracle.getTarget() and class_name_map[relationship_gen.getTarget()] == relationship_oracle.getSource():
        #         # print('1')
        #         return True

        # return False


    def matchRelationships(self,model_gen:ModelDef,model_oracle:ModelDef,class_name_map:Dict[str,str])->Dict[RelationshipDef,RelationshipDef]:
        classes_name_gen = [cls.getName() for cls in model_gen.get_all_classes()]
        rels_gen = [rel for rel in model_gen.get_all_relationships() if rel is not None]
        rels_oracle = [rel for rel in model_oracle.get_all_relationships() if rel is not None]

        matched_relationships = {}
        
        self.oracle_associations_count = sum(map(lambda x: 1 if x and x.getKind() != KIND_INHERITANCE else 0,rels_oracle))
        self.oracle_inheritances_count = sum(map(lambda x: 1 if x and x.getKind() == KIND_INHERITANCE else 0,rels_oracle))

        self.gen_associations_count = sum(map(lambda x: 1 if x and x.getKind() != KIND_INHERITANCE else 0,rels_gen))
        self.gen_inheritances_count = sum(map(lambda x: 1 if x and x.getKind() == KIND_INHERITANCE else 0,rels_gen))

        self.matched_associations_count = 0
        self.matched_inheritances_count = 0

        # valid_classes = set(class_name_map.keys())
        # Build a dictionary of relationships in the oracle model keyed by (source, target)

        for rel_gen in rels_gen:
            source_gen, target_gen = rel_gen.getSource(), rel_gen.getTarget()
            if source_gen not in classes_name_gen or target_gen not in classes_name_gen:
                if rel_gen.getKind() == KIND_INHERITANCE:
                    self.gen_inheritances_count -= 1
                    # print(f'The class in the relation is not in the oracle:{rel.getSource()} extends/inherit {rel.getTarget()}',file=f_relationship)
                else:
                    self.gen_associations_count -= 1
                    # print(f'The class in the relation is not in the oracle:{rel.getSource()} associate {rel.getTarget()}',file=f_relationship)
                continue
        

            for i, rel_oracle in enumerate(rels_oracle):
                # solve bug:  AttributeError: 'NoneType' object has no attribute 'getKind'
                if self.isRelationshipMatched(rel_gen,rel_oracle,class_name_map):
                    if rel_gen.getKind() == KIND_INHERITANCE:
                        self.matched_inheritances_count += 1
                    else:
                        self.matched_associations_count += 1

                    matched_relationships[rel_gen] = rel_oracle
                    rels_oracle[i]=None
                    break
            rels_oracle = [rel for rel in rels_oracle if rel is not None]

        return matched_relationships


    def matchModel(self,model_gen:ModelDef,model_oracle:ModelDef)->Tuple[Dict[ClassDef,ClassDef],Dict[str,str],Dict[RelationshipDef,RelationshipDef]]:

        matched_classes_name, matched_classes =self.matchClasses(model_gen,model_oracle)
        matched_relationships = self.matchRelationships(model_gen,model_oracle,matched_classes_name)
        matched_attributes_name, matched_attributes = self.matchAttributes(model_gen,model_oracle,matched_classes)

        # matched_name, matched_class = self.matchClassesAndAttributes(classes_gen, classes_oracle)
        # matched_rel = self.matchRelationship(relationships_gen,relationships_oracle,matched_name)
        self.update_map()
        return matched_classes,matched_attributes_name,matched_relationships


    # def matchClassesAndAttributes(self, classes_gen:List[ClassDef], classes_oracle:List[ClassDef]):
    #     matched_name,matched_class = self.matchClasses(classes_gen,classes_oracle)
    #     for g_cls,o_cls in matched_class.items():
    #         self.matchAttributes(g_cls.getAttributes(),o_cls.getAttributes())
    #     return matched_name,matched_class



