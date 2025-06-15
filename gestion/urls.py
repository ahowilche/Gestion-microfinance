from django.urls import path
from gestion import views
from .views import AjouterClient, ListeComptesView


urlpatterns = [
    path("", views.index, name="index"),
    path("GMyCom/connexion/", views.login_view, name="login"),
    path('GMyCom/deconnexion/', views.logout_view, name='logout'),
    #Tableau de bord et ses onglets
    #accueil
    path("GMyCom/tableau-bord/", views.dashboard, name="dashboard"),
    #Zone du client : liste, ajout, modification et suppresion
    path("GMyCom/tableau-bord/liste-client", views.liste_clients, name="liste_clients"),
    path('GMyCom/tableau-bord/clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('GMyCom/tableau-bord/clients/modifier/<int:client_id>/', views.modifier_client, name='modifier_client'),
    path('GMyCom/tableau-bord/compte/ajouter/<int:client_id>/', views.ajouter_compte, name='ajouter_compte'),  
    path('GMyCom/tableau-bord/ajouterClient/', AjouterClient.as_view(), name='ajouter_client'),
    
    #Zone des compte
    path('GMyCom/tableau-bord/compte/liste-compte/', ListeComptesView.as_view(), name='liste_compte'),
    path('GMyCom/tableau-bord/compte/transaction/', views.effectuer_transaction, name='effectuer_transaction'),
    path('GMyCom/tableau-bord/compte/transaction/operation/<int:compte_id>/', views.process_transaction, name='process_transaction'),

    
    #zone de transaction
]