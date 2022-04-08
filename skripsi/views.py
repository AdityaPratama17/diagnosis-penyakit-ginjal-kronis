from django.shortcuts import render, redirect
from .models import KFCV, Dataset, Plot, Range, Range_pengujian, Rule, Detail_Rule
from skripsi.scripts.kmeans import find_ranges as kmeans
from skripsi.scripts.transform import transform_dataset_and_instance as transform
from skripsi.scripts.bpso import feature_selection as bpso
from skripsi.scripts.bpso_uji import feature_selection as bpso_uji
from skripsi.scripts.c45 import selection
from skripsi.scripts.pengujian import k_fold_cross_validation
import pandas as pd, random, time
import io,urllib,base64,csv
import matplotlib.pyplot as plt

def index(request):
    return redirect('skripsi:dataset')

def dataset(request):
    # GET DATA
    dataset = pd.read_csv('static/dataset/CKD - missing value.csv', header = None).values.tolist()

    # FORMAT & INSERT DATASET TO DATABASE
    Dataset.objects.all().delete()
    for i,data in enumerate(dataset):
        Dataset.objects.create(
            id = i+1,
            Age = data[0],
            Bp = data[1],
            Sg = data[2],
            Al = data[3],
            Su = data[4],
            Rbc = data[5],
            Pc = data[6],
            Pcc = data[7],
            Ba = data[8],
            Bgr = data[9],
            Bu = data[10],
            Sc = data[11],
            Sod = data[12],
            Pot = data[13],
            Hemo = data[14],
            Pcv = data[15],
            Wc = data[16],
            Rc = data[17],
            Htn = data[18],
            Dm = data[19],
            Cad = data[20],
            Appet = data[21],
            Pe = data[22],
            Ane = data[23],
            Class = data[24],
        )

    # SET DATA ATTRIBUTES
    atribut = {'Age':['Age','Numerikal'],'Bp':['Blood Pressure','Kategorikal'],'Sg':['Specific Gravity','Kategorikal'],'Al':['Albumin','Kategorikal'],'Su':['Sugar','Kategorikal'],'Rbc':['Red Blood Cells','Kategorikal'],'Pc':['Pus Cell','Kategorikal'],'Pcc':['Pus Cell clumps','Kategorikal'],'Ba':['Bacteria','Kategorikal'],'Bgr':['Blood Glucose Random','Numerikal'],'Bu':['Blood Urea','Numerikal'],'Sc':['Serum Creatinine','Numerikal'],'Sod':['Sodium','Numerikal'],'Pot':['Potassium','Numerikal'],'Hemo':['Hemoglobin','Numerikal'],'Pcv':['Packed  Cell Volume','Numerikal'],'Wc':['White Blood Cell Count','Numerikal'],'Rc':['Red Blood Cell Count','Numerikal'],'Htn':['Hypertension','Kategorikal'],'Dm':['Diabetes Mellitus','Kategorikal'],'Cad':['Coronary Artery Disease','Kategorikal'],'Appet':['Appetite','Kategorikal'],'Pe':['Pedal Edema','Kategorikal'],'Ane':['Anemia','Kategorikal'],'Class':['Class','Kategorikal']}

    context ={
        'title' : 'Dataset',
        'dataset': dataset,
        'atribut': atribut,
    }
    return render(request, 'skripsi/index.html', context)

