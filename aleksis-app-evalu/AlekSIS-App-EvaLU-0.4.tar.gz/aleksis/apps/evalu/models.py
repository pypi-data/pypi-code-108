from base64 import b64decode, b64encode
from collections import OrderedDict
from typing import Dict, List, Optional, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Prefetch, Q, QuerySet
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.translation import gettext as _

from ckeditor.fields import RichTextField
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from aleksis.apps.chronos.models import Subject
from aleksis.apps.evalu.managers import (
    EvaluationGroupManager,
    EvaluationGroupQuerySet,
    EvaluationPhaseManager,
    EvaluationPhaseQuerySet,
    EvaluationRegistrationManager,
    EvaluationRegistrationQuerySet,
)
from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import Group, Person
from aleksis.core.util.core_helpers import get_site_preferences


class EvaluationPhase(ExtensibleModel):
    objects = EvaluationPhaseManager.from_queryset(EvaluationPhaseQuerySet)()

    name = models.CharField(max_length=255, verbose_name=_("Display Name"))
    evaluated_group = models.ForeignKey(
        to=Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Group with teachers which can register for evaluation"),
    )

    registration_date_start = models.DateField(
        verbose_name=_("First date teachers can register themselves for evaluation")
    )
    registration_date_end = models.DateField(
        verbose_name=_("Last date teachers can register themselves for evaluation")
    )
    evaluation_date_start = models.DateField(
        verbose_name=_("First date teachers can start the evaluation")
    )
    evaluation_date_end = models.DateField(verbose_name=_("Date when all evaluations stop"))
    results_date_start = models.DateField(verbose_name=_("First date teachers can see results"))

    privacy_notice = RichTextField(verbose_name=_("Privacy notice which teachers have to agree"))

    def clean(self):
        if self.registration_date_end < self.registration_date_start:
            raise ValidationError(
                _(
                    "The start of the registration period must "
                    "be before the end of the registration period."
                )
            )

        if self.evaluation_date_end < self.evaluation_date_start:
            raise ValidationError(
                _(
                    "The start of the evaluation period must "
                    "be before the end of the evaluation period."
                )
            )

        if self.registration_date_start >= self.evaluation_date_start:
            raise ValidationError(_("The registration has to be started before the evaluation."))

        if self.evaluation_date_end >= self.results_date_start:
            raise ValidationError(
                _("The evaluation has to be finished before users can see results.")
            )

    @property
    def registration_running(self):
        now_dt = timezone.now().date()
        return self.registration_date_start <= now_dt <= self.registration_date_end

    @property
    def status(self) -> str:
        now_dt = timezone.now().date()
        if self.evaluation_date_start <= now_dt <= self.evaluation_date_end:
            return "evaluation"
        elif self.evaluation_date_end < now_dt < self.results_date_start:
            return "evaluation_closed"
        elif now_dt >= self.results_date_start:
            return "results"
        else:
            return "not_started"

    @property
    def members_with_registration(self) -> QuerySet:
        return self.evaluated_group.members.all().prefetch_related(
            Prefetch(
                "evaluation_registrations",
                queryset=EvaluationRegistration.objects.filter(phase=self),
            )
        )

    class Meta:
        verbose_name = _("Evaluation phase")
        verbose_name_plural = _("Evaluation phases")

    def __str__(self):
        return self.name


