from django.db import models

class Dataset(models.Model):
    Age = models.CharField(max_length=255)
    Bp = models.CharField(max_length=255)
    Sg = models.CharField(max_length=255)
    Al = models.CharField(max_length=255)
    Su = models.CharField(max_length=255)
    Rbc = models.CharField(max_length=255)
    Pc = models.CharField(max_length=255)
    Pcc = models.CharField(max_length=255)
    Ba = models.CharField(max_length=255)
    Bgr = models.CharField(max_length=255)
    Bu = models.CharField(max_length=255)
    Sc = models.CharField(max_length=255)
    Sod = models.CharField(max_length=255)
    Pot = models.CharField(max_length=255)
    Hemo = models.CharField(max_length=255)
    Pcv = models.CharField(max_length=255)
    Wc = models.CharField(max_length=255)
    Rc = models.CharField(max_length=255)
    Htn = models.CharField(max_length=255)
    Dm = models.CharField(max_length=255)
    Cad = models.CharField(max_length=255)
    Appet = models.CharField(max_length=255)
    Pe = models.CharField(max_length=255)
    Ane = models.CharField(max_length=255)
    Class = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.id)

class Range(models.Model):
    atribut = models.CharField(max_length=255)
    min = models.CharField(max_length=255)
    max = models.CharField(max_length=255)
    diskrit = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.id)

class Range_pengujian(models.Model):
    atribut = models.CharField(max_length=255)
    min = models.CharField(max_length=255)
    max = models.CharField(max_length=255)
    diskrit = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.id)

class Rule(models.Model):
    kelas = models.CharField(max_length=255)
    rule = models.CharField(max_length=255)

    def __str__(self):
        return "{}. {} : {}".format(self.id,self.rule,self.kelas)

class Detail_Rule(models.Model):
    id_rule = models.IntegerField()
    atribut = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.id)

class KFCV(models.Model):
    id_data = models.IntegerField()
    fold = models.IntegerField()
    jenis = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "{}".format(self.id)

class Plot(models.Model):
    atribut = models.CharField(max_length=255)
    sc = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.id)