def diagnosis(request):
    # GET RULES
    rules = Rule.objects.values()

    if request.method == 'POST':
        # DISKRITISASI
        ranges = Range.objects.filter().values()
        diskrit = {}
        for range in ranges:
            if range['min']=='-':
                if float(request.POST[range['atribut']]) <= float(range['max']): 
                    diskrit[range['atribut']] = range['diskrit']
            elif range['max']=='-':
                if float(request.POST[range['atribut']]) > float(range['min']): 
                    diskrit[range['atribut']] = range['diskrit']
            else:
                if float(request.POST[range['atribut']]) > float(range['min']) and float(request.POST[range['atribut']]) <= float(range['max']): 
                    diskrit[range['atribut']] = range['diskrit']

        # KLASIFIKASI
        atrNumerik = ['Age', 'Bp', 'Bgr', 'Bu', 'Sc', 'Sod', 'Pot', 'Hemo', 'Pcv', 'Wc', 'Rc']
        all_rule = Rule.objects.filter().values()
        rule = Detail_Rule.objects.filter().values()
        for i in all_rule:
            flag = True
            for r in rule:
                if r['id_rule'] == i['id']:
                    if r['atribut'] in atrNumerik:
                        if diskrit[r['atribut']] != r['value']:
                            flag = False
                            break
                    else:
                        if request.POST[r['atribut']] != r['value']:
                            flag = False
                            break
            if flag == True:
                hasil = i['kelas']
                rule_benar = i['id']
                break
        
        context ={
            'title' : 'Diagnosis',
            'hasil' : hasil,
            'rule_benar' : rule_benar,
            'rules' : rules,
            'old' : request.POST,
        }
        return render(request, 'skripsi/diagnosis.html', context)
        
    context ={
        'title' : 'Diagnosis',
        'rules' : rules,
    }
    return render(request, 'skripsi/diagnosis.html', context)

def update_rules(request):
    # GET DATASET FROM DB
    dataset_db = Dataset.objects.filter().values()
    dataset = []
    for data in dataset_db:
        temp_arr = []
        for key,value in data.items():
            if key != 'id':
                temp_arr.append(value)
        dataset.append(temp_arr)

    # KMEANS
    ranges,plot = kmeans(dataset,'no')

    # TRANSFORMASI
    dataset,instance,atribut,atrNumerik = transform(dataset,ranges)

    # SELEKSI FITUR (BPSO)
    seleksi,result_avg,pengujian = bpso(dataset,instance,atribut,atrNumerik,int(request.POST['partikel']),int(request.POST['iterasi']),float(request.POST['w']),float(request.POST['c1']),float(request.POST['c2']))
    dataset,instance,atribut,atrNumerik = selection(dataset,instance,atribut,seleksi,atrNumerik)

    # GET BEST MODEL IN 10-FOLD CROSS VALIDATION
    rules = {}
    for i in pengujian:
        if i == 1:
            best = pengujian[i]['result']['accuracy']
            ruleAtr = pengujian[i]['ruleAtr']
            tree = pengujian[i]['tree']
        
        elif pengujian[i]['result']['accuracy'] > best:
            best = pengujian[i]['result']['accuracy']
            ruleAtr = pengujian[i]['ruleAtr']
            tree = pengujian[i]['tree']

    # INSERT MODEL TO DATABASE
    # -- data ranges
    atribut_numerik = ['Age','Bp','Sg','Al','Su','Rbc','Pc','Pcc','Ba','Bgr','Bu','Sc','Sod','Pot','Hemo','Pcv','Wc','Rc','Htn','Dm','Cad','Appet','Pe','Ane','Class']
    Range.objects.all().delete()
    iter = 1
    for atr,range in ranges.items():
        for i,value in enumerate(range):
            if i == 0:
                Range.objects.create(id=iter, atribut=atribut_numerik[atr], min='-', max=str(value), diskrit=i+1)
            elif i == len(range)-1:
                Range.objects.create(id=iter, atribut=atribut_numerik[atr], min=str(value), max='-', diskrit=i+1)
            else:
                Range.objects.create(id=iter, atribut=atribut_numerik[atr], min=str(value[0]), max=str(value[1]), diskrit=i+1)
            iter += 1

    # -- data rules
    Rule.objects.all().delete()
    Detail_Rule.objects.all().delete()
    iter = 1
    for i,rule in enumerate(ruleAtr):
        for j,item in enumerate(rule):
            if j != len(rule)-1:
                Detail_Rule.objects.create(id=iter, id_rule=i+1, atribut=item['atr_name'], value=item['ins'])
                iter+=1
            else:
                Rule.objects.create(id=i+1, kelas=item, rule=tree[i])
    
    return redirect('skripsi:diagnosis')

