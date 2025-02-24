
from typing import List, Tuple
from Matcher import Matcher


def count_metric(generated_count,matched_count,oracle_count):    
    if generated_count:
        precision = matched_count / generated_count
    else:
        precision = 0
    if oracle_count:
        recall = matched_count / oracle_count
    else:
        recall = 0
    if (precision + recall):
        f1 = 2*precision*recall/(precision+recall)
    else:
        f1 = 0
    if (precision + recall):
        f2 = (5 * precision * recall) / (4 * precision + recall)
    else:
        f2 = 0

    return precision,recall,f1,f2


def count_metric_atr(generated_count,matched_count,matched_count_ora,oracle_count):    
    if generated_count:
        precision = matched_count / generated_count
    else:
        precision = 0
    if oracle_count:
        recall = matched_count_ora / oracle_count
    else:
        recall = 0
    if (precision + recall):
        f1 = 2*precision*recall/(precision+recall)
    else:
        f1 = 0
    if (precision + recall):
        f2 = (5 * precision * recall) / (4 * precision + recall)
    else:
        f2 = 0

    return precision,recall,f1,f2


def print_metrics_1(Ma:Matcher, ps, name, c, sum_test_result,used_tokens):
    categories = [
        ("classes", Ma.generated_classes_count, Ma.matched_classes_count, Ma.oracle_classes_count),
        ("attributes", Ma.generated_attributes_count, Ma.matched_attributes_count,Ma.oracle_attributes_count),
        ("inheritances", Ma.gen_inheritances_count, Ma.matched_inheritances_count, Ma.oracle_inheritances_count),
        ("associations", Ma.gen_associations_count, Ma.matched_associations_count, Ma.oracle_associations_count)
    ]
    
    # Calculate metrics for each category and store them
    metrics = {}
    for category, generated, matched, oracle in categories:
        if category == 'attributes':
            precision,recall,f1,f2 = count_metric_atr(generated,matched,Ma.matched_attributes_count4recall,oracle)
            metrics[category] = {
                "precision": precision, 
                "recall": recall, 
                "f1": f1, 
                "f2": f2
            }
        else:
            precision, recall, f1, f2 = count_metric(generated, matched, oracle)
            metrics[category] = {
                "precision": precision, 
                "recall": recall, 
                "f1": f1, 
                "f2": f2
            }
    
    # Calculate relationship metrics
    generated_relationship_count = Ma.gen_associations_count + Ma.gen_inheritances_count
    matched_relationship_count = Ma.matched_associations_count + Ma.matched_inheritances_count
    oracle_relationship_count = Ma.oracle_associations_count + Ma.oracle_inheritances_count
    relationship_precision, relationship_recall, relationship_f1, relationship_f2 = count_metric(generated_relationship_count, matched_relationship_count, oracle_relationship_count)
    output = [
        f'{name},{c}-method1,{used_tokens},'
        f'{metrics["classes"]["precision"]:.4f},{metrics["classes"]["recall"]:.4f},{metrics["classes"]["f1"]:.4f},{metrics["classes"]["f2"]:.4f},'
        f'{metrics["attributes"]["precision"]:.4f},{metrics["attributes"]["recall"]:.4f},{metrics["attributes"]["f1"]:.4f},{metrics["attributes"]["f2"]:.4f},'
        f'{relationship_precision:.4f},{relationship_recall:.4f},{relationship_f1:.4f},{relationship_f2:.4f},'
        f'{metrics["associations"]["precision"]:.4f},{metrics["associations"]["recall"]:.4f},{metrics["associations"]["f1"]:.4f},{metrics["associations"]["f2"]:.4f},'
        f'{metrics["inheritances"]["precision"]:.4f},{metrics["inheritances"]["recall"]:.4f},{metrics["inheritances"]["f1"]:.4f},{metrics["inheritances"]["f2"]:.4f},'
        f'{Ma.matched_classes_count},{Ma.generated_classes_count},{Ma.oracle_classes_count},'
        f'{Ma.matched_attributes_count},{Ma.generated_attributes_count},{Ma.oracle_attributes_count},'
        f'{Ma.matched_associations_count},{Ma.gen_associations_count},{Ma.oracle_associations_count},'
        f'{Ma.matched_inheritances_count},{Ma.gen_inheritances_count},{Ma.oracle_inheritances_count}'
    ]
    print(f'{name},{c}-method1,precision,recall,f1,f2()\n,{used_tokens},'
        f'classes: {metrics["classes"]["precision"]:.4f},{metrics["classes"]["recall"]:.4f},{metrics["classes"]["f1"]:.4f},{metrics["classes"]["f2"]:.4f},\n'
        f'attributes:{metrics["attributes"]["precision"]:.4f},{metrics["attributes"]["recall"]:.4f},{metrics["attributes"]["f1"]:.4f},{metrics["attributes"]["f2"]:.4f},\n'
        f'relationships:{relationship_precision:.4f},{relationship_recall:.4f},{relationship_f1:.4f},{relationship_f2:.4f},\n'
        f'associations:{metrics["associations"]["precision"]:.4f},{metrics["associations"]["recall"]:.4f},{metrics["associations"]["f1"]:.4f},{metrics["associations"]["f2"]:.4f},\n'
        f'inheritances {metrics["inheritances"]["precision"]:.4f},{metrics["inheritances"]["recall"]:.4f},{metrics["inheritances"]["f1"]:.4f},{metrics["inheritances"]["f2"]:.4f},\n')
    print(*output, file=ps)

    # Update sum_test_result with current metrics
    pre_score = [
        metrics["classes"]["precision"], metrics["classes"]["recall"], metrics["classes"]["f1"], metrics["classes"]["f2"],
        metrics["attributes"]["precision"], metrics["attributes"]["recall"], metrics["attributes"]["f1"], metrics["attributes"]["f2"],
        relationship_precision, relationship_recall, relationship_f1, relationship_f2,
        metrics["associations"]["precision"], metrics["associations"]["recall"], metrics["associations"]["f1"], metrics["associations"]["f2"],
        metrics["inheritances"]["precision"], metrics["inheritances"]["recall"], metrics["inheritances"]["f1"], metrics["inheritances"]["f2"],
        Ma.matched_classes_count, Ma.generated_classes_count, Ma.oracle_classes_count,
        Ma.matched_attributes_count, Ma.generated_attributes_count, Ma.oracle_attributes_count,
        Ma.matched_associations_count, Ma.gen_associations_count, Ma.oracle_associations_count,
        Ma.matched_inheritances_count, Ma.gen_inheritances_count, Ma.oracle_inheritances_count,
        used_tokens
    ]
    
    sum_test_result = list(map(lambda x, y: x + y, sum_test_result, pre_score))
    return sum_test_result


