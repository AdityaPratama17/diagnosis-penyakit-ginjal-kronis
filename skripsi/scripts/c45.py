import math, random, numpy as np, copy

def data_cleaning(dataset):
    data_clean = []
    for data in dataset: 
        flag = True
        for d in data:
            if d == '?':
                flag = False
                break
        if flag == True: data_clean.append(data)
    return data_clean

def selection(dataset,instance,atribut,seleksi,atrNumerik):
    newDataset = []
    newInstance = []
    newAtribut = []
    newAtrNumerik = []
    newAtrNumerik = {}

    # SELECT COLOUMN DATASET
    for data in dataset:
        temp = []
        for i in range(len(data)-1):
            if seleksi[i] == 1: 
                temp.append(data[i])
        temp.append(data[i+1])
        newDataset.append(temp)
    
    # SELECT INSTANCE & ATRIBUT
    for i in range(len(seleksi)):
        if seleksi[i] == 1: 
            newInstance.append(instance[i])
            newAtribut.append(atribut[i])
            if i in atrNumerik:
                # newAtrNumerik.append(i)
                newAtrNumerik[i] = atribut[i]
    newInstance.append(instance[i+1])
    newAtribut.append(atribut[i+1])

    return newDataset,newInstance,newAtribut,newAtrNumerik

def create_rule(dataset,instance,atribut,seleksi,atrNumerik):
    # GET DATA WITHOUT MISSING VALUE
    data_clean = data_cleaning(dataset)

    # INIT VARIABLE
    ruleAwal = np.zeros(sum(seleksi)+1, dtype=int).tolist()
    rule = []
    tree = []

    # CREATE RULE
    rule,tree = createDecisionTree(atribut,dataset,data_clean,instance,ruleAwal,rule,[],tree)

    # GET FULL RULE TREE
    finalRule = []
    for subtree in tree:
        temp = 'IF '
        for i,node in enumerate(subtree):
            if i == len(subtree)-1: temp += ' THEN '
            elif i >= 1: temp += ' AND '
            if type(node) is not int: 
                if node['atr_name'] in atrNumerik.values():
                    temp += str(atribut[node['atr']])+str(instance[node['atr']][node['ins']])
                else:
                    temp += str(atribut[node['atr']])+' = '+str(instance[node['atr']][node['ins']])
            else: temp += str(instance[-1][node])
        finalRule.append(temp)
        # print(temp)

    return rule,tree,finalRule

def createDecisionTree(atribut,data_raw,dataset,instance,rule,ruleSet,tree,treeSet):
    # SELECTED DATA
    newDataset, new_data_raw = filter_data(data_raw,dataset,rule)

    # ENTROPY TOTAL
    indexKelas = len(rule)-1
    et = entropy(newDataset,indexKelas)

    # INIT VAR
    ei = {} # entropy instance
    ig = {} # info gain
    si = {} # split info
    gr = {} # gain ratio

    # PERULANGAN ATRIBUT
    for atr in range(len(rule)-1):
        ei[atr] = {}
        if rule[atr]==0:
            # PERULANGAN INSTANCE
            for ins in instance[atr]:
                # ENTROPY INSTANCE
                tempDataset,temp_data_raw = filter_data(new_data_raw,newDataset,createTempRule(rule,atr,ins))
                ei[atr][ins] = entropy(tempDataset,indexKelas)
            # INFO GAIN
            ig[atr] = infoGain(new_data_raw,newDataset,instance,et,ei,atr)
            # SPLIT INFO
            si[atr] = splitInfo(new_data_raw,newDataset,atr,instance)
            # GAIN RATIO
            if si[atr]==0: gr[atr]=0
            else: gr[atr]=ig[atr]/si[atr]
    
    # GAIN RATIO TERBESAR
    maxGainRatio = {'gainRatio_value':max(gr.values()),'atribut_index':max(gr, key=gr.get)}

    # PERULANGAN INSTANCE DARI GAIN RATIO TERBESAR
    for ins in instance[maxGainRatio['atribut_index']]:
        # PEMBUATAN RULE DAN REKURSIF 
        tempRule = createTempRule(rule,maxGainRatio['atribut_index'],ins)
        tempTree = createTempTree(atribut,tree,maxGainRatio['atribut_index'],ins)
        if ei[maxGainRatio['atribut_index']][ins]==0:
            tempDataset,temp_data_raw = filter_data(new_data_raw,newDataset,tempRule)
            ruleSet.append(createRule(tempDataset,tempRule,indexKelas))
            tempTree.append(ruleSet[-1][-1])
            treeSet.append(tempTree)
        else: 
            if rule.count(0)==2:
                tempDataset,temp_data_raw = filter_data(new_data_raw,newDataset,tempRule)
                ruleSet.append(createRule(tempDataset,tempRule,indexKelas))
                tempTree.append(ruleSet[-1][-1])
                treeSet.append(tempTree)
            else:
                ruleSet,treeSet = createDecisionTree(atribut,new_data_raw,newDataset,instance,tempRule,ruleSet,tempTree,treeSet)
    
    return ruleSet,treeSet

