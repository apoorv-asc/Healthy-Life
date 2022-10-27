from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('cost_pred/',views.cost_pred,name="cost_pred"),
    path('disease_pred/',views.disease_pred,name="disease_pred"),
    path('ner/',views.ner,name="ner")
]