def pengujian(request):
    if request.method == 'POST':
        # GET DATASET FROM DB
        dataset_db = Dataset.objects.filter().values()
        dataset = []
        for data in dataset_db:
            temp_arr = []
            for key,value in data.items():
                if key != 'id':
                    temp_arr.append(value)
            dataset.append(temp_arr)
        
        start_total = time.perf_counter()

        # KMEANS
        atribut_all = ['Age','Bp','Sg','Al','Su','Rbc','Pc','Pcc','Ba','Bgr','Bu','Sc','Sod','Pot','Hemo','Pcv','Wc','Rc','Htn','Dm','Cad','Appet','Pe','Ane','Class']
        if request.POST['diskrit'] == 'baru':
            Plot.objects.all().delete()
            ranges,plot = kmeans(dataset,'yes')
            # INSERT RANGES TO DB
            Range_pengujian.objects.all().delete()
            iter = 1
            for atr,range in ranges.items():
                for i,value in enumerate(range):
                    if i == 0:
                        Range_pengujian.objects.create(id=iter, atribut=atribut_all[atr], min='-', max=str(value), diskrit=i+1)
                    elif i == len(range)-1:
                        Range_pengujian.objects.create(id=iter, atribut=atribut_all[atr], min=str(value), max='-', diskrit=i+1)
                    else:
                        Range_pengujian.objects.create(id=iter, atribut=atribut_all[atr], min=str(value[0]), max=str(value[1]), diskrit=i+1)
                    iter += 1
        else:
            # GET RANGES FROM DB
            ranges_db = Range_pengujian.objects.filter().values()
            ranges = {}
            for range in ranges_db:
                if atribut_all.index(range['atribut']) not in ranges:
                    ranges[atribut_all.index(range['atribut'])] = []
                if range['min']=='-':
                    ranges[atribut_all.index(range['atribut'])].append(float(range['max']))
                elif range['max']=='-':
                    ranges[atribut_all.index(range['atribut'])].append(float(range['min']))
                else:
                    ranges[atribut_all.index(range['atribut'])].append([float(range['min']),float(range['max'])])
            # GET PLOT FROM DB
            plot_db = Plot.objects.filter().values()
            atribut_numerik = [0,1,9,10,11,12,13,14,15,16,17]
            plot = {}
            for i in atribut_numerik:
                temp = []
                for p in plot_db:
                    if p['atribut'] == atribut_all[i]:
                        temp.append(float(p['sc']))
                
                fig = plt.figure()
                plt.plot([2,3,4,5,6,7,8,9,10],temp,marker = 'o')
                plt.xlabel("Jumlah Klaster")
                plt.ylabel("Silhouette Coeficient Value")
                plt.grid(axis = 'y')
                plt.title('Silhouette Coeficient',loc='center')
                buf = io.BytesIO()
                fig.savefig(buf,format='png')
                buf.seek(0)
                string = base64.b64encode(buf.read())
                plot[atribut_all[i]] = urllib.parse.quote(string)
                plt.close(fig)

        ranges_html = {}
        for key,range in ranges.items(): 
            temp = []
            for i,data in enumerate(range):
                if i == 0:
                    temp.append({'diskrit':i+1,'range':'data &#8804 '+str(data)})
                elif i == len(range)-1:
                    temp.append({'diskrit':i+1,'range':'data > '+str(data)})
                else:
                    temp.append({'diskrit':i+1,'range':'data > '+str(data[0])+' dan data &#8804 '+str(data[1])})
            ranges_html[atribut_all[key]] = temp


        # TRANSFORMASI
        dataset,instance,atribut,atrNumerik = transform(dataset,ranges)

        # SELEKSI FITUR (BPSO)
        if request.POST['seleksi'] == 'yes':
            start = time.perf_counter()
            seleksi,result_avg,pengujian = bpso(dataset,instance,atribut,atrNumerik,int(request.POST['partikel']),int(request.POST['iterasi']),float(request.POST['w']),float(request.POST['c1']),float(request.POST['c2']))
            dataset,instance,atribut,atrNumerik = selection(dataset,instance,atribut,seleksi,atrNumerik)
            time_bpso = round(time.perf_counter() - start, 3)
            atribut_name = ['Age','Blood Pressure','Specific Gravity','Albumin','Sugar','Red Blood Cells','Pus Cell','Pus Cell clumps','Bacteria','Blood Glucose Random','Blood Urea','Serum Creatinine','Sodium','Potassium','Hemoglobin','Packed  Cell Volume','White Blood Cell Count','Red Blood Cell Count','Hypertension','Diabetes Mellitus','Coronary Artery Disease','Appetite','Pedal Edema','Anemia','Class']
            seleksi_html = {}
            for i,data in enumerate(seleksi):
                if data == 1: 
                    seleksi_html[atribut_all[i]] = {'atr_pendek':atribut_all[i], 'atr_panjang':atribut_name[i],'keterangan':'Digunakan'} 
                else: 
                    seleksi_html[atribut_all[i]] = {'atr_pendek':atribut_all[i], 'atr_panjang':atribut_name[i],'keterangan':'Tidak digunakan'}
            
        else:
            seleksi = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            dataset,instance,atribut,atrNumerik = selection(dataset,instance,atribut,seleksi,atrNumerik)
            seleksi_html = {}
            time_bpso = 0
            pengujian,result_avg = k_fold_cross_validation(10,dataset,instance,atribut,seleksi,atrNumerik)
        

        end_total = time.perf_counter()
        print('WAKTU TOTAL :',round(end_total-start_total,5))

        context ={
            'title' : 'Pengujian',
            'old' : request.POST,
            # kmeans
            'ranges' : ranges_html,
            'plot' : plot,
            # bpso
            'seleksi' : seleksi_html,
            'jumlah_atribut' : sum(seleksi),
            'time_bpso' : time_bpso,
            # pengujian
            'pengujian': pengujian,
            'result_avg': result_avg,
        }
        return render(request, 'skripsi/pengujian.html', context)

    context ={
        'title' : 'Pengujian',
    }
    return render(request, 'skripsi/pengujian.html', context)