class ComparisonGroup(ExtensibleModel):
    phase = models.ForeignKey(
        to=EvaluationPhase,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation phase"),
        related_name="comparison_groups",
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    groups = models.ManyToManyField(
        Group, verbose_name=_("Groups"), related_name="evalu_comparison_groups"
    )

    def is_valid_to_store(self, subject: Subject) -> bool:
        """Check if it's allowed to store data for this comparison group."""
        minimum_number = get_site_preferences()["evalu__number_of_persons_comparison_groups"]
        return (
            Person.objects.filter(
                owner_of__in=Group.objects.filter(subject_id=subject.id).filter(
                    Q(pk__in=self.groups.all()) | Q(parent_groups__in=self.groups.all())
                )
            )
            .distinct()
            .count()
            >= minimum_number
        )

    def is_valid_to_show(self, subject: Subject) -> bool:
        """Check if this group is allowed to be shown to the user."""
        minimum_number_persons = get_site_preferences()[
            "evalu__number_of_persons_comparison_groups"
        ]
        minimum_number_results = get_site_preferences()[
            "evalu__number_of_results_comparison_groups"
        ]
        number_of_results = self.results.filter(subject=subject).count()
        number_of_persons = (
            self.done_evaluations_comparison.filter(evaluation_group__group__subject_id=subject.id)
            .values_list("evaluation_group__registration", flat=True)
            .count()
        )
        return (
            number_of_results >= minimum_number_results
            and number_of_persons >= minimum_number_persons
        )

    class Meta:
        verbose_name = _("Comparison group")
        verbose_name_plural = _("Comparison groups")

    def __str__(self):
        return self.name


class EvaluationKeyPair(models.Model):
    private_key = models.TextField(verbose_name=_("Private key"), editable=False)
    public_key = models.TextField(verbose_name=_("Public key"), editable=False)

    class Meta:
        verbose_name = _("Evaluation key set")
        verbose_name_plural = _("Evaluation key set")

    def __str__(self):
        return f"Key {self.pk}"

    def get_public_key(self) -> Optional[RSAPublicKey]:
        """Get the public key."""
        if not self.public_key:
            return None
        public_key = serialization.load_pem_public_key(
            self.public_key.encode(), backend=default_backend()
        )
        return public_key

    def get_private_key(self, password: str) -> Optional[RSAPrivateKey]:
        """Get the private key."""
        if not self.private_key:
            return None
        private_key = serialization.load_pem_private_key(
            self.private_key.encode(), password=password.encode(), backend=default_backend()
        )
        return private_key

    @classmethod
    def create(cls, password: str) -> "EvaluationKeyPair":
        """Create a new public/private key pair from a given password."""
        pair = cls()
        # Generate a key
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        # Store the keys
        pair.private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
        ).decode()
        pair.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        pair.save()

        return pair

    def encrypt(self, message: Union[str, bytes]) -> str:
        """Encrypt a message with the public key."""
        public_key = self.get_public_key()
        if not isinstance(message, bytes):
            message = message.encode()
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )
        return b64encode(ciphertext).decode()

    def decrypt(self, ciphertext: Union[str, bytes], password: str) -> bytes:
        """Decrypt a message with the private key."""
        private_key = self.get_private_key(password)
        if not isinstance(ciphertext, bytes):
            ciphertext = ciphertext.encode()
        plaintext = private_key.decrypt(
            b64decode(ciphertext),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )
        return plaintext

    def test(self, password: str) -> bool:
        """Test to unlock the private key."""
        self.get_private_key(password)
        return True


