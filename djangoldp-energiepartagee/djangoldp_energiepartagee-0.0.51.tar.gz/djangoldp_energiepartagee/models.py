import uuid
from datetime import date, timedelta
from django.conf import settings
from django.db import models
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.utils.decorators import classonlymethod
from djangoldp.models import Model
from django.dispatch import receiver
from django.db.models import Max
from django.db.models.signals import pre_save, post_save, m2m_changed
from datetime import datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from djangoldp.permissions import LDPPermissions
from djangoldp.utils import is_anonymous_user
from djangoldp_energiepartagee.permissions import *
from djangoldp_energiepartagee.filters import *
from djangoldp.views import LDPViewSet


class RelatedactorViewSet(LDPViewSet):
    def is_safe_create(self, user, validated_data, *args, **kwargs):
        # '''
        # A function which is checked before the create operation to confirm the validated data is safe to add
        # returns True by default
        # :return: True if the actor being posted is one which I am a member of
        # '''
        # if user.is_superuser:
        #     return True
        # 
        # actor_arg = validated_data.get('actor')
        # 
        # try:
        #     from djangoldp_energiepartagee.models import Relatedactor, Actor
        # 
        #     actor = Actor.objects.get(urlid=actor_arg['urlid'])
        # 
        #     if Relatedactor.objects.filter(user=user, actor=actor, role='admin').exists():
        #         return True
        # 
        # except (get_user_model().DoesNotExist, KeyError):
        #     pass

        # '''
        # A function which is checked before the create operation to confirm the validated data is safe to add
        # returns True by default
        # returns False if an unknown (that is a user without any relatedactor) user tries to add a relatedactor with a defined role
        # '''
        # 
        # from djangoldp_energiepartagee.models import Relatedactor
        # print(Relatedactor.objects.filter(user=user))
        # print(validated_data.get('role'))
        # if not Relatedactor.objects.filter(user=user).exists() and validated_data.get('role') != None:
        #     return False
        # 
        # return True


        '''
        A function which is checked before the create operation to confirm the validated data is safe to add
        returns False by default
        returns True if the user:
            - is superuser
            - is admin or member on any actor
            - is unknown (that is a user without any relatedactor) user and tries to add a relatedactor with an empty role
        '''

        # is superuser
        if user.is_superuser:
            return True
        
        try:
            # from djangoldp_energiepartagee.models import Relatedactor
            # is admin or member on any actor        
            if Relatedactor.objects.filter(user=user, role__in=['admin', 'member']).exists():
                return True

            # is unknown user and tries to add a relatedactor with an empty role
            if not Relatedactor.objects.filter(user=user).exists() and validated_data.get('role') == None:
                return True
        
        except (get_user_model().DoesNotExist, KeyError):
            pass       

        return False

class Region(Model) :
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name="Région")
    isocode = models.CharField(max_length=6, blank=True, null=True, verbose_name="code ISO")

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:region'
        
    def __str__(self):
        return self.name

class College(Model) :
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="collège")

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:college'

    def __str__(self):
         return self.name

class Regionalnetwork(Model) :
    name = models.CharField(max_length=250, blank=True, null=True, verbose_name="Réseau régional")
    address = models.CharField(max_length=250, blank=True, null=True, verbose_name="Adresse")
    postcode = models.CharField(max_length=5, blank=True, null=True, verbose_name="Code Postal")
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name="Ville")
    colleges = models.ManyToManyField(College, blank=True, max_length=50, verbose_name="Collège")
    code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Code du réseau")
    logo = models.ImageField(blank=True, null=True, verbose_name="Logo")
    siren = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIRET")
    usercontact = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, verbose_name="contact")
    bank = models.CharField(max_length=250, blank=True, null=True, verbose_name="Banque")
    iban = models.CharField(max_length=35, blank=True, null=True, verbose_name="IBAN")
    bic = models.CharField(max_length=15, blank=True, null=True, verbose_name="BIC")
    orderpayment = models.CharField(max_length=250, blank=True, null=True, verbose_name="Ordre de paiement")
    addresspayment = models.CharField(max_length=250, blank=True, null=True, verbose_name="Adresse de paiement")
    postcodepayment = models.CharField(max_length=5, blank=True, null=True, verbose_name="Code Postal de paiement")
    citypayment = models.CharField(max_length=30, blank=True, null=True, verbose_name="Ville de paiement")
    signature = models.ImageField(blank=True, null=True, verbose_name="Signature")
    mandat = models.CharField(max_length=250, blank=True, null=True, verbose_name="Mandat du responsable légal")
    respname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nom du responsable légal")
    respfirstname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prénom du responsable légal")
    nationale = models.BooleanField(verbose_name="Réseau National", blank=True, null=True,  default=False)


    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:regionalnetwork'

    def __str__(self):
        return self.name