def split_data(request):
    if request.method == 'POST':
        KFCV.objects.all().delete()
        data = Dataset.objects.filter().values()
        rand = random.sample(range(0,400), 400)
        sum = [
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
            {'ckd':0,'notckd':0},
        ]
        
        iter = 1
        test = []
        for i,fold in enumerate(sum):
            for j,id in enumerate(rand):
                if id not in test:
                    if data[id]['Class'] == 'ckd':
                        if fold['ckd'] < 25:
                            KFCV.objects.create(id=iter, id_data=data[id]['id'], fold=i+1, jenis='test')
                            fold['ckd'] += 1
                            test.append(id)
                        else:
                            KFCV.objects.create(id=iter, id_data=data[id]['id'], fold=i+1, jenis='train')
                    else:
                        if fold['notckd'] < 15:
                            KFCV.objects.create(id=iter, id_data=data[id]['id'], fold=i+1, jenis='test')
                            fold['notckd'] += 1
                            test.append(id)
                        else:
                            KFCV.objects.create(id=iter, id_data=data[id]['id'], fold=i+1, jenis='train')
                else:
                    KFCV.objects.create(id=iter, id_data=data[id]['id'], fold=i+1, jenis='train')
                iter += 1

    
    return render(request, 'skripsi/split_data.html')


# ============= PENGUJIAN UNTUK SKRIPSI =============
def hasil_uji(request):   
    if request.method == 'POST':
        # get data
        dataset,instance,atribut,atrNumerik = get_data()
        
        # set param
        partikel = 15
        iterasi = 40
        w = 1.2
        c1 = c2 = 2
        error = 0.1
        
        start = time.perf_counter()
        arr_hasil = []
        old = 0
        i = 11
        while(i<=15): 
            # -- param check
            c1 = c2 = i
            # -- evaluate
            hasil,time_bpso,jum_seleksi = evaluasi(dataset,instance,atribut,atrNumerik,partikel,iterasi,w,c1,c2,i)
            # -- update dict
            hasil['param'] = i
            hasil['time_bpso'] = time_bpso
            hasil['jum_seleksi'] = jum_seleksi
            # -- check error
            if i != 1:
                hasil['selisih'] = abs(old-hasil['accuracy'])
                arr_hasil.append(hasil)
                # if abs(old-hasil['accuracy']) <= error:
                    # break
            else:
                hasil['selisih'] = hasil['accuracy']
                arr_hasil.append(hasil)

            print(i,'. now:',hasil['accuracy'],', before:',old,', selisih:',hasil['selisih'])
            old = hasil['accuracy']
            i += 1
        # -- print in csv
        cetak_csv(arr_hasil)
        end = time.perf_counter()
        print('WAKTU AKHIR:',round(end-start,5))

    return render(request, 'skripsi/hasil_uji.html')

