from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.db import transaction
from decimal import Decimal
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

import json
import random

from .models import Agent, Client, Compte, Mouvement, Credit, Remboursement


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
    
def liste_compte(request):
    return render(request, "dashboard/section/liste_compte.html")