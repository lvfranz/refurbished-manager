from django.urls import path
from . import views, reports

app_name = 'orders'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('scadenze/', views.scadenze_view, name='scadenze'),
    path('ordine/<int:pk>/', views.ordine_detail_view, name='ordine_detail'),
    path('report/sostituzioni/', reports.report_articoli_sostituiti, name='report_sostituzioni'),
    path('report/cliente/<int:cliente_id>/sostituzioni/', reports.report_sostituzioni_cliente, name='report_cliente_sostituzioni'),
]

