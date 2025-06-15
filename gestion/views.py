from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic import ListView


from decimal import Decimal
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

import json
import random

from .models import Agent, Client, Compte, Mouvement, Credit, Remboursement, HistoriqueTransaction
from django.db import transaction


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

    # Si l'utilisateur est admin, il voit tout
    if user.role == 'admin':
        clients = Client.objects.all()
        comptes = Compte.objects.all()
        mouvements = Mouvement.objects.all()
        credits = Credit.objects.all()
        remboursements = Remboursement.objects.all()
    else:
        # Sinon, il ne voit que ses propres données
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

    # Préparer les données pour le template
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
        'clients': clients  # Pour une utilisation future si nécessaire
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

        # Conversion de la date
        date_inscription = data.get('date_inscription')
        if date_inscription:
            try:
                data['date_inscription'] = datetime.strptime(date_inscription, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)

        # Liste des champs modifiables (exclut numero_identifiant)
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
                'numero_identifiant': client.identifiant,  # Renvoi à des fins d'affichage seulement
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
    template_name = 'dashboard/section/ajouter_client.html'  # Chemin vers votre template
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
        
        # Filtrage par recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(numero_compte__icontains=search_query) |
                Q(client__nom__icontains=search_query) |
                Q(client__prenom__icontains=search_query) |
                Q(client__identifiant__icontains=search_query)
            )
        
        # Filtrage par type de compte
        type_compte = self.request.GET.get('type')
        if type_compte in ['epargne', 'courant']:
            queryset = queryset.filter(type_compte=type_compte)
        
        # Filtrage par statut de solde
        statut = self.request.GET.get('statut')
        if statut == 'positive':
            queryset = queryset.filter(solde__gte=0)
        elif statut == 'negative':
            queryset = queryset.filter(solde__lt=0)
        
        # Annoter avec les totaux de dépôts et retraits en utilisant le modèle Mouvement
        queryset = queryset.annotate(
            total_depots=Sum('mouvements__montant', filter=Q(mouvements__type_mouvement='DEPOT')),
            total_retraits=Sum('mouvements__montant', filter=Q(mouvements__type_mouvement='RETRAIT'))
        )
        
        return queryset.order_by('-date_creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcul du solde total
        context['solde_total'] = Compte.objects.aggregate(
            total=Sum('solde')
        )['total'] or 0
        
        # Transmission des paramètres de filtrage pour le template
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

            # Historique
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
@require_http_methods(["POST"])
def octroyer_credit(request, compte_id):
    try:
        data = json.loads(request.body)
        montant = Decimal(data.get("montant"))
        taux_interet = Decimal(data.get("taux_interet"))
        duree_mois = int(data.get("duree_mois"))
        agent_id = data.get("agent_id")

        compte = get_object_or_404(Compte, id=compte_id)
        agent = get_object_or_404(Agent, id=agent_id)

        credit = Credit.objects.create(
            compte=compte,
            agent=agent,
            montant=montant,
            taux_interet=taux_interet,
            duree_mois=duree_mois
        )

        return JsonResponse({"success": True, "message": "Crédit octroyé."})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def rembourser_credit(request, credit_id):
    try:
        data = json.loads(request.body)
        montant = Decimal(data.get("montant"))

        credit = get_object_or_404(Credit, id=credit_id)

        remboursement = Remboursement.objects.create(
            credit=credit,
            montant=montant
        )

        return JsonResponse({"success": True, "message": "Remboursement effectué."})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@require_http_methods(["GET"])
def historique_transactions(request, compte_id):
    compte = get_object_or_404(Compte, id=compte_id)
    historiques = HistoriqueTransaction.objects.filter(compte=compte).order_by('-date')

    data = [
        {
            "type_operation": h.type_operation,
            "montant": str(h.montant),
            "date": h.date.strftime("%Y-%m-%d %H:%M"),
            "description": h.description
        }
        for h in historiques
    ]
    return JsonResponse({"historique": data})