class Interventionzone(Model) :
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Zone d'intervention")

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:interventionzone'

    def __str__(self):
        return self.name

class Legalstructure(Model) :
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Structure Juridique")

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:legalstructure'

    def __str__(self):
        return self.name

class Collegeepa(Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="collège")

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:collegeepa'

    def __str__(self):
         return self.name

class Paymentmethod(Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mode de paiement")

    class Meta(Model.Meta):
        permission_classes = [LDPPermissions]
        anonymous_perms = []
        authenticated_perms = ['view']
        rdf_type = 'energiepartagee:paymentmethod'

    def __str__(self):
        return self.name

class Profile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de téléphone")
    presentation = models.TextField( blank=True, null=True, verbose_name="Présentation de l'utilisateur")
    picture =  models.CharField(blank=True,  null=True, max_length=250, default="/img/default_avatar_user.svg", verbose_name="Photo de l'utilisateur")
    address = models.CharField(max_length=250, blank=True, null=True, verbose_name="Adresse")
    postcode = models.CharField(max_length=5, blank=True, null=True, verbose_name="Code Postal")
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name="Ville")
    
    class Meta(Model.Meta):
        owner_field = 'user'
        authenticated_perms = ['add']
        permission_classes = [ProfilePermissions]
        rdf_type = 'energiepartagee:profile'

    def __str__(self):
        return str(self.user)

class Integrationstep(Model):
    packagestep =  models.BooleanField(blank=True, null=True, verbose_name="Colis accueil à envoyer", default=False)
    adhspacestep = models.BooleanField(blank=True, null=True, verbose_name="Non inscrit sur espace Adh", default=False)
    adhliststep = models.BooleanField(blank=True, null=True, verbose_name="Non inscrit sur liste Adh", default=False)
    regionalliststep = models.BooleanField(blank=True, null=True, verbose_name="Non inscrit sur liste régional", default=False)
    admincomment = models.TextField( blank=True, null=True, verbose_name="Commentaires de l'administrateur")

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        permission_classes = [SuperUserOnlyPermission]
        rdf_type = 'energiepartagee:integrationstep'


    def __str__(self):
        return str(self.id)

ACTORTYPE_CHOICES = [
    ('soc_citoy', 'Sociétés Citoyennes'),
    ('collectivite', 'Collectivités'),
    ('structure', 'Structures d’Accompagnement'),
    ('partenaire', 'Partenaires'),
]

CATEGORY_CHOICES = [
    ('collectivite', 'Collectivités'),
    ('porteur_dev', 'Porteurs de projet en développement'),
    ('porteur_exploit', 'Porteurs de projet en exploitation'),
    ('partenaire', 'Partenaires'),
]

