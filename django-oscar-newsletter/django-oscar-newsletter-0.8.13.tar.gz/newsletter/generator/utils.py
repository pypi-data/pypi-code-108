from django.utils.text import slugify
from urllib.parse import urlparse
from ..models import Message, Article


class MessageGenerator:
    title = ''

    def __init__(self, request, offer, newsletter, with_prices):
        self.request = request
        self.offer = offer
        self.newsletter = newsletter
        self.with_prices = with_prices
        self.range = offer.benefit.range
        self.range_products = self.range.rangeproduct_set.filter(
            cached_slide__isnull=False
        ).exclude(cached_slide='')

    def generate(self):
        message = self._generate_message()
        self._generate_articles(message)
        return message

    def _generate_message(self):
        slug = slugify(self.offer.name) + '_'
        suffix = 0
        while Message.objects.filter(
                newsletter=self.newsletter,
                slug=slug + str(suffix)):
            suffix += 1

        message = Message.objects.create(
            newsletter=self.newsletter,
            slug=slug + str(suffix),
            title=self.offer.name,
        )
        return message

    def _get_image(self, range_product):
        image = None
        if self.with_prices:
            image = range_product.cached_slide
        elif range_product.image:
            image = range_product.image.file
        return image or None

    def _generate_articles(self, message):
        articles = []
        for range_product in self.range_products:
            image = self._get_image(range_product)
            article = Article.objects.update_or_create(
                post=message,
                image=image,
                defaults={
                    'title': range_product.get_title().replace('<br>', ' '),
                    'url': self.absolute_url(range_product.get_link()),
                    'text': '',
                }
            )[0]
            articles.append(article)
        return articles

    def absolute_url(self, url):
        is_absolute = bool(urlparse(url).netloc)
        if is_absolute:
            return url
        return self.request.build_absolute_uri(url)
