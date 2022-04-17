from skripsi.scripts.c45 import create_rule
from skripsi.scripts.confusion_matrix import confusion_matrix
from skripsi.models import KFCV
import time,random

def k_fold_cross_validation(k_CV,dataset,instance,atribut,seleksi,atrNumerik):
    kfcv = KFCV.objects.filter().values()        
    result_avg = {'accuracy':0, 'recall':0, 'precision':0, 'f_measure':0, 'time':0}
    pengujian = {}
    for i in range(10):
        # GET DATA TRAIN & DATA TEST
        dataTest = []
        dataTrain = []
        for data in kfcv:
            if data['fold'] == i+1:
                dataTest.append(dataset[data['id_data']-1])
            elif data['fold'] != i+1 and data['fold'] != 0:
                dataTrain.append(dataset[data['id_data']-1])

        # C4.5 
        start = time.perf_counter()
        rule,ruleAtr,tree = create_rule(dataTrain,instance,atribut,seleksi,atrNumerik)
        acc,cm = confusion_matrix(dataTest,rule)
        end = time.perf_counter()
        
        # SAVE DATA
        hasil = result(cm)
        pengujian[i+1] = {
            'tree':tree,
            'ruleAtr':ruleAtr,
            'cm': cm,
            'result' : hasil,
            'time' : round(end-start,5),
            }

        result_avg['accuracy'] += hasil['accuracy']
        result_avg['recall'] += hasil['recall']
        result_avg['precision'] += hasil['precision']
        result_avg['f_measure'] += hasil['f_measure']
        result_avg['time'] += round(end-start,5)


        # for j in tree: print(j)
        # print('true ckd      :',cm[0])
        # print('true notckd   :',cm[1])
        # print('false ckd     :',cm[2])
        # print('false notckd  :',cm[3])
        # print('accuracy      :',acc,'\n')
    
    result_avg['accuracy'] = round(result_avg['accuracy']/10,3)
    result_avg['recall'] = round(result_avg['recall']/10,3)
    result_avg['precision'] = round(result_avg['precision']/10,3)
    result_avg['f_measure'] = round(result_avg['f_measure']/10,3)
    result_avg['time'] = round(result_avg['time']/10,5)

    return pengujian, result_avg

def result(cm):
    accuracy = round(((cm[0]+cm[1])/sum(cm))*100, 3)
    recall = round((cm[0]/(cm[0]+cm[3]))*100, 3)
    precision = round((cm[0]/(cm[0]+cm[2]))*100, 3)
    f_measure = round(2*(recall*precision)/(recall+precision), 3)

    return {'accuracy':accuracy, 'recall':recall, 'precision':precision, 'f_measure':f_measure}