class Actor (Model):
    shortname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nom court de l'acteur")
    longname = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nom long de l'acteur")
    address = models.CharField(max_length=250, blank=True, null=True, verbose_name="Adresse")
    complementaddress = models.CharField(max_length=250, blank=True, null=True, verbose_name="Complément d'adresse")
    postcode = models.CharField(max_length=20, blank=True, null=True, verbose_name="Code Postal")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ville")
    region = models.ForeignKey(Region, max_length=50, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Région", related_name='actors')
    website = models.CharField(max_length=250, blank=True, null=True, verbose_name="Site internet")
    mail = models.CharField(max_length=50, blank=True, null=True, verbose_name="Adresse mail")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de téléphone")
    iban = models.CharField(max_length=35, blank=True, null=True, verbose_name="IBAN")
    lat = models.DecimalField(max_digits=30, decimal_places=25, blank=True, null=True, verbose_name="Lattitude")
    lng = models.DecimalField(max_digits=30, decimal_places=25, blank=True, null=True, verbose_name="Longitude")
    status = models.BooleanField(verbose_name="Adhérent", blank=True, null=True,  default=False)
    regionalnetwork = models.ForeignKey(Regionalnetwork, blank=True, null=True, max_length=250, on_delete=models.CASCADE, verbose_name="Paiement à effectuer à")
    actortype = models.CharField(choices=ACTORTYPE_CHOICES, max_length=50, blank=True, null=True, verbose_name="Type d'acteur")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50, blank=True, null=True, verbose_name="Catégorie de cotisant")
    numberpeople = models.IntegerField(blank=True, null=True, verbose_name="Nombre d'habitants")
    numberemployees = models.IntegerField(blank=True, null=True, verbose_name="Nombre d'employés")
    turnover = models.IntegerField(blank=True, null=True, verbose_name="Chiffre d'affaires")
    presentation = models.TextField(blank=True, null=True, verbose_name="Présentation/objet de la structure")
    interventionzone= models.ManyToManyField(Interventionzone, blank=True, max_length=50, verbose_name="Zone d'intervention",related_name='actors')
    logo =models.CharField(blank=True, max_length=250, null=True, default="https://moncompte.energie-partagee.org/img/default_avatar_actor.svg", verbose_name="Logo")
    legalstructure = models.ForeignKey(Legalstructure, max_length=50, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Structure Juridique", related_name='actors')
    legalrepresentant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_requests_created', blank=True, null=True, verbose_name="Représentant légal")
    managementcontact = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,  on_delete=models.CASCADE, verbose_name="Contact Gestion")
    adhmail = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mail pour compte espace ADH")
    siren = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIREN ou RNA")
    collegeepa = models.ForeignKey(Collegeepa, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Collège EPA", related_name='actors')
    college = models.ForeignKey(College, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Collège", related_name='actors')
    actorcomment = models.TextField( blank=True, null=True, verbose_name="Commentaires de l'acteur")
    signataire = models.BooleanField(blank=True, null=True, verbose_name="Signataire de la charte EP", default=False)
    adhesiondate = models.IntegerField(blank=True, null=True, verbose_name="Adhérent depuis")
    renewed = models.BooleanField(blank=True, null=True, verbose_name="Adhérent sur l'année en cours", default=True)
    integrationstep = models.ForeignKey(Integrationstep, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Espace administrateur", related_name="actors")
    visible = models.BooleanField(blank=True, null=True, verbose_name="Visible sur la carte", default=True)
    createdate = models.DateTimeField(auto_now_add=True, verbose_name="Date de création") 
    updatedate = models.DateTimeField(auto_now=True, verbose_name="Date de dernière mise à jour")

    @property
    def name(self):
         return "%s - %s" % ( self.shortname, self.longname )

    def get_next_contribution_amount(self):
        ''':return: the amount an actor should contribute in their next contribution'''
        amount = 0

        # Collectivity: 2c€ * Habitants - +50€ -1000€
        if self.category == CATEGORY_CHOICES[0][0] and self.numberpeople:
            amount = 0.02 * self.numberpeople
            if amount < 50:
                amount = 50
            elif amount > 1000: 
                amount = 1000
        # Porteur_dev: 50€
        elif self.category == CATEGORY_CHOICES[1][0]:
            amount = 50
        # Porteur_exploit: 0.5% CA +50€ -1000€
        elif self.category == CATEGORY_CHOICES[2][0] and self.turnover:
            amount = 0.005 * self.turnover
            if amount < 100:
                amount = 100
            elif amount > 1000:
                amount = 1000
        # Partenaire: 
        #   - 1 to 4 salariés: 100€
        #   - 5 to 10 salariés: 250€
        #   - > 10 salariés: 400€
        elif self.category == CATEGORY_CHOICES[3][0] and self.numberemployees:
            if self.numberemployees < 5:
                amount = 100
            elif self.numberemployees < 10:
                amount = 250
            elif self.numberemployees > 10:
                amount = 400

        return amount

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['view', 'add']
        permission_classes = [ActorPermissions]
        rdf_type = 'energiepartagee:actor'
        
    def __str__(self):
        return self.name 

CONTRIBUTION_CHOICES = [
    ('appel_a_envoye', 'Appel à envoyer'),
    ('appel_ok', 'Appel envoyé'),
    ('relance', 'Relancé'),
    ('a_ventiler', 'A ventiler'),
    ('valide', 'Validé'),
]

class Contribution(Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Acteur", related_name="contributions")
    year = models.IntegerField(blank=True, null=True, verbose_name="Année de cotisation")    
    numberpeople = models.IntegerField(blank=True, null=True, verbose_name="Nombre d'habitants")
    numberemployees = models.IntegerField(blank=True, null=True, verbose_name="Nombre d'employés")
    turnover = models.IntegerField(blank=True, null=True, verbose_name="Chiffre d'affaires")  
    amount = models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2, verbose_name="Montant à payer")
    contributionnumber = models.IntegerField(unique=True, blank=True, null=True, verbose_name="Numéro de la cotisation")
    paymentto = models.ForeignKey(Regionalnetwork, blank=True, null=True, max_length=250, on_delete=models.CASCADE, verbose_name="Paiement à effectuer à")
    paymentmethod = models.ForeignKey(Paymentmethod, blank=True, null=True, max_length=50, on_delete=models.CASCADE, verbose_name="Moyen de paiement")
    calldate = models.DateField( blank=True, null=True, verbose_name="Date du dernier appel")
    paymentdate = models.DateField(verbose_name="Date de paiement", blank=True, null=True)
    receptdate = models.DateField(verbose_name="Date de l'envoi du reçu", blank=True, null=True)
    receivedby = models.ForeignKey(Regionalnetwork, blank=True, null=True, max_length=250, on_delete=models.CASCADE, related_name='%(class)s_requests_created', verbose_name="Paiement reçu par")
    contributionstatus =  models.CharField(choices=CONTRIBUTION_CHOICES, max_length=50, default="appel_a_envoye", blank=True, null=True, verbose_name="Etat de la cotisation")
    ventilationpercent = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, verbose_name="pourcentage de ventilation")
    ventilationto = models.ForeignKey(Regionalnetwork, blank=True, null=True, max_length=250, on_delete=models.CASCADE,  related_name='%(class)s_ventilation', verbose_name="Bénéficiaire de la ventilation")
    ventilationdate = models.DateField(verbose_name="Date de paiement de la part ventilée", blank=True, null=True)
    factureventilation = models.CharField(max_length=25, blank=True, null=True, verbose_name="Numéro de facture de la ventilation")
    callcontact = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, verbose_name="animateur régional contact")
    createdate = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updatedate = models.DateTimeField(auto_now=True, verbose_name="Date de dernière mise à jour")

    def __str__(self):
        return "%s - %s" % (self.actor , self.year)

    @property
    def amountincents(self):
        return int(self.amount * 100)

    @classonlymethod
    def _get_next_contribution_number(cls):
        '''
        :return: next unique integer to populate the contributionnumber field
        '''
        # TODO: https://git.startinblox.com/energie-partagee/djangoldp_energiepartagee/issues/26
        # return uuid.uuid4()
        contribution_max_nb = Contribution.objects.aggregate(Max('contributionnumber'))['contributionnumber__max']
        
        if contribution_max_nb is None:
            return 1
            
        return contribution_max_nb + 1

    @classonlymethod
    def get_current_contribution_year(cls):
        return int(date.today().strftime("%Y"))

    @classonlymethod
    def create_annual_contribution(cls, actor):
        now = date.today()
        # payment_date = now + timedelta(30) # 30 days in the future

        c = Contribution(
            actor=actor,
            year=cls.get_current_contribution_year(),
            numberpeople=actor.numberpeople,
            numberemployees=actor.numberemployees,
            turnover=actor.turnover,
            amount=actor.get_next_contribution_amount(),
            contributionnumber=Contribution._get_next_contribution_number(),
            paymentto=actor.regionalnetwork
        )
        c.save()
    
    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view']
        permission_classes = [ContributionPermissions]
        rdf_type = 'energiepartagee:contribution'
        serializer_fields = ['actor', 'year', 'numberpeople', 'numberemployees', 'turnover', 'amount', 'contributionnumber', 'paymentto', 'paymentmethod', 'calldate', 'paymentdate', 'receptdate', 'receivedby', 'contributionstatus', 'ventilationpercent', 'ventilationto', 'ventilationdate', 'factureventilation', 'callcontact', 'amountincents'
        ]


ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('membre', 'Membre'),
]

