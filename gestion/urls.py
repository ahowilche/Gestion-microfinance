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


    # Historique des transactions
    path('GMyCom/tableau-bord/transaction-data/', views.transactions_data, name='historique_transactions'),
    path('GMyCom/tableau-bord/transaction/historique/', views.historique_page, name='historique_page'),
    
    
    # Crédit
    path('GMyCom/tableau-bord/credits/ajouter/', views.ajouter_credit, name='nouveau_credit'),
    path('GMyCom/tableau-bord/credits/creer/', views.create_credit_api, name='create_credit_api'),
    path('GMyCom/tableau-bord/credits/liste/', views.liste_credits, name='liste_credit'),

    # API endpoints for AJAX calls
    path('GMyCom/tableau-bord/credits/api/liste/', views.api_list_credits, name='api_list_credits'),
    
    #payement
    path('GMyCom/tableau-bord/remboursement/', views.remboursement, name ='page_remboursement'),
    path('GMyCom/tableau-bord/remboursement/api/credits/<int:credit_id>/payments/', views.get_credit_payments, name='api_get_credit_payments'),
    path('GMyCom/tableau-bord/remboursement/api/repayments/record/', views.record_repayment, name='api_record_repayment'),
]

