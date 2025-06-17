# gestion/views.py

# --- Imports Django standards ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count, F # <-- Assurez-vous que Sum est bien importé ici
from django.utils.decorators import method_decorator

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import ListView
from django.forms.models import model_to_dict

from django.core.paginator import Paginator
from datetime import datetime, timedelta

from decimal import Decimal, InvalidOperation # <-- Assurez-vous que InvalidOperation est importé
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

import json
import random
import io

from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date
from .models import Agent, Client, Compte, Mouvement, Credit, Remboursement, HistoriqueTransaction
from django.db import transaction

# --- Imports Django REST Framework (AJOUTÉS / VÉRIFIÉS) ---
from rest_framework.decorators import api_view, permission_classes # Importez ceci
from rest_framework.response import Response # Importez ceci
from rest_framework import status # Importez ceci
# from rest_framework.permissions import IsAuthenticated # Décommentez si vous utilisez l'authentification DRF


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.db.models.functions import TruncMonth
plt.switch_backend('Agg') 

from .utils import get_queryset_by_role 




print("--- DEBUG VIEWS.PY: Début du chargement du fichier views.py ---") # Pour le débogage de chargement

# --- Vos autres fonctions de vue existantes (inchangées) ---

def index(request):
    return render(request, "GMyCom/section/index.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    return render(request, 'GMyCom/section/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



## Vues mises à jour avec `get_queryset_by_role`

### Dashboard principal (`dashboard`)
@login_required
def dashboard(request):
    user = request.user
    
    # Utilisation de get_queryset_by_role pour filtrer les données
    clients = get_queryset_by_role(Client, user)
    # Les comptes doivent être liés aux clients que l'utilisateur peut voir
    comptes = Compte.objects.filter(client__in=clients) 
    
    # Pour les mouvements, crédits, et remboursements, on filtre directement par l'agent
    # sauf pour admin/superviseur qui voient tout.
    # get_queryset_by_role gère déjà cette logique.
    mouvements = get_queryset_by_role(Mouvement, user)
    credits = get_queryset_by_role(Credit, user)
    
    # Les remboursements sont liés aux crédits.
    # Si l'agent voit ses crédits, il doit voir les remboursements de ces crédits.
    # Pour admin/superviseur, tous les remboursements.
    if user.is_superuser or user.role == 'admin' or user.role == 'superviseur':
        remboursements = Remboursement.objects.all()
    else: # Agent simple
        remboursements = Remboursement.objects.filter(credit__in=credits)

    context = {
        "user_role": user.role,
        "nombre_clients": clients.count(),
        "nombre_comptes": comptes.count(),
        "solde_total": comptes.aggregate(Sum('solde'))['solde__sum'] or 0,
        "total_depot": mouvements.filter(type_mouvement='DEPOT').aggregate(Sum('montant'))['montant__sum'] or 0,
        "total_retrait": mouvements.filter(type_mouvement='RETRAIT').aggregate(Sum('montant'))['montant__sum'] or 0,
        "total_credit": credits.aggregate(Sum('montant'))['montant__sum'] or 0,
        "total_remboursement": remboursements.aggregate(Sum('montant'))['montant__sum'] or 0,
    }
    return render(request, "dashboard/section/tableauBord.html", context)

##################################################################################
#zone des clients#
##################################################################################

@login_required
def liste_clients(request):
    user = request.user
    # Utilisation de get_queryset_by_role pour filtrer les clients
    clients = get_queryset_by_role(Client, user).prefetch_related('comptes')
    
    clients_data = []
    for client in clients:
        clients_data.append({
            'id': client.id,
            'nom': client.nom,
            'prenom': client.prenom,
            'telephone': client.telephone,
            'adresse': client.adresse,
            'identifiant': client.identifiant,
            'dateInscription': client.date_inscription.strftime('%Y-%m-%d'),
            'comptes': [{
                'id': compte.id,
                'numeroCompte': compte.numero_compte,
                'typeCompte': compte.get_type_compte_display(),
                'solde': float(compte.solde),
            } for compte in client.comptes.all()]
        })
    return render(request, 'dashboard/section/liste_client.html', {
        'clients_json': json.dumps(clients_data),
        'clients': clients, # Passer le QuerySet directement pour la table HTML
        'user_role': user.role, # Utile pour l'affichage conditionnel dans le template
    })
    
    
@require_http_methods(["DELETE"])
@csrf_exempt # Attention au CSRF en production, utilisez @method_decorator(csrf_exempt, name='dispatch') pour CBVs ou Django REST Framework
@login_required # Ajoutez cette ligne
def supprimer_client(request, client_id):
    try:
        client = get_object_or_404(Client, id=client_id)
        user = request.user
        
        # Vérification des permissions avant la suppression
        if user.role == 'admin' or user.role == 'superviseur' or client.agent == user:
            client.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à supprimer ce client.'}, status=403)
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Client non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["PUT"])
@csrf_exempt # Attention au CSRF en production
@login_required # Ajoutez cette ligne
def modifier_client(request, client_id):
    try:
        data = json.loads(request.body)
        client = get_object_or_404(Client, id=client_id)
        user = request.user

        # Vérification des permissions avant la modification
        if not (user.role == 'admin' or user.role == 'superviseur' or client.agent == user):
            return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à modifier ce client.'}, status=403)

        date_inscription = data.get('date_inscription')
        if date_inscription:
            try:
                data['date_inscription'] = datetime.strptime(date_inscription, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
        
        fields = ['nom', 'prenom', 'telephone', 'adresse', 'date_inscription']
        for field in fields:
            if field in data:
                setattr(client, field, data[field])
        client.save()
        return JsonResponse({
            'success': True,
            'client': {
                'nom': client.nom,
                'prenom': client.prenom,
                'telephone': client.telephone,
                'adresse': client.adresse,
                'numero_identifiant': client.identifiant,
                'date_inscription': client.date_inscription.strftime('%Y-%m-%d') if client.date_inscription else None
            }
        })
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Client non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
      
@csrf_exempt # Attention au CSRF en production
@login_required # Ajoutez cette ligne
def ajouter_compte(request, client_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_compte = data.get("typeCompte")
            solde_initial = data.get("soldeInitial")
            
            client = get_object_or_404(Client, id=client_id)
            user = request.user

            # Vérification des permissions
            if not (user.role == 'admin' or user.role == 'superviseur' or client.agent == user):
                return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à ajouter un compte à ce client.'}, status=403)

            if client.comptes.count() >= 2:
                return JsonResponse({'success': False, 'message': 'Un client ne peut avoir que 2 comptes.'}, status=400)
            
            compte = Compte.objects.create(
                client=client,
                type_compte=type_compte,
                solde=solde_initial
            )
            return JsonResponse({'success': True, 'message': 'Compte créé avec succès.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)    


class AjouterClient(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    fields = ['nom', 'prenom', 'email', 'telephone', 'adresse']
    template_name = 'dashboard/section/ajouter_client.html'
    success_url = reverse_lazy('liste_clients')
    success_message = "Le client a été ajouté avec succès"
    
    def form_valid(self, form):
        # L'agent connecté devient l'agent responsable du nouveau client
        form.instance.agent = self.request.user
        return super().form_valid(form)


class ListeComptesView(ListView):
    model = Compte
    template_name = 'dashboard/section/liste_compte.html'
    context_object_name = 'comptes'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        # Utiliser get_queryset_by_role pour obtenir les clients que l'utilisateur peut voir
        clients_visibles = get_queryset_by_role(Client, user)
        # Ensuite, filtrer les comptes en fonction de ces clients
        queryset = super().get_queryset().select_related('client').filter(client__in=clients_visibles)
        
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(numero_compte__icontains=search_query) |
                Q(client__nom__icontains=search_query) |
                Q(client__prenom__icontains=search_query) |
                Q(client__identifiant__icontains=search_query)
            )
        type_compte = self.request.GET.get('type')
        if type_compte in ['epargne', 'courant']:
            queryset = queryset.filter(type_compte=type_compte)
        statut = self.request.GET.get('statut')
        if statut == 'positive':
            queryset = queryset.filter(solde__gte=0)
        elif statut == 'negative':
            queryset = queryset.filter(solde__lt=0)
        
        queryset = queryset.annotate(
            total_depots=Sum('mouvements__montant', filter=Q(mouvements__type_mouvement='DEPOT')),
            total_retraits=Sum('mouvements__montant', filter=Q(mouvements__type_mouvement='RETRAIT'))
        )
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Les totaux doivent aussi refléter les comptes que l'utilisateur peut voir
        clients_visibles = get_queryset_by_role(Client, user)
        comptes_visibles = Compte.objects.filter(client__in=clients_visibles)

        context['solde_total'] = comptes_visibles.aggregate(
            total=Sum('solde')
        )['total'] or 0
        context['search_query'] = self.request.GET.get('q', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        context['user_role'] = user.role # Ajouter le rôle pour le template
        return context


##################################################################################
#zone des Transactions#
##################################################################################

@login_required
def effectuer_transaction(request):
    user = request.user
    # Filtrer les comptes que l'utilisateur peut voir pour la sélection
    clients_visibles = get_queryset_by_role(Client, user)
    comptes = Compte.objects.select_related('client').filter(client__in=clients_visibles)
    
    return render(request, 'dashboard/section/transaction.html', {
        'comptes': comptes,
        'user_role': user.role,
    })

@require_http_methods(["POST"])
@login_required
def effectuer_mouvement(request, compte_id):
    try:
        compte = get_object_or_404(Compte, id=compte_id)
        user = request.user
        
        # Vérification de permission: un agent ne peut faire des mouvements que sur les comptes de ses clients
        if not (user.role == 'admin' or user.role == 'superviseur' or compte.client.agent == user):
            return JsonResponse({"success": False, "message": "Vous n'êtes pas autorisé à effectuer une transaction sur ce compte."}, status=403)

        type_mouvement = request.POST.get("type_mouvement")
        try:
            montant = Decimal(str(request.POST.get("amount")))
            if montant <= 0:
                return JsonResponse({"success": False, "message": "Le montant doit être positif"}, status=400)
        except (InvalidOperation, TypeError):
            return JsonResponse({"success": False, "message": "Montant invalide"}, status=400)
        
        if type_mouvement not in ["DEPOT", "RETRAIT"]:
            return JsonResponse({"success": False, "message": "Type de mouvement invalide"}, status=400)
        
        with transaction.atomic():
            mouvement = Mouvement.objects.create(
                compte=compte,
                agent=user, # L'agent qui effectue le mouvement
                type_mouvement=type_mouvement,
                montant=montant,
            )
            # Votre modèle Mouvement met déjà à jour le solde du compte dans sa méthode save
            
            HistoriqueTransaction.objects.create(
                compte=compte,
                type_operation=type_mouvement,
                montant=montant,
                description=f"{type_mouvement} effectué par {user.get_full_name()}"
            )
        return JsonResponse({
            "success": True,
            "message": "Transaction effectuée avec succès",
            "new_balance": str(compte.solde)
        })
    except ValueError as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": "Erreur serveur : " + str(e)}, status=500)


@csrf_exempt
@require_GET
@login_required # Assurez-vous que l'utilisateur est connecté
def transactions_data(request):
    user = request.user
    # Appliquer le filtrage par rôle en premier
    transactions = get_queryset_by_role(HistoriqueTransaction, user).select_related('compte__client')
    
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    type_filter = request.GET.get('type')
    client_filter = request.GET.get('client', '').strip().lower()
    min_amount = request.GET.get('minAmount')
    max_amount = request.GET.get('maxAmount')

    if start_date:
        start = parse_date(start_date)
        if start:
            transactions = transactions.filter(date__date__gte=start)
    if end_date:
        end = parse_date(end_date)
        if end:
            transactions = transactions.filter(date__date__lte=end)
    if type_filter:
        transactions = transactions.filter(type_operation__iexact=type_filter.upper())
    if client_filter:
        transactions = transactions.filter(
            Q(compte__client__nom__icontains=client_filter) |
            Q(compte__client__prenom__icontains=client_filter)
        )
    if min_amount:
        transactions = transactions.filter(montant__gte=min_amount)
    if max_amount:
        transactions = transactions.filter(montant__lte=max_amount)
    
    data = []
    for t in transactions.order_by('-date'):
        data.append({
            "id": t.id,
            "date": t.date.strftime('%Y-%m-%d'),
            "type": t.type_operation.lower(),
            "client": f"{t.compte.client.nom} {t.compte.client.prenom}",
            "account": t.compte.numero_compte,
            "amount": float(t.montant),
            "description": t.description,
            "balanceAfter": float(t.compte.solde) # Attention: solde du compte au moment de la requête, pas de la transaction
        })
    
    total_depots = transactions.filter(type_operation="DEPOT").aggregate(total=Sum('montant'))['total'] or 0
    total_retraits = transactions.filter(type_operation="RETRAIT").aggregate(total=Sum('montant'))['total'] or 0
    net = total_depots - total_retraits
    
    stats = {
        "totalTransactions": transactions.count(),
        "totalDeposits": total_depots,
        "totalWithdrawals": total_retraits,
        "netBalance": net,
        "transactions": data
    }
    return JsonResponse(stats, safe=False)

@login_required
def historique_page(request):
    # Cette vue renvoie juste le template, le filtrage se fait dans transactions_data via JS
    return render(request, "dashboard/section/historique.html", {'user_role': request.user.role})

##################################################################################
#zone des Crédits#
##################################################################################

@login_required # Assurez-vous que l'utilisateur est connecté pour accéder à ces vues
def credit(request):
    return render(request, "dashboard/section/nouveau_credit.html", {'user_role': request.user.role})

@login_required
def ajouter_credit(request):
    user = request.user
    # Filtrer les comptes visibles pour la sélection de crédit
    clients_visibles = get_queryset_by_role(Client, user)
    comptes = Compte.objects.filter(client__in=clients_visibles)
    
    context = {
        'comptes': comptes,
        'user_role': user.role,
    }
    return render(request, 'dashboard/section/nouveau_credit.html', context)

# NOTE: Pour `api_view`, assurez-vous d'avoir Django REST Framework installé (`pip install djangorestframework`)
# et `rest_framework` ajouté à `INSTALLED_APPS` dans settings.py.
# Si ce n'est pas le cas, vous devrez utiliser des JsonResponse directes et `json.loads(request.body)`
# et retirer les imports de rest_framework.
# Pour simplifier, je vais adapter la fonction `record_repayment` à une approche sans DRF ici,
# mais sachez que DRF est la meilleure pratique pour les APIs.

# from rest_framework.decorators import api_view # À décommenter si vous utilisez DRF
# from rest_framework.response import Response # À décommenter si vous utilisez DRF
# from rest_framework import status # À décommenter si vous utilisez DRF

@require_POST
@csrf_exempt # Continuez de l'utiliser si pas de jeton CSRF, mais à revoir pour la production !
@login_required # L'agent qui crée le crédit doit être connecté
def create_credit_api(request):
    print("--- DEBUG: Entrée dans create_credit_api ---")

    # Si vous n'utilisez pas DRF, utilisez request.body et json.loads
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        print("DEBUG: Erreur de décodage JSON.")
        return JsonResponse({'error': 'Données JSON invalides.'}, status=400)

    print(f"DEBUG: Données reçues: {data}")

    try:
        compte_id = data.get('compte')
        raw_montant = data.get('montant')
        raw_taux_interet = data.get('taux_interet')
        raw_duree_mois = data.get('duree_mois') # Renommé pour clarté avant conversion

        if not all([compte_id, raw_montant, raw_taux_interet, raw_duree_mois]):
            print("DEBUG: Champs obligatoires manquants pour le crédit.")
            return JsonResponse({'error': 'Tous les champs obligatoires doivent être remplis.'}, status=400)

        try:
            montant = Decimal(str(raw_montant))
            taux_interet = Decimal(str(raw_taux_interet))
            # FIX: Convertir duree_mois en int ici
            duree_mois = int(raw_duree_mois)

            if montant <= 0 or taux_interet < 0 or duree_mois <= 0:
                print(f"DEBUG: Validation échouée: montant={montant}, taux={taux_interet}, duree={duree_mois}")
                return JsonResponse({'error': 'Montant, taux ou durée invalide. Ils doivent être positifs.'}, status=400)
        except (InvalidOperation, ValueError): # Ajout de ValueError pour int()
            print(f"DEBUG: Erreur de conversion du montant/taux/durée: '{raw_montant}', '{raw_taux_interet}', '{raw_duree_mois}'")
            return JsonResponse({'error': 'Le montant, le taux d\'intérêt ou la durée n\'est pas un nombre valide.'}, status=400)

        compte = get_object_or_404(Compte, id=compte_id)
        user = request.user # L'agent qui crée le crédit

        # Vérification des permissions
        if not (user.role == 'admin' or user.role == 'superviseur' or (hasattr(compte.client, 'agent') and compte.client.agent == user)):
            return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à octroyer un crédit sur ce compte.'}, status=403)

        with transaction.atomic():
            credit = Credit.objects.create(
                compte=compte,
                agent=user, # Assigner l'agent connecté au crédit
                montant=montant,
                taux_interet=taux_interet,
                duree_mois=duree_mois,
            )
            print(f"DEBUG: Crédit créé : Numéro={credit.numero_credit}")

        return JsonResponse({'message': 'Crédit créé avec succès !', 'numero_credit': credit.numero_credit}, status=201)

    except Exception as e:
        import traceback
        print(f"--- ERREUR INATTENDUE DANS CREATE_CREDIT_API: {e} ---")
        traceback.print_exc()
        return JsonResponse({'error': 'Une erreur interne est survenue.'}, status=500)


@login_required
def liste_credits(request):
    return render(request, 'dashboard/section/liste_credit.html', {'user_role': request.user.role})

@require_GET
@login_required
def api_list_comptes(request):
    user = request.user
    # Filtrer les comptes visibles pour l'API
    clients_visibles = get_queryset_by_role(Client, user)
    comptes = Compte.objects.select_related('client').filter(client__in=clients_visibles)

    comptes_data = []
    for compte in comptes:
        comptes_data.append({
            'id': compte.id,
            'numero_compte': compte.numero_compte,
            'client_nom_complet': f"{compte.client.nom} {compte.client.prenom}" if hasattr(compte, 'client') and compte.client else "Client Inconnu",
            'solde': str(compte.solde),
        })
    return JsonResponse(comptes_data, safe=False)

@require_GET
@login_required
def api_list_credits(request):
    user = request.user
    # Filtrer les crédits en fonction du rôle de l'utilisateur
    credits = get_queryset_by_role(Credit, user).select_related('compte__client').filter(
        statut__in=['EN_COURS', 'EN_RETARD']
    ).annotate(
        total_rembourse_calcule = Sum('remboursements__montant')
    ).order_by('-date_octroi')
    
    credits_data = []
    for credit in credits:
        client_full_name = "Client Inconnu"
        account_number = "N/A"
        if hasattr(credit, 'compte') and credit.compte:
            account_number = credit.compte.numero_compte
            if hasattr(credit.compte, 'client') and credit.compte.client:
                client_full_name = f"{credit.compte.client.nom} {credit.compte.client.prenom}"
        
        paid_amount = credit.total_rembourse_calcule if credit.total_rembourse_calcule is not None else Decimal('0.00')
        remaining_amount = credit.montant - paid_amount # Ceci est le montant initial - remb. Pas le montant total dû avec intérêts.
        
        credits_data.append({
            'id': str(credit.id),
            'numero_credit': credit.numero_credit,
            'client_nom_complet': client_full_name,
            'numero_compte': account_number,
            'montant': str(credit.montant),
            'taux_interet': str(credit.taux_interet),
            'duree_mois': credit.duree_mois,
            'date_octroi': credit.date_octroi.strftime("%Y-%m-%d"),
            'statut': credit.statut,
            'montant_rembourse': str(paid_amount),
            'montant_restant_du': str(remaining_amount), # Attention: ceci est 'montant initial - remboursé'
            # 'type_credit': getattr(credit, 'type_credit', None), # Ces champs ne sont pas dans votre modèle Credit fourni
            # 'objet_credit': getattr(credit, 'objet_credit', None), # Ces champs ne sont pas dans votre modèle Credit fourni
        })
    return JsonResponse(credits_data, safe=False)


##################################################################################
#zone des remboursements#
##################################################################################

@login_required
def remboursement(request):
    """
    Rend la page HTML principale pour l'interface de remboursement de crédit.
    """
    return render(request, 'dashboard/section/remboursement.html', {'user_role': request.user.role})

@require_GET
@login_required
def get_credit_payments(request, credit_id):
    """
    Retourne l'historique des remboursements pour un crédit donné,
    avec une vérification de permission.
    """
    credit = get_object_or_404(Credit, id=credit_id)
    user = request.user

    # Vérification des permissions
    # Un superviseur ou admin peut voir tous les paiements d'un crédit.
    # Un agent ne peut voir les paiements que pour les crédits qu'il a octroyés.
    if not (user.role == 'admin' or user.role == 'superviseur' or credit.agent == user):
        return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à voir les paiements de ce crédit.'}, status=403)

    payments = credit.remboursements.all().order_by('-date')
    data = []
    for payment in payments:
        data.append({
            'id': str(payment.id),
            'montant': str(payment.montant),
            'date_paiement': payment.date.isoformat(),
            'methode_paiement': payment.methode_paiement, # Utilisez le champ du modèle
            'reference': payment.numero_remboursement,
            'notes': payment.notes, # Utilisez le champ du modèle
        })
    return JsonResponse(data, safe=False)


# --- Fonction record_repayment (MODIFIÉE) ---
# J'ai supprimé @api_view, @require_POST et @csrf_exempt
# pour revenir à une approche purement Django si vous n'utilisez pas DRF.
# Si vous utilisez DRF, réactivez @api_view et les imports de DRF.

@require_POST # Utiliser ce décorateur si c'est une vue Django classique (pas DRF)
@csrf_exempt # Pour le développement, à remplacer par un jeton CSRF en production
@login_required # L'agent qui enregistre le remboursement doit être connecté
def record_repayment(request):
    print("--- DEBUG: Entrée dans record_repayment ---")

    # Si pas de DRF, utilisez request.POST pour les données de formulaire, ou json.loads(request.body) pour les APIs JSON
    try:
        # Supposons que le front-end envoie du JSON via fetch/axios.
        data = json.loads(request.body)
        print(f"DEBUG: Données reçues via json.loads(request.body): {data}")
    except json.JSONDecodeError:
        print("DEBUG: Erreur de décodage JSON pour le remboursement.")
        return JsonResponse({"error": "Données JSON invalides."}, status=400)


    try:
        credit_id = data.get('credit_id')
        montant_str = data.get('montant')
        date_paiement_str = data.get('date_paiement')
        methode_paiement = data.get('methode_paiement', 'INCONNU')
        reference = data.get('reference', '')
        notes = data.get('notes', '')

        print(f"DEBUG: credit_id={credit_id}, montant_str='{montant_str}', date_paiement_str='{date_paiement_str}'")

        if not all([credit_id, montant_str, date_paiement_str]):
            print("DEBUG: Champs obligatoires manquants.")
            return JsonResponse(
                {"error": "Les champs 'credit_id', 'montant' et 'date_paiement' sont obligatoires."},
                status=400
            )

        try:
            montant = Decimal(str(montant_str))
            if montant <= 0:
                print("DEBUG: Montant de remboursement <= 0.")
                return JsonResponse({"error": "Le montant du remboursement doit être positif."}, status=400)
        except (InvalidOperation, TypeError):
            print(f"DEBUG: Erreur de conversion du montant: '{montant_str}'")
            return JsonResponse({"error": "Montant invalide ou non numérique."}, status=400)

        try:
            date_paiement = datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
            date_paiement_dt = timezone.make_aware(datetime.combine(date_paiement, datetime.min.time()))
            print(f"DEBUG: Date de paiement convertie: {date_paiement_dt}")
        except ValueError:
            print(f"DEBUG: Format de date invalide: '{date_paiement_str}'")
            return JsonResponse({"error": "Format de date invalide. Utilisez YYYY-MM-DD."}, status=400)

        credit = get_object_or_404(Credit, id=credit_id)
        user = request.user # L'agent qui enregistre le remboursement
        print(f"DEBUG: Crédit trouvé: ID={credit.id}, Numéro={credit.numero_credit}")

        # Vérification des permissions
        if not (user.role == 'admin' or user.role == 'superviseur' or credit.agent == user):
            return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à enregistrer un remboursement pour ce crédit.'}, status=403)

        # Calcul de la part principal/intérêt (Simplification ici, à adapter pour une vraie amortisation)
        montant_principal_remb = montant
        montant_interet_remb = Decimal('0.00') # Si vous ne calculez pas les intérêts ici

        with transaction.atomic():
            print("DEBUG: Début de la transaction atomique pour le remboursement.")
            remboursement = Remboursement.objects.create(
                credit=credit,
                agent=user, # Assignez l'agent connecté
                montant=montant,
                montant_principal=montant_principal_remb,
                montant_interet=montant_interet_remb,
                date=date_paiement_dt,
                methode_paiement=methode_paiement,
                reference=reference,
                notes=notes,
            )
            print(f"DEBUG: Remboursement créé : ID={remboursement.id}, Montant={remboursement.montant}")

            # Le modèle Remboursement a déjà une logique de save qui met à jour le statut du crédit
            # et le solde du compte dans sa propre méthode save. Assurez-vous que cette logique est correcte.
            # J'ai commenté et laissé le code ci-dessous pour information, mais il est possible qu'il soit redondant
            # si Remboursement.save() le fait déjà.

            # credit.montant_rembourse = (credit.montant_rembourse or Decimal('0.00')) + montant
            # print(f"DEBUG: Nouveau montant remboursé pour le crédit {credit.id}: {credit.montant_rembourse}")

            # # Mise à jour du statut du crédit (généralement géré par la save de Remboursement)
            # montant_total_du = credit.montant # À ajuster si le montant total dû inclut les intérêts
            # if credit.montant_rembourse >= montant_total_du:
            #     credit.statut = 'REMBOURSE'
            #     print(f"DEBUG: Statut du crédit {credit.id} mis à 'REMBOURSE'.")
            # else:
            #     if credit.statut not in ['EN_COURS', 'EN_RETARD']:
            #         credit.statut = 'EN_COURS'
            #     print(f"DEBUG: Statut du crédit {credit.id} reste: {credit.statut}.")
            # credit.save()

            print("DEBUG: Transaction atomique terminée avec succès.")

        return JsonResponse(
            {"message": "Remboursement enregistré avec succès", "id": str(remboursement.id)},
            status=201 # HTTP_201_CREATED
        )

    except Credit.DoesNotExist:
        print(f"--- ERREUR: Crédit introuvable pour ID: {credit_id} ---")
        return JsonResponse({"error": "Crédit introuvable."}, status=404)
    except ValueError as e:
        print(f"--- ERREUR DE DONNÉES ou DE CONVERSION: {e} ---")
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        import traceback
        print(f"--- ERREUR INATTENDUE DANS LE BLOC TRY/EXCEPT PRINCIPAL: {e} ---")
        traceback.print_exc()
        return JsonResponse({"error": f"Une erreur interne est survenue sur le serveur: {e}"},
                             status=500)

print("--- DEBUG VIEWS.PY: Fin du chargement du fichier views.py ---")



  
##################################################################################
#zone des rapports#
##################################################################################
#########################################  RAPPORT  ##############################  

try:
    from .models import Client, Compte, Credit, Remboursement, Mouvement, HistoriqueTransaction
    print("DEBUG: Modèles Django importés avec succès.")
except ImportError as e:
    print(f"ATTENTION : Les modèles Django n'ont pas pu être importés ({e}). Le rapport utilisera des données factices.")
    # Définitions de classes factices pour le développement/test sans DB connectée
    class DummyQuerySet:
        def count(self): return 0
        def aggregate(self, *args, **kwargs): return {'total': Decimal('0.00')}
        def filter(self, *args, **kwargs): return self
        def values(self, *args, **kwargs): return []
        def all(self): return []
        def order_by(self, *args, **kwargs): return self

    class DummyModel:
        objects = DummyQuerySet()

    class DummyAccount:
        def __init__(self, num, client_obj=None, solde=Decimal('0.00')):
            self.numero_compte = num
            self.client = client_obj
            self.solde = solde
        def get_type_compte_display(self): return "Épargne" # Valeur par défaut pour dummy

    class DummyClient:
        def __init__(self, identifiant, nom, prenom, tel, email, date_insc):
            self.identifiant = identifiant
            self.nom = nom
            self.prenom = prenom
            self.telephone = tel
            self.email = email
            self.date_inscription = date_insc
            self._comptes = DummyQuerySet() # Simuler un related manager
        
        @property
        def comptes(self):
            # Pour la démo, on peut retourner un queryset factice ou même une liste de comptes factices
            # Ici, on simule qu'un client dummy a toujours 2 comptes dummy
            if not self._comptes.all(): # Éviter de recréer si déjà fait
                self._comptes = DummyQuerySet()
                self._comptes._data = [DummyAccount(f"{self.identifiant}-ACC1", self), DummyAccount(f"{self.identifiant}-ACC2", self)]
                self._comptes.all = lambda: self._comptes._data # Simuler .all()
                self._comptes.count = lambda: len(self._comptes._data) # Simuler .count()
            return self._comptes

    class DummyTransaction:
        def __init__(self, date, type_op, montant, compte_obj, description=""):
            self.date = date
            self.type_operation = type_op
            self.montant = Decimal(montant)
            self.compte = compte_obj
            self.description = description
        def get_type_operation_display(self):
            return self.type_operation.capitalize()

    # Assigner les classes factices
    Client = DummyModel
    Compte = DummyModel
    Credit = DummyModel
    Remboursement = DummyModel
    Mouvement = DummyModel
    HistoriqueTransaction = DummyModel
    


# --- Styles pour les paragraphes ---
styles = getSampleStyleSheet()

styles['Normal'].fontName = 'Helvetica'
styles['Normal'].fontSize = 10
styles['Normal'].leading = 12

styles.add(ParagraphStyle(name='ReportTitle', fontName='Helvetica-Bold', fontSize=24, spaceAfter=20, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='SectionTitle', fontName='Helvetica-Bold', fontSize=16, spaceBefore=20, spaceAfter=10, alignment=TA_LEFT))

style_normal = styles['Normal']
style_center = ParagraphStyle(name='NormalCenter', parent=styles['Normal'])
style_center.alignment = TA_CENTER
styles.add(style_center)

style_right = ParagraphStyle(name='NormalRight', parent=styles['Normal'])
style_right.alignment = TA_RIGHT
styles.add(style_right)

# Style pour le texte des cellules du tableau, avec une taille de police plus petite si nécessaire
styles.add(ParagraphStyle(name='TableCellText', fontName='Helvetica', fontSize=8.5, leading=10, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='TableCellRight', fontName='Helvetica', fontSize=8.5, leading=10, alignment=TA_RIGHT))


def generate_pdf_response(buffer, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    buffer.seek(0)
    response.write(buffer.getvalue())
    return response

def create_chart_image(data, labels, title, chart_type='pie', colors=None):
    buffer = io.BytesIO()
    plt.figure(figsize=(6, 4))

    if colors is None:
        colors = plt.cm.Paired.colors

    if chart_type == 'pie':
        plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.axis('equal')
    elif chart_type == 'bar':
        plt.bar(labels, data, color=colors if isinstance(colors, list) else 'skyblue')
        plt.ylabel('Montant')
        plt.xticks(rotation=45, ha='right')
    
    plt.title(title)
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer


## Rapports avec filtrage par rôle

### Page de sélection de rapport


@login_required # Assurez-vous que l'utilisateur est connecté
def rapport(request):
    return render(request, 'dashboard/section/rapport.html', {'user_role': request.user.role})


@login_required # Ajoutez ce décorateur
def rapport_resume_financier_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []

    user = request.user # Obtenez l'utilisateur courant

    story.append(Paragraph("<b>RÉSUMÉ FINANCIER GLOBAL</b>", styles['ReportTitle']))
    story.append(Paragraph(f"Date de Génération : {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", style_right))
    story.append(Spacer(1, 0.4 * inch))

    # Initialisation des totaux
    total_clients = 0
    total_comptes = 0
    total_solde_comptes = Decimal('0.00')
    total_credits_octroyes = Decimal('0.00')
    total_credits_rembourses = Decimal('0.00')
    total_depots = Decimal('0.00')
    total_retraits = Decimal('0.00')

    try:
        # Appliquez le filtrage par rôle à chaque QuerySet
        clients_queryset = get_queryset_by_role(Client, user)
        comptes_queryset = Compte.objects.filter(client__in=clients_queryset) # Les comptes sont liés aux clients visibles
        credits_queryset = get_queryset_by_role(Credit, user)
        # Les remboursements dépendent des crédits, et Mouvement de l'agent si ce n'est pas un admin/superviseur
        mouvements_queryset = get_queryset_by_role(Mouvement, user)
        
        # Pour les remboursements, si l'utilisateur est un agent, il ne voit que les remboursements de SES crédits.
        if user.is_superuser or user.role in ['admin', 'superviseur']:
            remboursements_queryset = Remboursement.objects.all()
        else: # Agent simple
            remboursements_queryset = Remboursement.objects.filter(credit__in=credits_queryset)

        total_clients = clients_queryset.count()
        total_comptes = comptes_queryset.count()
        total_solde_comptes = comptes_queryset.aggregate(total=Sum('solde'))['total'] or Decimal('0.00')
        total_credits_octroyes = credits_queryset.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        total_credits_rembourses = remboursements_queryset.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        total_depots = mouvements_queryset.filter(type_mouvement='DEPOT').aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        total_retraits = mouvements_queryset.filter(type_mouvement='RETRAIT').aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

    except AttributeError: # Si les modèles sont factices
        total_clients = 125
        total_comptes = 200
        total_solde_comptes = Decimal('1500000.00')
        total_credits_octroyes = Decimal('850000.00')
        total_credits_rembourses = Decimal('620000.00')
        total_depots = Decimal('2100000.00')
        total_retraits = Decimal('700000.00')
        print("INFO : Utilisation de données factices pour le rapport financier car les modèles ne sont pas accessibles.")


    story.append(Paragraph("<b>1. Métriques Clés</b>", styles['SectionTitle']))
    data_metrics = [
        ["Métrique", "Valeur"],
        ["Total Clients", total_clients],
        ["Total Comptes", total_comptes],
        ["Solde Total des Comptes", f"{total_solde_comptes:,.2f} XOF".replace(',', ' ').replace('.', ',')],
        ["Crédits Octroyés", f"{total_credits_octroyes:,.2f} XOF".replace(',', ' ').replace('.', ',')],
        ["Crédits Remboursés", f"{total_credits_rembourses:,.2f} XOF".replace(',', ' ').replace('.', ',')],
        ["Total Dépôts", f"{total_depots:,.2f} XOF".replace(',', ' ').replace('.', ',')],
        ["Total Retraits", f"{total_retraits:,.2f} XOF".replace(',', ' ').replace('.', ',')],
    ]
    table_metrics_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#e0f2fe')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93c5fd')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1d4ed8')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])
    table_metrics = Table(data_metrics, colWidths=[3.5*inch, 3.5*inch])
    table_metrics.setStyle(table_metrics_style)
    story.append(table_metrics)
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("<b>2. Répartition des Soldes par Type de Compte</b>", styles['SectionTitle']))
    labels_solde = []
    data_solde = []
    try:
        if Compte.objects:
            # Filtrer les comptes visibles pour le graphique de solde
            solde_par_type = comptes_queryset.values('type_compte').annotate(total_solde=Sum('solde'))
            labels_solde = [item['type_compte'].capitalize() for item in solde_par_type]
            data_solde = [float(item['total_solde']) for item in solde_par_type]
    except AttributeError:
        labels_solde = ['Épargne', 'Courant']
        data_solde = [900000, 600000]
        print("INFO : Utilisation de données factices pour le solde par type car les modèles ne sont pas accessibles.")

    if data_solde:
        chart_solde_buffer = create_chart_image(data_solde, labels_solde, "Solde par Type de Compte", 'pie', colors=['#3b82f6', '#10b981', '#f59e0b'])
        img_solde = Image(chart_solde_buffer)
        img_solde.width = 3.5 * inch
        img_solde.height = 2.5 * inch
        story.append(img_solde)
    else:
        story.append(Paragraph("Pas de données de solde de compte pour le graphique.", style_normal))
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("<b>3. Comparaison des Dépôts et Retraits</b>", styles['SectionTitle']))
    if total_depots > 0 or total_retraits > 0:
        chart_mouvements_buffer = create_chart_image(
            [float(total_depots), float(total_retraits)],
            ['Dépôts', 'Retraits'],
            "Dépôts vs Retraits",
            'bar',
            colors=['#10b981', '#ef4444']
        )
        img_mouvements = Image(chart_mouvements_buffer)
        img_mouvements.width = 3.5 * inch
        img_mouvements.height = 2.5 * inch
        story.append(img_mouvements)
    else:
        story.append(Paragraph("Pas de données de mouvement pour le graphique.", style_normal))
    story.append(Spacer(1, 0.4 * inch))

    story.append(Paragraph("<b>4. Transactions Récentes</b>", styles['SectionTitle']))
    recent_transactions = []
    try:
        if HistoriqueTransaction.objects:
            # Filtrer les transactions récentes par rôle
            recent_transactions = get_queryset_by_role(HistoriqueTransaction, user).order_by('-date')[:10]
    except AttributeError:
        print("INFO : Utilisation de données factices pour les transactions récentes car le modèle n'est pas accessible.")
        # Utiliser les DummyTransaction et DummyAccount avec DummyClient comme base
        dummy_client1 = DummyClient('CL001', 'Dupont', 'Jean', '0788123456', 'jean.dupont@example.com', timezone.now() - datetime.timedelta(days=300))
        dummy_account1 = dummy_client1.comptes.all()[0] # Obtenir un compte factice pour le client factice

        recent_transactions = [
            DummyTransaction(timezone.now() - datetime.timedelta(days=1), 'DEPOT', '50000.00', dummy_account1, 'Dépôt client A'),
            DummyTransaction(timezone.now() - datetime.timedelta(days=2), 'RETRAIT', '15000.00', dummy_account1, 'Retrait client B'),
            DummyTransaction(timezone.now() - datetime.timedelta(days=3), 'VIREMENT', '25000.00', dummy_account1, 'Virement vers C-003'),
            DummyTransaction(timezone.now() - datetime.timedelta(days=4), 'DEPOT', '10000.00', dummy_account1, 'Dépôt client C'),
        ]

    if recent_transactions:
        data_transactions = [
            [
                Paragraph("<b>Date</b>", style_center),
                Paragraph("<b>Type</b>", style_center),
                Paragraph("<b>Montant (XOF)</b>", style_center),
                Paragraph("<b>Compte</b>", style_center),
                Paragraph("<b>Description</b>", style_center)
            ]
        ]
        for t in recent_transactions:
            data_transactions.append([
                Paragraph(t.date.strftime("%Y-%m-%d %H:%M"), styles['TableCellText']),
                Paragraph(t.get_type_operation_display(), styles['TableCellText']),
                Paragraph(f"{t.montant:,.2f}".replace(',', ' ').replace('.', ','), styles['TableCellRight']),
                Paragraph(t.compte.numero_compte, styles['TableCellText']),
                Paragraph(t.description or "N/A", styles['TableCellText'])
            ])

        table_transactions = Table(data_transactions, colWidths=[
            1.6*inch,   # Date
            1.2*inch,   # Type
            1.4*inch,   # Montant
            1.6*inch,   # Compte
            3.89*inch   # Description
        ])
        
        table_transactions.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0ea5e9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#e0f2fe')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7dd3fc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284c7')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(table_transactions)
    else:
        story.append(Paragraph("Aucune transaction récente à afficher.", style_normal))
    story.append(Spacer(1, 0.4 * inch))

    doc.build(story)
    return generate_pdf_response(buffer, "Resume_Financier_Global")


@login_required # Ajoutez ce décorateur
def rapport_clients_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []

    user = request.user # Obtenez l'utilisateur courant

    story.append(Paragraph("<b>RAPPORT DES CLIENTS</b>", styles['ReportTitle']))
    story.append(Spacer(1, 0.4 * inch))

    clients = []
    try:
        if Client.objects:
            # Appliquez le filtrage par rôle pour les clients
            clients = get_queryset_by_role(Client, user).order_by('nom', 'prenom')
    except AttributeError:
        print("INFO : Utilisation de données factices pour les clients car le modèle n'est pas accessible.")
        clients = [
            DummyClient('CL001', 'Dupont', 'Jean', '0788123456', 'jean.dupont@example.com', timezone.now() - datetime.timedelta(days=300)),
            DummyClient('CL002', 'Martin', 'Sophie', '0788654321', 'sophie.martin@example.com', timezone.now() - datetime.timedelta(days=150)),
        ]

    if not clients:
        story.append(Paragraph("Aucun client trouvé.", style_normal))
    else:
        data = [
            [
                Paragraph("<b>Identifiant</b>", style_center),
                Paragraph("<b>Nom Complet</b>", style_center),
                Paragraph("<b>Téléphone</b>", style_center),
                Paragraph("<b>Email</b>", style_center),
                Paragraph("<b>Date Inscription</b>", style_center),
                Paragraph("<b>Total Comptes</b>", style_center)
            ]
        ]
        for client in clients:
            total_comptes_client = 0
            try:
                # Filtrer les comptes de ce client que l'utilisateur peut voir
                # Ou s'assurer que .comptes est déjà filtré si client vient d'un get_queryset_by_role pour Client
                # Le plus simple est de s'appuyer sur le filtrage des clients, et que les comptes sont liés à ces clients
                if client.id: # S'assurer que ce n'est pas un DummyClient sans réel ID
                    total_comptes_client = Compte.objects.filter(client=client).count()
                    if not (user.is_superuser or user.role in ['admin', 'superviseur'] or client.agent == user):
                        # Si l'utilisateur n'est pas censé voir ce client, il ne devrait pas apparaître ici.
                        # Mais get_queryset_by_role(Client, user) gère déjà cela.
                        # Cette ligne est plutôt une double vérification ou pour un cas où la relation agent-client n'est pas directe.
                        total_comptes_client = 0 # Ou gérer l'exclusion de la ligne entière
                else: # Pour les DummyClient
                    total_comptes_client = client.comptes.count() 
            except AttributeError:
                total_comptes_client = client.comptes_count() 
            
            data.append([
                Paragraph(client.identifiant, styles['TableCellText']),
                Paragraph(f"{client.nom} {client.prenom}", styles['TableCellText']),
                Paragraph(client.telephone, styles['TableCellText']),
                Paragraph(client.email or "N/A", styles['TableCellText']),
                Paragraph(client.date_inscription.strftime("%Y-%m-%d"), styles['TableCellText']),
                Paragraph(str(total_comptes_client), styles['TableCellText'])
            ])
        
        table = Table(data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 2.5*inch, 1.2*inch, 1.1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (5,1), (5,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#dcfce7')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#86efac')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#22c55e')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(table)
    
    doc.build(story)
    return generate_pdf_response(buffer, "Rapport_Clients")


@login_required
def rapport_transactions_pdf(request, client_id=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []

    user = request.user # Obtenez l'utilisateur courant

    title_text = "<b>RAPPORT GLOBAL DES TRANSACTIONS</b>"
    transactions = []

    try:
        # Obtenez le QuerySet de base pour les transactions filtré par rôle
        base_transactions_qs = get_queryset_by_role(HistoriqueTransaction, user)

        if client_id:
            # Si un client_id est spécifié, nous devons nous assurer que l'utilisateur peut voir ce client
            client_qs_by_role = get_queryset_by_role(Client, user)
            try:
                client = client_qs_by_role.get(pk=client_id)
                # Si le client est visible par l'utilisateur, filtrez les transactions pour ce client
                transactions = base_transactions_qs.filter(compte__client=client).order_by('-date')
                title_text = f"<b>RAPPORT DES TRANSACTIONS POUR {client.nom.upper()} {client.prenom.upper()}</b>"
            except Client.DoesNotExist:
                transactions = []
                title_text = f"<b>RAPPORT DES TRANSACTIONS (CLIENT ID {client_id} INTROUVABLE ou non autorisé)</b>"
                print(f"INFO : Client avec ID {client_id} non trouvé ou non autorisé pour l'utilisateur {user.username}.")
        else:
            # Si pas de client_id, prendre toutes les transactions visibles par l'utilisateur
            transactions = base_transactions_qs.all().order_by('-date')
    except AttributeError:
        # Données factices en cas de problème d'accès aux modèles Django
        print("INFO : Modèle HistoriqueTransaction ou Client non accessible. Utilisation de données factices.")
        
        # Filtrage des données factices basé sur le rôle ou l'ID client factice
        all_dummy_transactions = HistoriqueTransaction.objects.all() # C'est le DummyQuerySet global

        if client_id:
            # Simuler le filtrage pour un client_id spécifique parmi les dummy clients
            dummy_clients_for_user = get_queryset_by_role(Client, user).all()
            target_dummy_client = next((c for c in dummy_clients_for_user if str(c.id) == str(client_id)), None)

            if target_dummy_client:
                # Filtrer les transactions factices par les comptes du client factice
                transactions = [
                    t for t in all_dummy_transactions if hasattr(t, 'compte') and hasattr(t.compte, 'client') and t.compte.client.id == target_dummy_client.id
                ]
                if transactions:
                    title_text = f"<b>RAPPORT DES TRANSACTIONS POUR {target_dummy_client.nom.upper()} {target_dummy_client.prenom.upper()} (Données factices)</b>"
                else:
                    title_text = f"<b>RAPPORT DES TRANSACTIONS POUR CLIENT ID {client_id} (Aucune transaction factice trouvée)</b>"
            else:
                transactions = []
                title_text = f"<b>RAPPORT DES TRANSACTIONS (CLIENT ID {client_id} INTROUVABLE ou non autorisé pour données factices)</b>"
        else:
            # Pour le rapport global factice, filtrer par les clients que l'utilisateur peut voir
            clients_visible_for_user = get_queryset_by_role(Client, user).all()
            visible_client_ids = {c.id for c in clients_visible_for_user}
            transactions = [
                t for t in all_dummy_transactions if hasattr(t, 'compte') and hasattr(t.compte, 'client') and t.compte.client.id in visible_client_ids
            ]
            if transactions:
                title_text = "<b>RAPPORT GLOBAL DES TRANSACTIONS (Données factices)</b>"
            else:
                title_text = "<b>RAPPORT GLOBAL DES TRANSACTIONS (Aucune donnée factice trouvée pour votre rôle)</b>"
        
        # Sortir les transactions factices par date (même si elles sont déjà dans l'ordre initialement)
        transactions.sort(key=lambda x: x.date, reverse=True)


    story.append(Paragraph(title_text, styles['ReportTitle']))
    story.append(Spacer(1, 0.4 * inch))

    if not transactions:
        story.append(Paragraph("Aucune transaction trouvée pour cette sélection.", style_normal))
    else:
        data = [
            [
                Paragraph("<b>Date</b>", style_center),
                Paragraph("<b>Type</b>", style_center),
                Paragraph("<b>Montant (XOF)</b>", style_center),
                Paragraph("<b>Compte</b>", style_center),
                Paragraph("<b>Description</b>", style_center)
            ]
        ]
        for t in transactions:
            data.append([
                Paragraph(t.date.strftime("%Y-%m-%d %H:%M"), styles['TableCellText']),
                Paragraph(t.get_type_operation_display(), styles['TableCellText']),
                Paragraph(f"{t.montant:,.2f}".replace(',', ' ').replace('.', ','), styles['TableCellRight']),
                Paragraph(getattr(t.compte, 'numero_compte', 'N/A'), styles['TableCellText']), # Assurez-vous que t.compte existe et a numero_compte
                Paragraph(t.description or "N/A", styles['TableCellText'])
            ])
        
        table = Table(data, colWidths=[1.6*inch, 1.2*inch, 1.4*inch, 1.6*inch, 3.89*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0ea5e9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#e0f2fe')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#7dd3fc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284c7')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(table)
    
    doc.build(story)
    filename = f"Rapport_Transactions_{client_id}" if client_id else "Rapport_Global_Transactions"
    return generate_pdf_response(buffer, filename)



def rapport_credits_pdf(request, client_id=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []

    title_text = "<b>RAPPORT GLOBAL DES CRÉDITS</b>"
    credits = []

    try:
        if client_id:
            if Client.objects:
                try:
                    client = Client.objects.get(pk=client_id)
                    if Credit.objects:
                        credits = Credit.objects.filter(compte__client=client).order_by('-date_octroi')
                    title_text = f"<b>RAPPORT DES CRÉDITS POUR {client.nom.upper()} {client.prenom.upper()}</b>"
                except Client.DoesNotExist:
                    credits = []
                    title_text = "<b>RAPPORT DES CRÉDITS (CLIENT INTROUVABLE)</b>"
                    print(f"INFO : Client avec ID {client_id} non trouvé.")
            else:
                print(f"INFO : Modèle Client non accessible pour filtrer les crédits pour ID {client_id}.")
                credits = []
        else:
            if Credit.objects:
                credits = Credit.objects.all().order_by('-date_octroi')
    except AttributeError:
        credits = []
        print("INFO : Modèle Credit non accessible. Pas de crédits réels.")

    if not credits and not (client_id and "INTROUVABLE" in title_text):
        class DummyCredit:
            def __init__(self, num, montant, taux, duree, date_octroi, statut, montant_remb):
                self.numero_credit = num
                self.montant = Decimal(montant)
                self.taux_interet = Decimal(taux)
                self.duree_mois = duree
                self.date_octroi = date_octroi
                self.statut = statut
                self.montant_rembourse = Decimal(montant_remb)

        credits = [
            DummyCredit('CRD-001', '100000.00', '5.0', 12, timezone.now() - datetime.timedelta(days=60), 'En Cours', '20000.00'),
            DummyCredit('CRD-002', '250000.00', '7.5', 24, timezone.now() - datetime.timedelta(days=300), 'Remboursé', '250000.00'),
            DummyCredit('CRD-003', '50000.00', '6.0', 6, timezone.now() - datetime.timedelta(days=10), 'En Cours', '0.00'),
        ]
        if client_id:
            # Note: Cette logique de filtrage des crédits factices est simpliste.
            # Elle ne fonctionnera que si le client_id correspond exactement à la fin du numéro de crédit factice.
            credits = [c for c in credits if c.numero_credit.endswith(str(client_id))]
            if not credits:
                title_text = f"<b>RAPPORT DES CRÉDITS POUR CLIENT ID {client_id} (Aucun crédit factice trouvé)</b>"
            else:
                title_text = f"<b>RAPPORT DES CRÉDITS POUR CLIENT ID {client_id} (Données factices)</b>"
        else:
            title_text = "<b>RAPPORT GLOBAL DES CRÉDITS (Données factices)</b>"


    story.append(Paragraph(title_text, styles['ReportTitle']))
    story.append(Spacer(1, 0.4 * inch))

    if not credits:
        story.append(Paragraph("Aucun crédit trouvé pour cette sélection.", style_normal))
    else:
        data_credits = [
            [
                Paragraph("<b>Numéro Crédit</b>", style_center),
                Paragraph("<b>Montant Octroyé (XOF)</b>", style_center),
                Paragraph("<b>Taux (%)</b>", style_center),
                Paragraph("<b>Durée (mois)</b>", style_center),
                Paragraph("<b>Date Octroi</b>", style_center),
                Paragraph("<b>Statut</b>", style_center),
                Paragraph("<b>Montant Remboursé (XOF)</b>", style_center)
            ]
        ]
        for credit in credits:
            montant_remb = getattr(credit, 'montant_rembourse', Decimal('0.00')) 
            data_credits.append([
                Paragraph(credit.numero_credit, styles['TableCellText']),
                Paragraph(f"{credit.montant:,.2f}".replace(',', ' ').replace('.', ','), styles['TableCellRight']),
                Paragraph(f"{credit.taux_interet:.2f}", styles['TableCellRight']),
                Paragraph(str(credit.duree_mois), styles['TableCellText']),
                Paragraph(credit.date_octroi.strftime("%Y-%m-%d"), styles['TableCellText']),
                Paragraph(credit.statut, styles['TableCellText']),
                Paragraph(f"{montant_remb:,.2f}".replace(',', ' ').replace('.', ','), styles['TableCellRight'])
            ])
        
        table_credits = Table(data_credits, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1*inch, 1.8*inch])
        table_credits.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),
            ('ALIGN', (3,1), (3,-1), 'CENTER'),
            ('ALIGN', (6,1), (6,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fee2e2')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ef4444')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(table_credits)
        story.append(Spacer(1, 0.4 * inch))

        story.append(Paragraph("<b>Statut des Crédits</b>", styles['SectionTitle']))
        labels_statut = []
        data_statut = []
        try:
            if Credit.objects:
                statut_counts = Credit.objects.values('statut').annotate(count=Count('statut')).order_by('statut')
                labels_statut = [item['statut'] for item in statut_counts]
                data_statut = [item['count'] for item in statut_counts]
        except AttributeError:
            labels_statut = ['En Cours', 'Remboursé', 'En Retard']
            data_statut = [15, 8, 2]
            print("INFO : Utilisation de données factices pour le statut des crédits car le modèle n'est pas accessible.")

        if data_statut:
            chart_statut_buffer = create_chart_image(data_statut, labels_statut, "Statut des Crédits", 'bar', colors=['#f59e0b', '#10b981', '#ef4444'])
            img_statut = Image((chart_statut_buffer))
            img_statut.width = 3.5 * inch
            img_statut.height = 2.5 * inch
            story.append(img_statut)
        else:
            story.append(Paragraph("Pas de données de statut de crédit pour le graphique.", style_normal))
        story.append(Spacer(1, 0.4 * inch))

        story.append(Paragraph("<b>Montant des Crédits Octroyés par Mois (sur les 12 derniers mois)</b>", styles['SectionTitle']))
        
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=365)

            credits_monthly = Credit.objects.filter(
                date_octroi__range=(start_date, end_date)
            ).annotate(
                month=TruncMonth('date_octroi')
            ).values('month').annotate(
                total_amount=Sum('montant')
            ).order_by('month')

            if credits_monthly:
                months = [item['month'].strftime('%Y-%m') for item in credits_monthly]
                amounts = [float(item['total_amount']) for item in credits_monthly]

                plt.figure(figsize=(8, 4))
                plt.plot(months, amounts, marker='o', linestyle='-', color='#8b5cf6')
                plt.xlabel('Mois')
                plt.ylabel('Montant Total des Crédits (XOF)')
                plt.title('Tendances des Crédits Octroyés')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True)
                plt.tight_layout()
                
                chart_tendances_buffer = io.BytesIO()
                plt.savefig(chart_tendances_buffer, format='png')
                plt.close()
                chart_tendances_buffer.seek(0)

                img_tendances = Image((chart_tendances_buffer))
                img_tendances.width = 5.5 * inch
                img_tendances.height = 3.5 * inch
                story.append(img_tendances)
            else:
                story.append(Paragraph("Pas de données de crédit suffisantes sur les 12 derniers mois pour le graphique de tendance.", style_normal))
        except Exception as e:
            story.append(Paragraph("Impossible de générer le graphique de tendance des crédits.", style_normal))
            print("ERREUR Graphique de tendance :", str(e))


    doc.build(story)
    filename = f"Rapport_Credits_{client_id}" if client_id else "Rapport_Global_Credits"
    return generate_pdf_response(buffer, filename)