class Relatedactor(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Acteur", related_name="members")
    role  = models.CharField(choices=ROLE_CHOICES, max_length=50, blank=True, null=True, verbose_name="Rôle de l'utilisateur")

    class Meta(Model.Meta):
        permission_classes = [RelatedactorPermissions]
        view_set = RelatedactorViewSet
        rdf_type = 'energiepartagee:relatedactor'

    def __str__(self):
        return "%s - %s" % (self.user , self.actor)

    @classmethod
    def get_mine(self, user, role=None):
        if is_anonymous_user(user):
            return Relatedactor.objects.none()

        if role is None:
            return Relatedactor.objects.filter(user=user)

        return Relatedactor.objects.filter(user=user, role=role)

    @classmethod
    def get_user_actors_id(self, user, role=None):
        return self.get_mine(user=user, role=role).values_list('actor_id', flat=True)
            

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user(sender, instance, created, **kwargs):
    if created:
        profileInstance = Profile(
            user=instance,
            picture="https://moncompte.energie-partagee.org/img/default_avatar_user.svg"
        )
        profileInstance.save()


@receiver(post_save, sender=Actor)
def create_actor(sender, instance, created, **kwargs):
    if created:
        if not instance.contributions or instance.contributions.exists() == False:
            amount = instance.get_next_contribution_amount()

            memberInstance = instance.members.create(
                role = ROLE_CHOICES[0][0],
                user = instance.managementcontact
            )
            memberInstance.save()

            contributionInstance = instance.contributions.create(
                year = Contribution.get_current_contribution_year(),
                numberpeople=instance.numberpeople,
                numberemployees=instance.numberemployees,
                turnover=instance.turnover,
                amount = amount,
                paymentto = instance.regionalnetwork,
                contributionnumber = Contribution._get_next_contribution_number()
            )
            contributionInstance.save()
            
            integrationstepInstance = Integrationstep(
                packagestep = True,
                adhspacestep = True,
                adhliststep = True,
                regionalliststep = True
            )
            integrationstepInstance.save()
            instance.integrationstep = integrationstepInstance
            
            instance.save()


@receiver(pre_save, sender=Contribution)
def update_status_after_payment_change(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # New contribution
        pass 
    else:
        # Detect change on payment fields
        if old_instance.receivedby == instance.receivedby or \
            old_instance.paymentmethod == instance.paymentmethod or \
            old_instance.paymentdate == instance.paymentdate :

            # Check if payment fields are filled
            if instance.receivedby is not None and \
                instance.paymentmethod is not None and \
                instance.paymentdate is not None :

                # Change status except if is already 'validé' 
                if instance.contributionstatus != CONTRIBUTION_CHOICES[4][0]:
                    instance.contributionstatus = CONTRIBUTION_CHOICES[3][0]
