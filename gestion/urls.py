# Déjà importés :
from django.urls import path
from gestion import views
from .views import AjouterClient, ListeComptesView

urlpatterns = [
    # --- Authentification & tableau de bord ---
    path("", views.index, name="index"),
    path("connexion/", views.login_view, name="login"),
    path('deconnexion/', views.logout_view, name='logout'),
    path("tableau-bord/", views.dashboard, name="dashboard"),

    # --- Zone Clients ---
    path("tableau-bord/liste-client", views.liste_clients, name="liste_clients"),
    path('tableau-bord/clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('tableau-bord/clients/modifier/<int:client_id>/', views.modifier_client, name='modifier_client'),
    path('tableau-bord/compte/ajouter/<int:client_id>/', views.ajouter_compte, name='ajouter_compte'),
    path('tableau-bord/ajouterClient/', AjouterClient.as_view(), name='ajouter_client'),

    # --- Zone Comptes ---
    path('tableau-bord/compte/liste-compte/', ListeComptesView.as_view(), name='liste_compte'),

    # --- Zone Transactions (à ajouter) ---
    # Mouvement (Dépôt / Retrait)
    path('tableau-bord/transaction/', views.effectuer_transaction, name='effectuer_transaction'),
    path('tableau-bord/transaction/mouvement/<int:compte_id>/', views.effectuer_mouvement, name='effectuer_mouvement'),
    # Historique des transactions
    path('tableau-bord/transaction-data/', views.transactions_data, name='historique_transactions'),
    path('tableau-bord/transaction/historique/', views.historique_page, name='historique_page'),
    
    
    # Crédit
    path('tableau-bord/credits/ajouter/', views.ajouter_credit, name='nouveau_credit'),
    path('tableau-bord/credits/creer/', views.create_credit_api, name='create_credit_api'),
    path('tableau-bord/credits/liste/', views.liste_credits, name='liste_credit'),

    # API endpoints for AJAX calls
    path('tableau-bord/credits/api/liste/', views.api_list_credits, name='api_list_credits'),
    
    #payement
    path('tableau-bord/remboursement/', views.remboursement, name ='page_remboursement'),
    path('tableau-bord/remboursement/api/credits/<int:credit_id>/payments/', views.get_credit_payments, name='api_get_credit_payments'),
    path('tableau-bord/remboursement/api/repayments/record/', views.record_repayment, name='api_record_repayment'),
    
    #Rapport
    path('tableau-bord/rapport/', views.rapport, name ='rapport'),
    path('rapports/resume-financier/', views.rapport_resume_financier_pdf, name='rapport_resume_financier'),
    path('rapports/clients/', views.rapport_clients_pdf, name='rapport_clients'),
    path('rapports/transactions/', views.rapport_transactions_pdf, name='rapport_transactions_global'),
    path('rapports/transactions/<int:client_id>/', views.rapport_transactions_pdf, name='rapport_transactions_client'),
    path('rapports/credits/', views.rapport_credits_pdf, name='rapport_credits_global'),
    path('rapports/credits/<int:client_id>/', views.rapport_credits_pdf, name='rapport_credits_client'),
]