class EvaluationRegistration(ExtensibleModel):
    objects = EvaluationRegistrationManager.from_queryset(EvaluationRegistrationQuerySet)()

    phase = models.ForeignKey(
        to=EvaluationPhase,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation phase"),
        related_name="registrations",
    )
    person = models.ForeignKey(
        to=Person,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluated person"),
        related_name="evaluation_registrations",
    )
    privacy_accepted = models.BooleanField(verbose_name=_("Privacy notice accepted"))
    delete_after_phase = models.BooleanField(
        default=False, verbose_name=_("Delete evaluation data after this phase?")
    )
    privacy_accepted_at = models.DateTimeField(verbose_name=_("Privacy notice accepted at"))
    privacy_form = models.FileField(blank=True, verbose_name=_("Submitted privacy form as PDF"))
    keys = models.ForeignKey(
        to=EvaluationKeyPair,
        on_delete=models.CASCADE,
        verbose_name=_("Keys used to encrypt the evaluation"),
        editable=False,
    )
    finished = models.BooleanField(default=False, verbose_name=_("Finished"))
    finished_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Finished at"))

    class Meta:
        verbose_name = _("Evaluation registration")
        verbose_name_plural = _("Evaluation registrations")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "phase", "site"], name="person_phase_site_unique"
            )
        ]

    def __str__(self):
        return f"{self.phase}: {self.person}"

    @property
    def finishing_possible(self):
        return (
            bool(self.groups_with_done_evaluations)
            and not self.finished
            and self.phase.status == "evaluation"
        )

    @property
    def results_accessible(self):
        return self.phase.status == "results" or self.finished

    def generate_privacy_form(self):
        """Generate a privacy form for this registration."""
        from .tasks import generate_privacy_form_task

        if not self.pk:
            self.save()
        generate_privacy_form_task.delay(self.pk)

    def sync_evaluation_groups(self):
        possible_groups = (
            Group.objects.annotate(members_count=Count("members"))
            .filter(owners=self.person, members_count__gt=0, subject_id__isnull=False)
            .on_day(self.phase.evaluation_date_start)
        )
        evaluation_groups = {g.group: g for g in self.groups.all() if g.group}

        objects_to_add = []
        for group in possible_groups:
            if group not in evaluation_groups:
                evaluation_group = EvaluationGroup(
                    registration=self, group=group, group_name=group.name
                )
                objects_to_add.append(evaluation_group)
            else:
                evaluation_group = evaluation_groups[group]
                if evaluation_group.group_name != group.name:
                    evaluation_group.group_name = group.name
                    evaluation_group.save()

        if objects_to_add:
            EvaluationGroup.objects.bulk_create(objects_to_add)

    @property
    def groups_with_done_evaluations(self) -> QuerySet:
        """Return all groups with at least one done evaluation."""
        return (
            self.groups.all()
            .annotate(
                members_count=Count("group__members", distinct=True),
                done_evaluations_count=Count("done_evaluations", distinct=True),
            )
            .filter(
                done_evaluations_count__gte=get_site_preferences()[
                    "evalu__number_of_persons_results"
                ]
            )
        )

    @property
    def evaluation_groups_with_stats(self) -> QuerySet:
        """Return evaluation groups with some statistics annotated."""
        return self.groups.all().annotate(
            members_count=Count("group__members", distinct=True),
            done_evaluations_count=Count("done_evaluations", distinct=True),
        )

    @classmethod
    def register(
        cls, phase: EvaluationPhase, person: Person, password: str, delete_after_phase: bool = False
    ):
        """Register a person for an evaluation phase."""
        keys = EvaluationKeyPair.create(password)
        registration, __ = EvaluationRegistration.objects.update_or_create(
            phase=phase,
            person=person,
            defaults={
                "privacy_accepted": True,
                "privacy_accepted_at": timezone.now(),
                "delete_after_phase": delete_after_phase,
                "keys": keys,
            },
        )
        return registration

    def finish(self):
        self.finished = True
        self.finished_at = timezone.now()
        self.save()
        self.groups.all().update(unlocked=False)


