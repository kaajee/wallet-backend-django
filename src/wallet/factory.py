import uuid

import factory
from django.contrib.auth import get_user_model
from factory import SubFactory

from src.wallet.models import WalletModel, TransactionModel


class AccountFactory(factory.django.DjangoModelFactory):
    customer_xid = uuid.uuid4()

    class Meta:
        model = get_user_model()


class WalletFactory(factory.django.DjangoModelFactory):
    account = SubFactory(AccountFactory)

    class Meta:
        model = WalletModel


class TransactionFactory(factory.django.DjangoModelFactory):
    created_by = SubFactory(AccountFactory)
    wallet = SubFactory(WalletFactory)
    amount = 10_000
    transaction_type = TransactionModel.TypeSelector.deposit
    reference_id = factory.Faker('uuid4')

    class Meta:
        model = TransactionModel
