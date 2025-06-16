from django.db import models, transaction
from django.utils import timezone 
import random
import datetime
from django.contrib.auth.models import AbstractUser
from decimal import Decimal, InvalidOperation

# =========================
# AGENT UTILISATEUR
# =========================
class Agent(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent')

    def __str__(self):
        return self.get_full_name() or self.username


# =========================
# CLIENT
# =========================
class Client(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="clients")
    identifiant = models.CharField(max_length=10, unique=True, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=150)
    date_inscription = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.identifiant})"

    def save(self, *args, **kwargs):
        if not self.identifiant:
            self.identifiant = self.generer_identifiant()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Création automatique du premier compte à l'inscription
            Compte.objects.create(client=self)

    def generer_identifiant(self):
        prefix = "ID"
        while True:
            suffix = ''.join(str(random.randint(0, 9)) for _ in range(7))
            identifiant = f"{prefix}{suffix}"
            if not Client.objects.filter(identifiant=identifiant).exists():
                return identifiant


# =========================
# COMPTE
# =========================
class Compte(models.Model):
    
    TYPE_CHOICES = [
        ('epargne', 'Épargne'),
        ('courant', 'Courant'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="comptes")
    type_compte = models.CharField(max_length=20, choices=TYPE_CHOICES, default='epargne')
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_creation = models.DateField(auto_now_add=True)
    numero_compte = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.numero_compte:
            self.numero_compte = self.generer_numero_compte()

        # Limite à 2 comptes par client
        if not self.pk and self.client.comptes.count() >= 2:
            raise ValueError("Un client ne peut pas avoir plus de 2 comptes.")

        super().save(*args, **kwargs)

    def generer_numero_compte(self):
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = str(random.randint(1000, 9999))
        return f"C-{date_part}{random_part}"

    def __str__(self):
        return f"{self.numero_compte} ({self.client})"


# (Les autres classes restent inchangées)
# =========================
# MOUVEMENTS : DÉPÔT / RETRAIT
# =========================


class Mouvement(models.Model):
    TYPE_CHOICES = (
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
    )

    compte = models.ForeignKey("Compte", on_delete=models.CASCADE, related_name="mouvements")
    agent = models.ForeignKey("Agent", on_delete=models.SET_NULL, null=True)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Sécurité : garantir que le montant est bien un Decimal
        if not isinstance(self.montant, Decimal):
            try:
                self.montant = Decimal(str(self.montant))
            except InvalidOperation:
                raise ValueError("Montant invalide")

        if self.montant <= 0:
            raise ValueError("Le montant doit être positif")

        with transaction.atomic():
            if is_new:
                if self.type_mouvement == 'RETRAIT' and self.montant > self.compte.solde:
                    raise ValueError("Solde insuffisant pour effectuer ce retrait.")
            super().save(*args, **kwargs)

            if is_new:
                if self.type_mouvement == 'DEPOT':
                    self.compte.solde += self.montant
                elif self.type_mouvement == 'RETRAIT':
                    self.compte.solde -= self.montant
                self.compte.save()

    def __str__(self):
        return f"{self.type_mouvement} de {self.montant} sur {self.compte.numero_compte}"

# =========================
# HISTORIQUE DES TRANSACTIONS
# =========================
class HistoriqueTransaction(models.Model):
    TYPE_CHOICES = (
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
        ('CREDIT', 'Crédit'),
        ('REMBOURSEMENT', 'Remboursement'),
    )
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    type_operation = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.type_operation} de {self.montant} sur {self.compte.numero_compte}"


# =========================
# CRÉDIT
# =========================
class Credit(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2)
    duree_mois = models.PositiveIntegerField()
    date_octroi = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=20, default='EN_COURS')
    montant_rembourse = models.DecimalField(
        max_digits=12, # Ajustez la taille maximale si vos montants peuvent être très grands
        decimal_places=2,
        default=Decimal('0.00'), # Très important pour les calculs et éviter les valeurs None
        help_text="Montant total déjà remboursé pour ce crédit."
    )
    # New field for credit number
    numero_credit = models.CharField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return f"Crédit {self.numero_credit} - {self.montant} sur {self.compte}"

    def save(self, *args, **kwargs):
        if not self.numero_credit:
            # Generate a credit number based on timestamp (e.g., CR-YYYYMMDDHHMMSS-milliseconds)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            self.numero_credit = f"CR-{timestamp}"
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            HistoriqueTransaction.objects.create(
                compte=self.compte,
                type_operation="CREDIT",
                montant=self.montant,
                description=f"Crédit octroyé (Numéro: {self.numero_credit})"
            )
            # 2. Mise à jour du solde du compte   # Assurez-vous que votre modèle Compte a un champ 'solde'
            self.compte.solde += self.montant
            self.compte.save()

# =========================
# REMBOURSEMENT DE CRÉDIT
# =========================

class Remboursement(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="remboursements")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True) # Agent qui a enregistré
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    montant_principal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00')) # Part du capital
    montant_interet = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00')) # Part des intérêts
    date = models.DateTimeField(default=timezone.now) # Changement de DateField à DateTimeField
    numero_remboursement = models.CharField(max_length=50, unique=True, editable=False) # Référence unique
    methode_paiement = models.CharField(max_length=50, default="INCONNU") # Ajoutez ceci
    reference = models.CharField(max_length=100, blank=True, null=True) # Ajoutez ceci si ce n'est pas numero_remboursement
    notes = models.TextField(blank=True, null=True) # Ajoutez ceci


    def __str__(self):
        return f"Remboursement {self.numero_remboursement} de {self.montant} sur {self.credit} le {self.date.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.numero_remboursement:
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
            self.numero_remboursement = f"REM-{timestamp}"

        if is_new:
            if self.montant_principal in [None, '']:
                self.montant_principal = Decimal('0.00')
            if self.montant_interet in [None, '']:
                self.montant_interet = Decimal('0.00')
            if self.montant_principal == Decimal('0.00') and self.montant_interet == Decimal('0.00'):
                self.montant_principal = self.montant

        if Decimal(self.montant_principal) + Decimal(self.montant_interet) != self.montant:
            raise ValueError("La somme du principal et des intérêts ne correspond pas au montant total du remboursement.")

        if self.montant <= 0:
            raise ValueError("Le montant du remboursement doit être positif.")

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_new:
                compte = self.credit.compte
                from django.db.models import F
                compte.solde = F('solde') - self.montant
                compte.save(update_fields=['solde'])

                HistoriqueTransaction.objects.create(
                    compte=compte,
                    type_operation="REMBOURSEMENT",
                    montant=self.montant,
                    description=f"Remboursement crédit ({self.numero_remboursement}) - Principal: {self.montant_principal}, Intérêts: {self.montant_interet}"
                )
        remboursements_total = self.credit.remboursements.aggregate(
            total=models.Sum('montant'))['total'] or Decimal('0.00')

        if remboursements_total >= self.credit.montant:
            self.credit.statut = 'REMBOURSE'
            self.credit.save(update_fields=['statut'])
