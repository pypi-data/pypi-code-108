from django.db import models
from django.conf import settings
from .validators import positive_number


class Category(models.Model):
    """Product category model."""

    name = models.CharField(max_length=255, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'Categories'


class AbstractProduct(models.Model):
    """Abstract model for Product models."""

    name = models.CharField(max_length=255, verbose_name='Name')
    barcode = models.CharField(max_length=255, null=True, blank=True, verbose_name='Barcode')
    qrcode = models.CharField(max_length=500, null=True, blank=True, verbose_name='QR-code')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Category')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')
    purchase_price = models.FloatField(validators=[positive_number], verbose_name='Purchase price')
    price = models.FloatField(validators=[positive_number], verbose_name='Price')
    promotion_price = models.FloatField(validators=[positive_number], null=True, blank=True,
                                        verbose_name='Promotional price')
    promotion_product = models.BooleanField(default=False, verbose_name='Promotional product')
    image = models.ImageField(null=True, blank=True, verbose_name='Image')
    active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        abstract = True


class Product(AbstractProduct):
    """The product model is inherited from the 'AbstractProduct' abstract model.
    When you perform actions on the model, you interact with the 'ProductHistory' model."""

    def add_history(self, action_type, exists):
        """Adding history."""

        ProductHistory.objects.create(
            product=self,
            action=action_type,
            name=self.name,
            barcode=self.barcode,
            qrcode=self.qrcode,
            category=self.category,
            product_count=self.product_count,
            purchase_price=self.purchase_price,
            price=self.price,
            promotion_price=self.promotion_price,
            image=self.image,
            active=self.active,
            exists=exists,
        )

    def removal_or_change_history(self):
        """Adding history on 'save'/'update' of the Product model."""

        if not self.pk:
            action_type = ActionType.objects.filter(name='Product addition').first()
        else:
            action_type = ActionType.objects.filter(name='Product change').first()

        super(Product, self).save()

        return action_type

    def unexists_history(self):
        """Adding history on 'delete' of the Product model."""

        action_type = ActionType.objects.filter(name='Product removal').first()

        self.add_history(action_type, False)

        ProductHistory.objects.filter(product=self).update(exists=False)

    def __str__(self):
        return f'[{self.pk}] {self.name}'

    def save(self, **kwargs):
        """Redefined 'create'/'update' function. It then adds an entry to the 'ProductHistory' model."""

        action_type = self.removal_or_change_history()

        self.add_history(action_type, True)

    def delete(self, *args, **kwargs):
        """Redefined 'delete' function. It then adds an entry to the 'ProductHistory' model."""

        self.unexists_history()

        super(Product, self).delete()

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'Products'


class CartList(models.Model):
    """Cart model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to={'is_staff': True, 'is_active': True},
                             on_delete=models.PROTECT, verbose_name='Cashier')

    def __str__(self):
        full_name = self.user.get_full_name()

        if full_name:
            full_name = f' / {self.user.get_full_name()}'

        return f'[{self.pk}] {self.user}{full_name}'

    class Meta:
        verbose_name = 'cart action'
        verbose_name_plural = 'Cart list'


class Cart(models.Model):
    """Open cart model."""

    basket_number = models.ForeignKey(CartList, on_delete=models.CASCADE, verbose_name='Cart number')
    product = models.ForeignKey(Product, limit_choices_to={'active': True}, on_delete=models.PROTECT,
                                verbose_name='Product')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')

    def __str__(self):
        return f'{self.product.price} / {self.product.name}'

    class Meta:
        verbose_name = 'cart'
        verbose_name_plural = 'Open carts'


class ActionType(models.Model):
    """Model of the types of actions performed with the product."""

    name = models.CharField(max_length=255, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'type'
        verbose_name_plural = 'Actions'


class ProductHistory(models.Model):
    """Product history model."""

    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, verbose_name='Product')
    action = models.ForeignKey(ActionType, null=True, on_delete=models.PROTECT, verbose_name='Action')
    name = models.CharField(max_length=255, verbose_name='Name')
    barcode = models.CharField(max_length=255, null=True, blank=True, verbose_name='Barcode')
    qrcode = models.CharField(max_length=500, null=True, blank=True, verbose_name='QR-code')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT, default=None,
                                 verbose_name='Category')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')
    purchase_price = models.FloatField(validators=[positive_number], verbose_name='Purchase price')
    price = models.FloatField(validators=[positive_number], verbose_name='Price')
    promotion_price = models.FloatField(validators=[positive_number], null=True, blank=True,
                                        verbose_name='Promotional price')
    promotion_product = models.BooleanField(default=False, verbose_name='Promotional product')
    image = models.ImageField(null=True, blank=True, verbose_name='Image')
    active = models.BooleanField(verbose_name='Active')
    exists = models.BooleanField(verbose_name='Available')
    action_date = models.DateTimeField(auto_now=True, verbose_name='Date')

    def __str__(self):
        return f'{self.product.name}'

    class Meta:
        verbose_name = 'history'
        verbose_name_plural = 'History'
