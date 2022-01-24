from django.db import models

from pfx.pfxcore.decorator import rest_property
from pfx.pfxcore.models import JSONReprMixin


class Author(models.Model):
    first_name = models.CharField("First Name", max_length=30)
    last_name = models.CharField("Last Name", max_length=30)
    slug = models.SlugField("Slug", unique=True)
    gender = models.CharField("Gender", max_length=10, choices=[
        ('male', "Male"), ('female', "Female")], default='male')
    science_fiction = models.BooleanField("Science Fiction", default=False)
    created_at = models.DateField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @rest_property("Name Length", "IntegerField")
    def name_length(self):
        return len(str(self))


class BookType(JSONReprMixin, models.Model):
    name = models.CharField("Name", max_length=30)
    slug = models.SlugField("Slug")

    class Meta:
        verbose_name = "Book Type"
        verbose_name_plural = "Book Types"

    def json_repr(self):
        return dict(pk=self.pk,
                    resource_slug=self.slug,
                    resource_name=str(self))

    def __str__(self):
        return f"{self.name}"


class Book(models.Model):
    name = models.CharField("Name", max_length=30)
    author = models.ForeignKey(
        'tests.Author', on_delete=models.RESTRICT,
        related_name='books', verbose_name="Author")
    type = models.ForeignKey(
        'tests.BookType', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='books', verbose_name="Book Type")
    pub_date = models.DateField("Pub Date")
    created_at = models.DateField("Created at", auto_now_add=True)
    pages = models.IntegerField("Pages", null=True, blank=True)
    rating = models.FloatField("Rating", null=True, blank=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.name}"
