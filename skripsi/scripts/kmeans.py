import math,random
from statistics import mean
import io,urllib,base64
import matplotlib.pyplot as plt

from skripsi.models import Plot

def find_ranges(dataset,save_plot):
    atribut = ['Age','Bp','Sg','Al','Su','Rbc','Pc','Pcc','Ba','Bgr','Bu','Sc','Sod','Pot','Hemo','Pcv','Wc','Rc','Htn','Dm','Cad','Appet','Pe','Ane','Class']
    atribut_numerik = [0,1,9,10,11,12,13,14,15,16,17]
    ranges = {}
    plot = {}
    for atr in atribut_numerik:
        # AMBIL DATA SESUAI ATRIBUT
        dataAtribut = get_data_by_attribute(dataset,atr)
        maxx = max(dataAtribut)
        minn = min(dataAtribut)

        # NORMALISASI
        dataAtribut = [(data-minn)/(maxx-minn) for data in dataAtribut]

        # CARI DATA KLUSTER
        klaster,SC_value = find_data_cluster_by_SC(dataAtribut)
        klaster = [sorted(k) for k in klaster]
        klaster = sorted(klaster, key=lambda x: x[0], reverse=False)

        # SET RANGES
        ranges[atr] = []
        for i in range(len(klaster)):
            # DENORMALISASI
            if i == 0:
                ranges[atr].append(round(max(klaster[i])*(maxx-minn)+minn, 2))
            elif i == len(klaster)-1:
                ranges[atr].append(round(max(klaster[i-1])*(maxx-minn)+minn, 2))
            else:
                min_range = round(max(klaster[i-1])*(maxx-minn)+minn, 2)
                max_range = round(max(klaster[i])*(maxx-minn)+minn, 2)
                ranges[atr].append([min_range,max_range])
        
        if save_plot == 'yes':
            # # CREATE PLOT
            fig = plt.figure()
            plt.plot([2,3,4,5,6,7,8,9,10],SC_value,marker = 'o')
            plt.xlabel("Jumlah Klaster")
            plt.ylabel("Silhouette Coeficient Value")
            plt.grid(axis = 'y')
            plt.title('Silhouette Coeficient',loc='center')
            buf = io.BytesIO()
            fig.savefig(buf,format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read())
            plot[atribut[atr]] = urllib.parse.quote(string)
            plt.close(fig)

            # # INSERT SC VALUE TO DB
            for i in SC_value:
                Plot.objects.create(atribut=atribut[atr], sc=i)

    return ranges,plot

def get_data_by_attribute(dataset,atribut):
    data_clean = []
    for data in dataset:
        if str(data[atribut]) != '?':
            data_clean.append(float(data[atribut]))
    return data_clean

def find_data_cluster_by_SC(dataset):
    SC_value = []
    klaster_selected = []

    for jumlah_centroid in range(2,11):
        klaster = find_centroid_and_cluster(dataset,jumlah_centroid)
        sc = silhouette(klaster)
        SC_value += [sc]

        if jumlah_centroid==2: 
            sc_max = sc
            klaster_selected = klaster
        else:
            if sc >= sc_max:
                sc_max = sc
                klaster_selected = klaster
        
    # hapus klaster yang tidak memiliki anggota
    new_klaster_selected = [kls for kls in klaster_selected if len(kls) != 0]
            
    return new_klaster_selected,SC_value

def find_centroid_and_cluster(dataset,jumCentroid):
    # SET CENTROID AWAL
    centroid = random.sample(dataset, jumCentroid)

    # CREATE CENTROID
    oldCentroid = centroid
    while(True):
        newCentroid,klaster = createCentroid(dataset,oldCentroid,jumCentroid)
        if newCentroid==oldCentroid: break
        else: oldCentroid=newCentroid
    
    return klaster

def createCentroid(dataset,centroid,jumCentroid):
    # INIT KLASTER
    klaster = []
    for i in range(jumCentroid):
        klaster.append([])

    # SET KLASTER (EUCLIDEAN)
    minn = {'klaster_awal':0, 'klaster_akhir':0}
    for data in dataset:
        for i,ctd in enumerate(centroid):
            euclidean = math.sqrt((ctd-data)**2)
            if i==0: 
                minn['klaster_awal']=euclidean
            if minn['klaster_awal']>=euclidean: 
                minn['klaster_awal']=euclidean
                minn['klaster_akhir']=i
        klaster[minn['klaster_akhir']].append(data)
    
    # SET NEW CENTROID
    newCentroid = []
    for i,kls in enumerate(klaster):
        if len(kls)==0:
            newCentroid.append(centroid[i])
        else:
            newCentroid.append(mean(kls))
    
    return newCentroid,klaster

def silhouette(klaster):
    # perhitungan a(i)
    ai = []
    for kls in klaster:
        if len(kls) == 1:
            ai.append([0])
        else:
            temp = []
            for data_a in kls:
                sum = 0
                for data_b in kls:
                    if data_a != data_b:
                        sum += math.sqrt((data_a - data_b)**2)
                temp.append(sum/(len(kls)-1))
            ai.append(temp)
    
    # perhitungan b(i)
    bi = []
    for kls_a in klaster:
        temp = []
        for data_a in kls_a:
            di = []
            for kls_b in klaster:
                if kls_a != kls_b:
                    sum = 0
                    for data_b in kls_b:
                        sum += math.sqrt((data_a - data_b)**2)
                    if len(kls_b) == 0: di.append(0)
                    else: di.append(sum/len(kls_b))
            temp.append(min(di))
        bi.append(temp)

    # perhitungan si
    si = []
    for i,kls in enumerate(klaster):
        for j,data in enumerate(kls):
            if max(bi[i][j],ai[i][j]) == 0: 
                si.append(0)
            else:
                si.append((bi[i][j]-ai[i][j])/max(bi[i][j],ai[i][j]))
    
    return mean(si)