class EvaluationGroup(ExtensibleModel):
    objects = EvaluationGroupManager.from_queryset(EvaluationGroupQuerySet)()

    registration = models.ForeignKey(
        to=EvaluationRegistration,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluated person"),
        related_name="groups",
    )
    group = models.ForeignKey(
        to=Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Group of evaluating persons"),
    )
    group_name = models.CharField(max_length=255, verbose_name=_("Group name"))
    unlocked = models.BooleanField(default=False, verbose_name=_("Evaluation unlocked"))

    @property
    def is_unlocked(self):
        return self.unlocked and self.registration.phase.status == "evaluation"

    def lock(self):
        """Lock the group for evaluations."""
        self.unlocked = False
        self.save()

    def unlock(self):
        """Unlock the group for evaluations."""
        self.unlocked = True
        self.save()

    @property
    def possible_comparison_groups(self):
        return self.registration.phase.comparison_groups.filter(
            Q(groups=self.group) | Q(groups__child_groups=self.group)
        ).distinct()

    def get_average_results(self, password: str) -> List[dict]:
        """Get evaluation results as average values for this group."""
        results = []
        for item in (
            EvaluationItem.objects.filter(item_type=QuestionType.AGREEMENT)
            .select_related("part")
            .order_by("part__order", "order")
        ):
            decrypted_values = [r.get_result(password) for r in item.results.filter(group=self)]
            if not decrypted_values:
                continue
            average = sum(decrypted_values) / len(decrypted_values)
            results.append(
                {"item": model_to_dict(item), "average": average, "part": model_to_dict(item.part)}
            )
        return results

    def get_comparison_results(self) -> List[dict]:
        """Get evaluation results as comparison values for this group."""
        # Skip if there is no comparison group
        if not self.group or not self.group.subject:
            return []
        results = []

        # Get comparison groups and prefetch data
        comparison_groups = self.possible_comparison_groups.prefetch_related(
            Prefetch(
                "results", queryset=ComparisonResult.objects.filter(subject=self.group.subject)
            )
        )

        for comparison_group in comparison_groups:
            comparison_results = comparison_group.results.all()

            # Check number of results
            if not comparison_group.is_valid_to_show(self.group.subject):
                continue

            result = {
                "comparison_group": model_to_dict(comparison_group, exclude=["groups"]),
                "subject": model_to_dict(self.group.subject),
            }

            # Calculate average results for every item
            concrete_results = []
            for item in (
                EvaluationItem.objects.filter(item_type=QuestionType.AGREEMENT)
                .select_related("part")
                .order_by("part__order", "order")
            ):
                values = [r.get_result() for r in comparison_results if r.item == item]
                if not values:
                    continue
                average = sum(values) / len(values)
                concrete_results.append(
                    {
                        "item": model_to_dict(item),
                        "average": average,
                        "part": model_to_dict(item.part),
                    }
                )
            result["results"] = concrete_results

            results.append(result)
        return results

    def get_frequency_results(self, password: str) -> List[dict]:
        """Get evaluation results as frequencies of single values for this group."""
        results = []
        for item in EvaluationItem.objects.filter(item_type=QuestionType.AGREEMENT).order_by(
            "part__order", "order"
        ):
            labels = {key: desc for key, desc in Answer.choices}
            frequencies = {key: 0 for key, desc in Answer.choices}
            decrypted_values = [r.get_result(password) for r in item.results.filter(group=self)]

            for value in decrypted_values:
                frequencies[value] += 1

            frequency_result = OrderedDict()
            for key, value in frequencies.items():
                frequency_result[key] = {
                    "label": labels[key],
                    "frequency": value,
                    "background_color": Answer.background_colors[key],
                    "border_color": Answer.border_colors[key],
                }

            results.append({"item": model_to_dict(item), "frequencies": frequency_result})
        return results

    def get_free_text_results(self, password: str) -> List[dict]:
        """Get all free text evaluation results for this group."""
        results = []
        for item in EvaluationItem.objects.filter(item_type=QuestionType.FREE_TEXT).order_by(
            "part__order", "order"
        ):
            decrypted_values = [r.get_result(password) for r in item.results.filter(group=self)]
            answers = [v for v in decrypted_values if v]
            results.append({"item": model_to_dict(item), "answers": answers})
        return results

    def save(self, *args, **kwargs):
        if self.group:
            self.group_name = self.group.name or self.group.short_name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Evaluation group")
        verbose_name_plural = _("Evaluation groups")
        constraints = [
            models.UniqueConstraint(
                fields=["registration", "group", "site"], name="registration_group_site_unique"
            )
        ]


class DoneEvaluation(ExtensibleModel):
    group = models.ForeignKey(
        to=EvaluationGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation group"),
        related_name="done_evaluations",
    )
    evaluated_by = models.ForeignKey(
        to=Person, on_delete=models.CASCADE, verbose_name=_("Evaluated by")
    )

    class Meta:
        verbose_name = _("Done evaluation")
        verbose_name_plural = _("Done evaluations")
        constraints = [
            models.UniqueConstraint(
                fields=["group", "evaluated_by", "site"],
                name="registration_group_evaluated_by_site_unique",
            )
        ]


