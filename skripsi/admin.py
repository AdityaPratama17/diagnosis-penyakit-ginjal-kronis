from django.contrib import admin
from .models import KFCV, Dataset, Detail_Rule, Rule

# Register your models here.
admin.site.register(Dataset)
admin.site.register(Rule)
admin.site.register(Detail_Rule)
admin.site.register(KFCV)