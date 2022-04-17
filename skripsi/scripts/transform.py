import copy

def transform_dataset_and_instance(dataset,ranges):
    atribut = ['Age','Bp','Sg','Al','Su','Rbc','Pc','Pcc','Ba','Bgr','Bu','Sc','Sod','Pot','Hemo','Pcv','Wc','Rc','Htn','Dm','Cad','Appet','Pe','Ane','Class']
    atrNumerik = [0,1,9,10,11,12,13,14,15,16,17]
    instance = [
        {}, # age
        {}, # bp
        {1:'1.005', 2:'1.010', 3:'1.015', 4:'1.020', 5:'1.025'}, # Sg
        {1:'0', 2:'1', 3:'2', 4:'3', 5:'4', 6:'5'}, # Al
        {1:'0', 2:'1', 3:'2', 4:'3', 5:'4', 6:'5'}, # Su
        {1:'normal', 2:'abnormal'}, # Rbc
        {1:'normal', 2:'abnormal'}, # Pc
        {1:'present', 2:'notpresent'}, # Pcc
        {1:'present', 2:'notpresent'}, # Ba
        {}, # bgr
        {}, # bu
        {}, # sc
        {}, # sod
        {}, # pot
        {}, # hemo
        {}, # pvc
        {}, # wc
        {}, # rc
        {1:'yes', 2:'no'}, # Htn
        {1:'yes', 2:'no'}, # Dm
        {1:'yes', 2:'no'}, # Cad
        {1:'good', 2:'poor'}, # Appet
        {1:'yes', 2:'no'}, # Pe
        {1:'yes', 2:'no'}, # Ane
        {1:'ckd', 2:'notckd'}, # Class
    ]

    dataset = transf_data(dataset,ranges,atrNumerik,instance)
    instance = transf_instance(ranges,instance,atribut)
    return dataset,instance,atribut,atrNumerik

def transf_data(dataset,ranges,atrNumerik,instance):
    datasetNew = copy.deepcopy(dataset)
    for data in datasetNew:
        for i,d in enumerate(data):
            if str(d) != '?':
                if i in atrNumerik:
                    value = (float(d))
                    for j,range in enumerate(ranges[i]):
                        if j == 0:
                            if value<=range:
                                data[i] = j+1
                                break
                        elif j == len(ranges[i])-1:
                            if value>range:
                                data[i] = j+1
                                break
                        else:
                            if value>range[0] and value<=range[1]:
                                data[i] = j+1
                                break
                else:
                    for j in instance[i]:
                        if instance[i][j] == data[i]:
                            data[i] = j
                            break
    return datasetNew

def transf_instance(ranges,instance,atribut):
    instanceNew = copy.deepcopy(instance)
    for range in ranges:
        for i,r in enumerate(ranges[range]):
            if i == 0:
                instanceNew[range][i+1] = ' &#8804 '+str(r)
            elif i == len(ranges[range])-1:
                instanceNew[range][i+1] = ' > '+str(r)
            else:
                instanceNew[range][i+1] = ' > '+str(r[0])+' AND '+atribut[range]+' &#8804 '+str(r[1])
    return instanceNew

