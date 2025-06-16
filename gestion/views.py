# gestion/views.py

# --- Imports Django standards ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q # <-- Assurez-vous que Sum est bien importé ici
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

from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date
from .models import Agent, Client, Compte, Mouvement, Credit, Remboursement, HistoriqueTransaction
from django.db import transaction

# --- Imports Django REST Framework (AJOUTÉS / VÉRIFIÉS) ---
from rest_framework.decorators import api_view, permission_classes # Importez ceci
from rest_framework.response import Response # Importez ceci
from rest_framework import status # Importez ceci
# from rest_framework.permissions import IsAuthenticated # Décommentez si vous utilisez l'authentification DRF


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

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        clients = Client.objects.all()
        comptes = Compte.objects.all()
        mouvements = Mouvement.objects.all()
        credits = Credit.objects.all()
        remboursements = Remboursement.objects.all()
    else:
        clients = Client.objects.filter(agent=user)
        comptes = Compte.objects.filter(client__in=clients)
        mouvements = Mouvement.objects.filter(agent=user)
        credits = Credit.objects.filter(agent=user)
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

#zone des clients
@login_required
def liste_clients(request):
    user = request.user
    if user.role == 'admin':
        clients = Client.objects.all().prefetch_related('comptes')
    else:
        clients = Client.objects.filter(agent=user).prefetch_related('comptes')
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
        'clients': clients
    })

@require_http_methods(["DELETE"])
@csrf_exempt
def supprimer_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        client.delete()
        return JsonResponse({'success': True})
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Client non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["PUT"])
@csrf_exempt
def modifier_client(request, client_id):
    try:
        data = json.loads(request.body)
        client = Client.objects.get(id=client_id)
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