def hasil_uji_akselerasi(request):   
    if request.method == 'POST':
        # get data
        dataset,instance,atribut,atrNumerik = get_data()
        
        # set param
        partikel = 15
        iterasi = 40
        w = 0.9
        # c1 = 1 
        # c2 = 1.2

        c1_arr = [2,1.8,1.6,1.4,1.2,0.1,0.5,1,1.5,2,0.2,0.4,0.6,0.8,1]
        c2_arr = [0.2,0.4,0.6,0.8,1,0.1,0.5,1,1.5,2,2,1.8,1.6,1.4,1.2]

        start = time.perf_counter()
        arr_hasil = []
        old = 0
        for i,val in enumerate(c1_arr):
            # -- param check
            c1 = c1_arr[i]
            c2 = c2_arr[i]
            # -- evaluate
            hasil,time_bpso,jum_seleksi = evaluasi(dataset,instance,atribut,atrNumerik,partikel,iterasi,w,c1,c2,i+1)
            # -- update dict
            hasil['param'] = i+1
            hasil['time_bpso'] = time_bpso
            hasil['jum_seleksi'] = jum_seleksi
            # -- check error
            if i != 0:
                hasil['selisih'] = abs(old-hasil['accuracy'])
                arr_hasil.append(hasil)
            else:
                hasil['selisih'] = hasil['accuracy']
                arr_hasil.append(hasil)

            print(i+1,'. now:',hasil['accuracy'],', before:',old,', selisih:',hasil['selisih'])
            old = hasil['accuracy']
        # -- print in csv
        cetak_csv(arr_hasil)
        end = time.perf_counter()
        print('WAKTU AKHIR:',round(end-start,5))

    return render(request, 'skripsi/hasil_uji_akselerasi.html')

def get_data():
    # GET DATASET FROM DB
    dataset_db = Dataset.objects.filter().values()
    dataset = []
    for data in dataset_db:
        temp_arr = []
        for key,value in data.items():
            if key != 'id':
                temp_arr.append(value)
        dataset.append(temp_arr)

    atribut_all = ['Age','Bp','Sg','Al','Su','Rbc','Pc','Pcc','Ba','Bgr','Bu','Sc','Sod','Pot','Hemo','Pcv','Wc','Rc','Htn','Dm','Cad','Appet','Pe','Ane','Class']
    # GET RANGES FROM DB
    ranges_db = Range_pengujian.objects.filter().values()
    ranges = {}
    for range in ranges_db:
        if atribut_all.index(range['atribut']) not in ranges:
            ranges[atribut_all.index(range['atribut'])] = []
        if range['min']=='-':
            ranges[atribut_all.index(range['atribut'])].append(float(range['max']))
        elif range['max']=='-':
            ranges[atribut_all.index(range['atribut'])].append(float(range['min']))
        else:
            ranges[atribut_all.index(range['atribut'])].append([float(range['min']),float(range['max'])])
    
    # TRANSFORMASI
    dataset,instance,atribut,atrNumerik = transform(dataset,ranges)

    return dataset,instance,atribut,atrNumerik

def evaluasi(dataset,instance,atribut,atrNumerik,partikel,iterasi,w,c1,c2,iter_param):
    # SELEKSI FITUR (BPSO)
    start = time.perf_counter()
    seleksi,result_avg,pengujian = bpso_uji(dataset,instance,atribut,atrNumerik,partikel,iterasi,w,c1,c2,iter_param)
    dataset,instance,atribut,atrNumerik = selection(dataset,instance,atribut,seleksi,atrNumerik)
    end = time.perf_counter()

    return result_avg,round(end-start,5),sum(seleksi)

def cetak_csv(mydict):        
    # field names 
    fields = ['param','accuracy','recall','precision','f_measure','time','time_bpso','jum_seleksi','selisih'] 
    # name of csv file 
    filename = "static/dataset/pengujian.csv"
    # writing to csv file 
    with open(filename, 'w', newline='') as csvfile: 
        # creating a csv dict writer object 
        writer = csv.DictWriter(csvfile, fieldnames = fields) 
        # writing headers (field names) 
        writer.writeheader() 
        # writing data rows 
        writer.writerows(mydict) 