from django.urls import path
from gestion import views


urlpatterns = [
    path("", views.index, name="index"),
    path("GMyCom/connexion/", views.login_view, name="login"),
    path('GMyCom/deconnexion/', views.logout_view, name='logout'),

    path("GMyCom/tableau-bord/", views.dashboard, name="dashboard"),
]