@csrf_exempt
def ajouter_compte(request, client_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_compte = data.get("typeCompte")
            solde_initial = data.get("soldeInitial")
            client = Client.objects.get(id=client_id)
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
        form.instance.agent = self.request.user
        return super().form_valid(form)

class ListeComptesView(ListView):
    model = Compte
    template_name = 'dashboard/section/liste_compte.html'
    context_object_name = 'comptes'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset().select_related('client')
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
        context['solde_total'] = Compte.objects.aggregate(
            total=Sum('solde')
        )['total'] or 0
        context['search_query'] = self.request.GET.get('q', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['statut_filter'] = self.request.GET.get('statut', '')
        return context

@login_required
def effectuer_transaction(request):
    comptes = Compte.objects.select_related('client').all()
    return render(request, 'dashboard/section/transaction.html', {
        'comptes': comptes,
    })

@require_http_methods(["POST"])
@login_required
def effectuer_mouvement(request, compte_id):
    try:
        compte = get_object_or_404(Compte, id=compte_id)
        agent = request.user
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
                agent=agent,
                type_mouvement=type_mouvement,
                montant=montant,
            )
            HistoriqueTransaction.objects.create(
                compte=compte,
                type_operation=type_mouvement,
                montant=montant,
                description=f"{type_mouvement} effectué par {agent.get_full_name()}"
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
def transactions_data(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    type_filter = request.GET.get('type')
    client_filter = request.GET.get('client', '').strip().lower()
    min_amount = request.GET.get('minAmount')
    max_amount = request.GET.get('maxAmount')
    transactions = HistoriqueTransaction.objects.select_related('compte__client')
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
            "balanceAfter": float(t.compte.solde)
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
    return render(request, "dashboard/section/historique.html")

def credit(request):
    return render(request, "dashboard/section/nouveau_credit.html")

def ajouter_credit(request):
    comptes = Compte.objects.all()
    context = {
        'comptes': comptes,
    }
    return render(request, 'dashboard/section/nouveau_credit.html', context)

@require_POST
def create_credit_api(request):
    try:
        data = json.loads(request.body)
        compte_id = data.get('compte')
        raw_montant = data.get('montant')
        raw_taux_interet = data.get('taux_interet')
        duree_mois = data.get('duree_mois')
        if not all([compte_id, raw_montant, raw_taux_interet, duree_mois]):
            return JsonResponse({'error': 'Tous les champs obligatoires doivent être remplis.'}, status=400)
        try:
            montant = Decimal(str(raw_montant))
            taux_interet = Decimal(str(raw_taux_interet))
        except InvalidOperation:
            return JsonResponse({'error': 'Le montant ou le taux d\'intérêt n\'est pas un nombre valide.'}, status=400)
        try:
            compte = Compte.objects.get(id=compte_id)
        except Compte.DoesNotExist:
            return JsonResponse({'error': 'Compte introuvable.'}, status=404)
        agent = Agent.objects.first()
        with transaction.atomic():
            credit = Credit.objects.create(
                compte=compte,
                agent=agent,
                montant=montant,
                taux_interet=taux_interet,
                duree_mois=duree_mois,
            )
        return JsonResponse({'message': 'Crédit créé avec succès !', 'numero_credit': credit.numero_credit}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def liste_credits(request):
    return render(request, 'dashboard/section/liste_credit.html')

@require_GET
def api_list_comptes(request):
    comptes_data = []
    comptes = Compte.objects.select_related('client').all()
    for compte in comptes:
        comptes_data.append({
            'id': compte.id,
            'numero_compte': compte.numero_compte,
            'client_nom_complet': f"{compte.client.nom} {compte.client.prenom}" if hasattr(compte, 'client') and compte.client else "Client Inconnu",
            'solde': str(compte.solde),
        })
    return JsonResponse(comptes_data, safe=False)

@require_GET
def api_list_credits(request):
    credits_data = []
    credits = Credit.objects.select_related('compte__client').filter(
        statut__in=['EN_COURS', 'EN_RETARD']
    ).annotate(
        total_rembourse_calcule = Sum('remboursements__montant')
    ).order_by('-date_octroi')
    for credit in credits:
        client_full_name = "Client Inconnu"
        account_number = "N/A"
        if hasattr(credit, 'compte') and credit.compte:
            account_number = credit.compte.numero_compte
            if hasattr(credit.compte, 'client') and credit.compte.client:
                client_full_name = f"{credit.compte.client.nom} {credit.compte.client.prenom}"
        paid_amount = credit.total_rembourse_calcule if credit.total_rembourse_calcule is not None else Decimal('0.00')
        remaining_amount = credit.montant - paid_amount
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
            'montant_restant_du': str(remaining_amount),
            'type_credit': getattr(credit, 'type_credit', None),
            'objet_credit': getattr(credit, 'objet_credit', None),
            'montant_rembourse': str(paid_amount),
            'montant_restant_du': str(remaining_amount),
        })
    return JsonResponse(credits_data, safe=False)

def remboursement(request):
    """
    Rend la page HTML principale pour l'interface de remboursement de crédit.
    """
    return render(request, 'dashboard/section/remboursement.html')

@require_GET
def get_credit_payments(request, credit_id):
    """
    Retourne l'historique des remboursements pour un crédit donné.
    """
    credit = get_object_or_404(Credit, id=credit_id)
    payments = credit.remboursements.all().order_by('-date')
    data = []
    for payment in payments:
        data.append({
            'id': str(payment.id),
            'montant': str(payment.montant),
            'date_paiement': payment.date.isoformat(),
            'methode_paiement': 'ESPECES', # Vérifiez si votre modèle a ce champ
            'reference': payment.numero_remboursement,
            'notes': '', # Vérifiez si votre modèle a ce champ
        })
    return JsonResponse(data, safe=False)

# --- Fonction record_repayment (MODIFIÉE) ---
@api_view(['POST']) # <-- **TRÈS IMPORTANT : Ajoute les fonctionnalités DRF**
# @permission_classes([IsAuthenticated]) # <-- DÉCOMMENTEZ ET IMPORTEZ si l'utilisateur doit être authentifié via DRF
@csrf_exempt # Continuez de l'utiliser si pas de jeton CSRF, mais à revoir pour la production !
# @require_POST # Ce décorateur est redondant avec @api_view(['POST']) et peut être retiré.
def record_repayment(request):
    print("--- DEBUG: Entrée dans record_repayment ---") # Premier print

    # Utilisez request.data directement si @api_view est présent.
    # Cela gère automatiquement le parsing JSON pour les requêtes POST.
    data = request.data
    print(f"DEBUG: Données reçues via request.data: {data}")

    try:
        credit_id = data.get('credit_id')
        montant_str = data.get('montant') # Récupérez le montant comme string initialement
        date_paiement_str = data.get('date_paiement') # Format YYYY-MM-DD
        methode_paiement = data.get('methode_paiement', 'INCONNU') # Assurez-vous que ce champ existe dans Remboursement
        reference = data.get('reference', '') # Assurez-vous que ce champ existe dans Remboursement
        notes = data.get('notes', '') # Assurez-vous que ce champ existe dans Remboursement

        print(f"DEBUG: credit_id={credit_id}, montant_str='{montant_str}', date_paiement_str='{date_paiement_str}'")

        if not all([credit_id, montant_str, date_paiement_str]):
            print("DEBUG: Champs obligatoires manquants.")
            return Response(
                {"error": "Les champs 'credit_id', 'montant' et 'date_paiement' sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            montant = Decimal(str(montant_str)) # Convertir en Decimal
            if montant <= 0:
                print("DEBUG: Montant de remboursement <= 0.")
                return Response({"error": "Le montant du remboursement doit être positif."}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidOperation:
            print(f"DEBUG: Erreur de conversion du montant: '{montant_str}'")
            return Response({"error": "Montant invalide ou non numérique."}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError: # Au cas où montant_str serait None
            print("DEBUG: Montant est None.")
            return Response({"error": "Le montant est requis et doit être numérique."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convertir la date du formulaire en objet date
            date_paiement = datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
            # Combinez avec une heure (min.time()) et rendez-la consciente du fuseau horaire
            date_paiement_dt = timezone.make_aware(datetime.combine(date_paiement, datetime.min.time()))
            print(f"DEBUG: Date de paiement convertie: {date_paiement_dt}")
        except ValueError:
            print(f"DEBUG: Format de date invalide: '{date_paiement_str}'")
            return Response({"error": "Format de date invalide. Utilisez YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        credit = get_object_or_404(Credit, id=credit_id)
        print(f"DEBUG: Crédit trouvé: ID={credit.id}, Numéro={credit.numero_credit}")

        # Calcul de la part principal/intérêt (Simplification ici)
        montant_principal_remb = montant
        montant_interet_remb = Decimal('0.00')

        with transaction.atomic():
            print("DEBUG: Début de la transaction atomique pour le remboursement.")
            remboursement = Remboursement.objects.create(
                credit=credit,
                # agent=request.user, # Décommentez si vous gérez l'agent connecté
                montant=montant,
                montant_principal=montant_principal_remb,
                montant_interet=montant_interet_remb,
                date=date_paiement_dt,
                # methode_paiement=methode_paiement, # <-- DÉCOMMENTEZ ET VÉRIFIEZ LE MODÈLE
                # reference=reference,               # <-- DÉCOMMENTEZ ET VÉRIFIEZ LE MODÈLE
                # notes=notes,                       # <-- DÉCOMMENTEZ ET VÉRIFIEZ LE MODÈLE
            )
            print(f"DEBUG: Remboursement créé : ID={remboursement.id}, Montant={remboursement.montant}")

            # Mettre à jour le montant_rembourse sur le modèle Credit
            # Assurez-vous que votre modèle Credit a un champ `montant_rembourse` de type DecimalField
            # et qu'il est initialisé à 0.00 lors de la création d'un crédit.
            credit.montant_rembourse = (credit.montant_rembourse or Decimal('0.00')) + montant
            print(f"DEBUG: Nouveau montant remboursé pour le crédit {credit.id}: {credit.montant_rembourse}")

            # Mettre à jour le statut du crédit si entièrement remboursé
            # Vous devrez probablement définir un "montant total dû" incluant les intérêts pour une logique exacte.
            montant_total_du = credit.montant # Ajustez ceci si vous avez un calcul d'intérêt plus complexe
            if credit.montant_rembourse >= montant_total_du:
                credit.statut = 'REMBOURSE'
                print(f"DEBUG: Statut du crédit {credit.id} mis à 'REMBOURSE'.")
            else:
                # S'assurer qu'il est "EN_COURS" ou "EN_RETARD" si ce n'est pas déjà le cas
                if credit.statut not in ['EN_COURS', 'EN_RETARD']:
                    credit.statut = 'EN_COURS'
                print(f"DEBUG: Statut du crédit {credit.id} reste: {credit.statut}.")

            credit.save() # Sauvegardez les changements sur le crédit

            print("DEBUG: Transaction atomique terminée avec succès.")

        return Response(
            {"message": "Remboursement enregistré avec succès", "id": str(remboursement.id)},
            status=status.HTTP_201_CREATED
        )

    except Credit.DoesNotExist:
        print(f"--- ERREUR: Crédit introuvable pour ID: {credit_id} ---")
        return Response({"error": "Crédit introuvable."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        print(f"--- ERREUR DE DONNÉES ou DE CONVERSION: {e} ---")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        print(f"--- ERREUR INATTENDUE DANS LE BLOC TRY/EXCEPT PRINCIPAL: {e} ---")
        traceback.print_exc() # Cela imprimera le traceback complet dans la console
        return Response({"error": f"Une erreur interne est survenue sur le serveur: {e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)