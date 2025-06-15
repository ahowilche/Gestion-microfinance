# Déjà importés :
from django.urls import path
from gestion import views
from .views import AjouterClient, ListeComptesView

urlpatterns = [
    # --- Authentification & tableau de bord ---
    path("", views.index, name="index"),
    path("GMyCom/connexion/", views.login_view, name="login"),
    path('GMyCom/deconnexion/', views.logout_view, name='logout'),
    path("GMyCom/tableau-bord/", views.dashboard, name="dashboard"),

    # --- Zone Clients ---
    path("GMyCom/tableau-bord/liste-client", views.liste_clients, name="liste_clients"),
    path('GMyCom/tableau-bord/clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('GMyCom/tableau-bord/clients/modifier/<int:client_id>/', views.modifier_client, name='modifier_client'),
    path('GMyCom/tableau-bord/compte/ajouter/<int:client_id>/', views.ajouter_compte, name='ajouter_compte'),
    path('GMyCom/tableau-bord/ajouterClient/', AjouterClient.as_view(), name='ajouter_client'),

    # --- Zone Comptes ---
    path('GMyCom/tableau-bord/compte/liste-compte/', ListeComptesView.as_view(), name='liste_compte'),

    # --- Zone Transactions (à ajouter) ---
    # Mouvement (Dépôt / Retrait)
    path('GMyCom/tableau-bord/transaction/', views.effectuer_transaction, name='effectuer_transaction'),
    path('GMyCom/tableau-bord/transaction/mouvement/<int:compte_id>/', views.effectuer_mouvement, name='effectuer_mouvement'),

    # Crédit
    path('GMyCom/tableau-bord/transaction/credit/<int:compte_id>/', views.octroyer_credit, name='octroyer_credit'),

    # Remboursement de crédit
    path('GMyCom/tableau-bord/transaction/remboursement/<int:credit_id>/', views.rembourser_credit, name='rembourser_credit'),

    # Historique des transactions
    path('GMyCom/tableau-bord/transaction/historique/<int:compte_id>/', views.historique_transactions, name='historique_transactions'),
]
