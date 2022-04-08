import numpy as np, copy, time
from skripsi.scripts.c45 import selection
from skripsi.scripts.pengujian import k_fold_cross_validation


def feature_selection(dataset,instance,atribut,atrNumerik,jumPartikel,iterasi,w,c1,c2):
    # INIT
    gbest = {'fitness':0, 'fitur': [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 'result_avg':{}, 'pengujian':{}}
    pbest = []
    v = []
    x = []
    r1 = 1 #0.2
    r2 = 1 #0.4

    # INIT x & v
    v,x,pbest = inisialisasi_x_v(x,v,jumPartikel,pbest)

    # UPDATE GBEST PBEST BBY ITERATE
    fitness = []
    for i in range(iterasi):
        pbest,gbest = update_gbest_pbest(x,gbest,pbest,jumPartikel,dataset,instance,atribut,atrNumerik,i+1)
        v = update_kecepatan(v,x,jumPartikel,w,c1,c2,r1,r2,pbest,gbest)
        x = update_posisi(v,jumPartikel)
        fitness.append(gbest['fitness'])

    return gbest['fitur'],gbest['result_avg'],gbest['pengujian']

def inisialisasi_x_v(x,v,jumPartikel,pbest):
    # keceptan (v)
    v = np.zeros((jumPartikel,24)).tolist()
    # posisi (x)
    x = np.random.randint(2, size=(jumPartikel,24)).tolist()
    # pbest
    for i in range(jumPartikel):
        pbest.append({'fitness':0, 'fitur':x[i]})
        
    return v,x,pbest

def update_gbest_pbest(x,gbest,pbest,jumPartikel,dataset,instance,atribut,atrNumerik,num_iter):
    for i in range(jumPartikel):
        # hitung fitness (C4.5)
        start = time.perf_counter()
        tempDataset,tempInstance,tempAtribut,tempAtrNumerik = selection(dataset,instance,atribut,x[i],atrNumerik)
        pengujian,result_avg = k_fold_cross_validation(10,tempDataset,tempInstance,tempAtribut,x[i],tempAtrNumerik)
        fitness = result_avg['accuracy']
        print(num_iter,'.',i+1,'. Waktu KFCV:',round(time.perf_counter()-start,5),'. Fitness:',fitness,'. Jum Fitur:',sum(x[i]))

        # update gbest & pbest
        ubah = False
        if fitness >= pbest[i]['fitness']: 
            if fitness == pbest[i]['fitness']:
                if sum(x[i]) < sum(pbest[i]['fitur']):
                    ubah = True
            else:
                ubah = True
        if ubah:
            # update pbest
            pbest[i] = {'fitness':fitness, 'fitur':x[i]}
            if fitness >= gbest['fitness']:
                if fitness == gbest['fitness']:
                    if sum(x[i]) < sum(gbest['fitur']):
                        # update gbest
                        gbest = {'fitness':fitness, 'fitur':x[i], 'result_avg':result_avg, 'pengujian':pengujian}
                else:
                    # update gbest
                    gbest = {'fitness':fitness, 'fitur':x[i], 'result_avg':result_avg, 'pengujian':pengujian}

    return pbest,gbest

def update_kecepatan(v,x,jumPartikel,w,c1,c2,r1,r2,pbest,gbest):
    v_new = copy.deepcopy(v)
    for i in range(jumPartikel):
        for j in range(len(v[i])):
            v_new[i][j] = w*v[i][j] + c1*r1*(pbest[i]['fitur'][j]-x[i][j]) + c2*r2*(gbest['fitur'][j]-x[i][j])
    return v_new

def update_posisi(v,jumPartikel):
    sig = np.zeros((jumPartikel,24)).tolist()
    rand = np.random.uniform(low=0.0, high=1.0, size=(jumPartikel,24)).tolist()
    for i in range(jumPartikel):
        for j in range(len(v[i])):
            sig[i][j] = 1/(1 + np.exp(-v[i][j]))
            if rand[i][j] < sig[i][j]: sig[i][j] = 1
            else: sig[i][j] = 0
    return sig