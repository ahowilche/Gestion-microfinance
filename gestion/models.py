from django.db import models
from django.utils import timezone
import random
from django.contrib.auth.models import AbstractUser

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

    compte = models.ForeignKey("Compte", on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent", on_delete=models.SET_NULL, null=True)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

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

    def __str__(self):
        return f"Crédit {self.montant} sur {self.compte}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            HistoriqueTransaction.objects.create(
                compte=self.compte,
                type_operation="CREDIT",
                montant=self.montant,
                description="Crédit octroyé"
            )


# =========================
# REMBOURSEMENT DE CRÉDIT
# =========================
class Remboursement(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Remboursement de {self.montant} le {self.date}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            compte = self.credit.compte
            compte.solde -= self.montant
            compte.save()
            HistoriqueTransaction.objects.create(
                compte=compte,
                type_operation="REMBOURSEMENT",
                montant=self.montant,
                description="Remboursement crédit"
            )


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
