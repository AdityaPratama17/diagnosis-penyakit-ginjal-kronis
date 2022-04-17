from django.urls import path
from skripsi import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dataset', views.dataset, name="dataset"),
    path('diagnosis', views.diagnosis, name="diagnosis"),
    path('update_rules', views.update_rules, name="update_rules"),
    path('pengujian', views.pengujian, name="pengujian"),

    # --
    path('split_data', views.split_data, name="split_data"),
    path('hasil_uji', views.hasil_uji, name="hasil_uji"),
    path('hasil_uji_akselerasi', views.hasil_uji_akselerasi, name="hasil_uji_akselerasi"),
    path('uji_overfitting', views.uji_overfitting, name="uji_overfitting"),
]