def print_metrics_2(Ma:Matcher,ps,name:str,c:int,accumulators:List[int],gen_relas_count,match_relas_count,oracle_relas_count)->Tuple[List[int],int,int,int]:
     # 完成累加的功能
    gen_relas_count += Ma.gen_associations_count + Ma.gen_inheritances_count
    match_relas_count += Ma.matched_associations_count + Ma.matched_inheritances_count
    oracle_relas_count += Ma.oracle_associations_count + Ma.oracle_inheritances_count
     # Update accumulators using simplified llama syntax
    accumulators[0] += Ma.matched_classes_count
    accumulators[1] += Ma.generated_classes_count
    accumulators[2] += Ma.oracle_classes_count

    accumulators[12] += Ma.matched_attributes_count4recall
    accumulators[3] += Ma.matched_attributes_count
    accumulators[4] += Ma.generated_attributes_count
    accumulators[5] += Ma.oracle_attributes_count

    accumulators[6] += Ma.matched_associations_count
    accumulators[7] += Ma.gen_associations_count
    accumulators[8] += Ma.oracle_associations_count

    accumulators[9] += Ma.matched_inheritances_count
    accumulators[10] += Ma.gen_inheritances_count
    accumulators[11] += Ma.oracle_inheritances_count

    return accumulators,gen_relas_count,match_relas_count,oracle_relas_count