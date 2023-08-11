import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountManager(BaseUserManager):
    def create_user(self, customer_xid, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not customer_xid:
            raise ValueError(_("The customer_xid must be set"))

        user = self.model(customer_xid=customer_xid, **extra_fields)
        user.save()
        return user


class AccountModel(AbstractBaseUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_xid = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255)

    USERNAME_FIELD = "customer_xid"
    REQUIRED_FIELDS = []

    objects = AccountManager()

    class Meta:
        db_table = 'account'

    def __str__(self):
        return self.customer_xid


class WalletModel(models.Model):
    """ Model that contains information about user wallet. """

    class StatusSelector(models.TextChoices):
        enabled = 'enabled', _('enabled')
        disabled = 'disabled', _('disabled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.IntegerField(default=0)
    account = models.OneToOneField(AccountModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=StatusSelector.choices, default=StatusSelector.disabled)
    enabled_at = models.DateTimeField('created', auto_now_add=True)

    class Meta:
        db_table = 'wallet'


class TransactionModel(models.Model):
    """ Model that contains information about every wallet transaction (deposit/withdrawal). """

    class TypeSelector(models.TextChoices):
        deposit = 'deposit', _('Deposit')
        withdraw = 'withdraw', _('Withdraw')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.IntegerField(default=0)
    transaction_type = models.CharField(max_length=50, choices=TypeSelector.choices, default=TypeSelector.deposit)
    reference_id = models.CharField(max_length=255, unique=True)
    wallet = models.ForeignKey(WalletModel, on_delete=models.CASCADE)
    created = models.DateTimeField(
        'created',
        auto_now_add=True,
        help_text='Date/time this object was created.'
    )
    created_by = models.ForeignKey(AccountModel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'transaction'
