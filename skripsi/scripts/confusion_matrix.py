import random

def accuracy(dataTest,rules):
    iter = 0
    for data in dataTest:
        for rule in rules:
            flag=True
            for i,r in enumerate(rule):
                if r!=0 and i!=(len(rule)-1):
                    if r!=data[i]: 
                        flag=False
                        break
            if flag==True: 
                if data[(len(rule)-1)] == rule[(len(rule)-1)]:
                    iter+=1
                break

    return (iter/len(dataTest))*100

def confusion_matrix(dataTest,rules):
    cm = [0,0,0,0] # index : 0=TrueCKD 1=TrueNOTCKD 2=FalseCKD 3=FalseNOTCKD
    for data in dataTest:
        for rule in rules:
            flag=True
            missing_value = False
            for i,r in enumerate(rule):
                if r!=0 and i!=(len(rule)-1):
                    if str(data[i]) == '?':
                        missing_value = True
                        break
                    if r!=data[i]: 
                        flag=False
                        break
            if flag==True: 
                if missing_value == True:
                    if data[-1]==1:
                        cm[2]+=1
                    elif data[-1]==2:
                        cm[3]+=1
                elif data[-1]==1 and rule[-1]==1:
                    cm[0]+=1
                elif data[-1]==2 and rule[-1]==2:
                    cm[1]+=1
                elif data[-1]==1 and rule[-1]==2:
                    cm[2]+=1
                elif data[-1]==2 and rule[-1]==1:
                    cm[3]+=1
                break
    
    return ((cm[0]+cm[1])/sum(cm))*100, cm