def filter_data(data_raw,dataset,rule):
    selectData = []
    for data in dataset:
        for i,item in enumerate(data):
            flag = True
            if rule[i]!=0:
                if rule[i]!=item:
                    flag = False
                    break
        if flag==True: 
            selectData.append(data)
    
    selectData_raw = []
    for data in data_raw:
        for i,item in enumerate(data):
            flag = True
            if rule[i]!=0:
                if rule[i]!=item and str(item) != '?':
                    flag = False
                    break
        if flag==True: 
            selectData_raw.append(data)

    return selectData,selectData_raw

def entropy(dataset,indexKelas):
    jumData = len(dataset)
    jumKelas1 = jumlahDataPer(dataset,indexKelas,1)
    jumKelas2 = jumlahDataPer(dataset,indexKelas,2)

    if jumData==0 or jumKelas1==0 or jumKelas2==0:
        return 0
    else:
        return ( (-jumKelas1/jumData) * (math.log(jumKelas1/jumData, 2.0)) ) + ( (-jumKelas2/jumData) * (math.log(jumKelas2/jumData, 2.0)) )

def infoGain(data_raw,dataset,instance,et,ei,atribut):
    ig =  0
    for ins in instance[atribut]:
        ig += (jumlahDataPer(dataset,atribut,ins)/len(dataset))*ei[atribut][ins]
    
    jum_dataset = len(dataset)
    jum_data_raw = len(data_raw)

    return (jum_dataset/jum_data_raw)*(et-ig)

def splitInfo(data_raw,dataset,atribut,instance):
    si = 0
    for ins in instance[atribut]:
        jumDataInstance = jumlahDataPer(dataset,atribut,ins)
        if jumDataInstance!=0:
            si += (-jumDataInstance/len(dataset))*(math.log(jumDataInstance/len(dataset), 2.0))
    
    jum_missing_value = 0
    for data in data_raw:
        if str(data[atribut]) == '?':
            jum_missing_value += 1
    
    if jum_missing_value!=0:
        si += (-jum_missing_value/len(dataset))*(math.log(jum_missing_value/len(dataset), 2.0))

    return si

def createTempRule(rule,atribut,instance):
    newRule = copy.deepcopy(rule)
    newRule[atribut]=instance
    return newRule

def createTempTree(atributName,tree,atribut,instance):
    newTree = copy.deepcopy(tree)
    newTree.append({'atr':atribut, 'atr_name':atributName[atribut], 'ins':instance})
    return newTree

def createRule(dataset,rule,indexKelas):
    jumKelas1 = jumlahDataPer(dataset,indexKelas,1)
    jumKelas2 = jumlahDataPer(dataset,indexKelas,2)

    newRule = copy.deepcopy(rule)
    if jumKelas1>jumKelas2: newRule[indexKelas] = 1
    elif jumKelas1<jumKelas2: newRule[indexKelas] = 2
    elif jumKelas1==jumKelas2: newRule[indexKelas] = random.randint(1,2)
    return newRule

def jumlahDataPer(dataset,atribut,value):
    jum=0
    for data in dataset:
        if data[atribut]==value: 
            jum+=1
    return jum