class EvaluationPart(ExtensibleModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    order = models.IntegerField(verbose_name=_("Order"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Evaluation part")
        verbose_name_plural = _("Evaluation parts")
        constraints = [
            models.UniqueConstraint(fields=["order", "site"], name="order_site_unique"),
            models.UniqueConstraint(fields=["name", "site"], name="name_site_unique"),
        ]


class QuestionType(models.TextChoices):
    FREE_TEXT = "free_text", _("Free text")
    AGREEMENT = "agreement", _("Agreement")


class Answer(models.IntegerChoices):
    TRUE = 1, _("Is true")
    MOSTLY_TRUE = 2, _("Is mostly true")
    LESS_TRUE = 3, _("Is less true")
    NOT_TRUe = 4, _("Is not true")

    @classproperty
    def background_colors(cls) -> Dict[int, str]:  # noqa
        return {
            1: "rgba(75, 192, 192, 0.2)",
            2: "rgba(255, 205, 86, 0.2)",
            3: "rgba(255, 159, 64, 0.2)",
            4: "rgba(255, 99, 132, 0.2)",
        }

    @classproperty
    def border_colors(cls) -> Dict[int, str]:  # noqa
        return {
            1: "rgb(75, 192, 192)",
            2: "rgb(255, 205, 86)",
            3: "rgb(255, 159, 64)",
            4: "rgb(255, 99, 132)",
        }


class EvaluationItem(ExtensibleModel):
    part = models.ForeignKey(
        to=EvaluationPart,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation part"),
        related_name="items",
    )
    order = models.IntegerField(verbose_name=_("Order"))
    name = models.CharField(
        max_length=255, verbose_name=_("Name"), help_text=_("as shown in results")
    )
    question = models.TextField(
        verbose_name=_("Question"), help_text=_("as shown on evaluation form")
    )
    item_type = models.CharField(
        choices=QuestionType.choices, max_length=255, verbose_name=_("Question type")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Evaluation item")
        verbose_name_plural = _("Evaluation items")
        constraints = [
            models.UniqueConstraint(fields=["part", "site", "order"], name="part_site_order_unique")
        ]


class EvaluationResult(ExtensibleModel):
    group = models.ForeignKey(
        to=EvaluationGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation group"),
        related_name="results",
    )
    item = models.ForeignKey(
        to=EvaluationItem,
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
        related_name="results",
    )
    result = models.TextField(verbose_name=_("Encrypted result"))
    result_key = models.TextField(verbose_name=_("Encrypted fernet key"))

    def store_result(self, result: Union[str, int], commit: bool = False):
        if not self.group:
            raise ValueError("No evaluation group set: encryption impossible.")
        message = str(result)

        fernet_key = Fernet.generate_key()

        # Encrypt fernet key and store it
        encrypted_fernet_key = self.group.registration.keys.encrypt(fernet_key)
        self.result_key = encrypted_fernet_key

        # Encrypt message and store it
        fernet = Fernet(fernet_key)
        self.result = b64encode(fernet.encrypt(message.encode())).decode()

        if commit:
            self.save()

    def add_comparison_results(self, result: str):
        if not self.group.group or not self.group.group.subject:
            # Can't store comparison results without a group
            return
        subject = self.group.group.subject
        for comparison_group in self.group.possible_comparison_groups:
            if comparison_group.is_valid_to_store(subject):
                comparison_result = ComparisonResult(
                    comparison_group=comparison_group,
                    subject=subject,
                    item=self.item,
                    result=result,
                )
                comparison_result.save()
                DoneEvaluationComparison.objects.get_or_create(
                    comparison_group=comparison_group, evaluation_group=self.group
                )

    def get_result(self, password: str) -> Union[str, int]:
        # Decrypt fernet key
        fernet_key = self.group.registration.keys.decrypt(self.result_key, password)

        # Decrypt result
        fernet = Fernet(fernet_key)
        result = fernet.decrypt(b64decode(self.result.encode())).decode()

        if self.item.item_type == QuestionType.AGREEMENT:
            return int(result)
        return result

    class Meta:
        verbose_name = _("Evaluation result")
        verbose_name_plural = _("Evaluation results")


class ComparisonResult(ExtensibleModel):
    comparison_group = models.ForeignKey(
        to=ComparisonGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Comparison group"),
        related_name="results",
    )
    subject = models.ForeignKey(
        to=Subject,
        on_delete=models.CASCADE,
        verbose_name=_("Subject"),
        related_name="evalu_results",
    )

    item = models.ForeignKey(
        to=EvaluationItem,
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
        related_name="comparison_results",
    )
    result = models.TextField(verbose_name=_("Result"))

    def get_result(self) -> Union[str, int]:
        if self.item.item_type == QuestionType.AGREEMENT:
            return int(self.result)
        return self.result

    class Meta:
        verbose_name = _("Comparison result")
        verbose_name_plural = _("Comparison results")


class DoneEvaluationComparison(ExtensibleModel):
    comparison_group = models.ForeignKey(
        to=ComparisonGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Comparison group"),
        related_name="done_evaluations_comparison",
    )
    evaluation_group = models.ForeignKey(
        to=EvaluationGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Evaluation group"),
        related_name="done_evaluations_comparison",
    )

    class Meta:
        verbose_name = _("Done evaluation (comparison)")
        verbose_name_plural = _("Done evaluations (comparison)")
