import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APILiveServerTestCase

from src.wallet.factory import AccountFactory, WalletFactory, TransactionFactory
from src.wallet.models import AccountModel, WalletModel, TransactionModel


# Test Helpers
def create_account():
    account = AccountFactory()
    token = Token.objects.create(user=account)
    account.token = str(token)
    account.save()

    return account, token


class TestWallet(APILiveServerTestCase):
    def setUp(self) -> None:
        self.customer_xid = 'ea0212d3-abd6-406f-8c67-868e814a2436'
        self.reference_id = uuid.uuid4()

    def test_init(self):
        # Init account
        with self.subTest('Success Init'):
            response = self.client.post(
                reverse('api-init'),
                data={'customer_xid': self.customer_xid}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            response_data = response.json().get('data', {})
            self.assertIsNotNone(response_data.get('token'))
            self.assertEqual(response.json().get('status'), 'success')
            self.assertEqual(AccountModel.objects.count(), 1)

        with self.subTest('Error Init - Missing customer_xid'):
            response = self.client.post(
                reverse('api-init')
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json().get('status'), 'fail')

    def test_enable(self):
        account, token = create_account()

        with self.subTest('Wallet Not Found'):
            response_not_found = self.client.post(reverse('api-wallet'), HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response_not_found.status_code, status.HTTP_400_BAD_REQUEST)

        wallet = WalletFactory(account=account)

        # Enable wallet
        with self.subTest('Not authenticated'):
            response = self.client.post(reverse('api-wallet'))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest('Success enabled'):
            response_2 = self.client.post(reverse('api-wallet'), HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
            data_2 = response_2.json().get('data', {})
            self.assertIsNotNone(data_2.get('wallet'))
            self.assertEquals(data_2.get('wallet', {}).get('id'), str(wallet.id))

        with self.subTest('Error enabled - Wallet already enabled'):
            response_3 = self.client.post(
                reverse('api-wallet'),
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response_3.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response_3.json().get('status'), 'fail')
            data_3 = response_3.json().get('data', {})
            self.assertEquals(data_3.get('error'), "Already enabled")

    def test_view(self):
        # View wallet
        account, token = create_account()
        WalletFactory(account=account)

        response = self.client.get(reverse('api-wallet'), HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json().get('data', {})
        self.assertIsNotNone(data.get('wallet'))

    def test_deposit(self):
        account, token = create_account()
        WalletFactory(account=account, status='enabled')

        # Deposit amount
        response = self.client.post(
            reverse('api-deposit'),
            data={
                'amount': 6000,
                'reference_id': self.reference_id
            },
            HTTP_AUTHORIZATION=f"Token {token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wallet = WalletModel.objects.get(account=account)
        self.assertEqual(wallet.balance, 6000)
        self.assertEqual(TransactionModel.objects.count(), 1)

        with self.subTest('Error - Missing amount field'):
            response_error = self.client.post(
                reverse('api-deposit'),
                data={
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response_error.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdrawal(self):
        account, token = create_account()
        wallet = WalletFactory(account=account, status='enabled')

        with self.subTest('Error - Balance is not enough'):
            response_error = self.client.post(
                reverse('api-withdraw'),
                data={
                    'amount': 6000,
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response_error.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest('Error - Balance is not enough'):
            wallet.balance = 10000
            wallet.save()

            # Withdraw amount
            response = self.client.post(
                reverse('api-withdraw'),
                data={
                    'amount': 6000,
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            wallet = WalletModel.objects.get(account=account)
            self.assertEqual(wallet.balance, 4000)
            self.assertEqual(TransactionModel.objects.count(), 1)

        with self.subTest('Error - Missing amount field'):
            error_missing = self.client.post(
                reverse('api-withdraw'),
                data={
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(error_missing.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reference_id(self):
        account, token = create_account()
        WalletFactory(account=account, status='enabled', balance=10000)

        with self.subTest('Error - Reference id is missing'):
            # Deposit wallet
            miss_ref_id = self.client.post(
                reverse('api-deposit'),
                data={
                    'amount': 6000
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(miss_ref_id.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(miss_ref_id.json().get('data', {}).get('error'), 'Please input reference id')

        with self.subTest('Error - Reference id is not unique'):
            # Deposit wallet
            self.client.post(
                reverse('api-deposit'),
                data={
                    'amount': 6000,
                    'reference_id': self.reference_id
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )

            # Withdraw wallet
            response = self.client.post(
                reverse('api-withdraw'),
                data={
                    'amount': 6000,
                    'reference_id': self.reference_id
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json().get('data', {}).get('error'), 'Reference Id must be unique')

        with self.subTest('Get reference id'):
            # Withdraw wallet
            response = self.client.get(reverse('api-reference-id'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsNotNone(response.json().get('data', {}).get('reference_id'))

    def test_disable(self):
        # Disable wallet
        account, token = create_account()
        WalletFactory(account=account, status='enabled')

        with self.subTest('Success disabled wallet'):
            response = self.client.patch(reverse('api-wallet'), HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json().get('data', {})
            self.assertEquals(data.get('wallet', {}).get('status'), "disabled")

        with self.subTest('Error - wallet has been disabled'):
            response_error = self.client.patch(reverse('api-wallet'), HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response_error.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wallet_decorator(self):
        account, token = create_account()

        with self.subTest('Error - Wallet not fund'):
            response_1 = self.client.post(
                reverse('api-withdraw'),
                data={
                    'amount': 6000,
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response_1.status_code, status.HTTP_400_BAD_REQUEST)
            data_1 = response_1.json().get('data', {})
            self.assertEqual(data_1.get('error'), 'Wallet is not found')

        with self.subTest('Error - Wallet disabled'):
            WalletFactory(account=account, status='disabled')
            response_disabled_wallet = self.client.post(
                reverse('api-withdraw'),
                data={
                    'amount': 0,
                    'reference_id': uuid.uuid4()
                },
                HTTP_AUTHORIZATION=f"Token {token}"
            )
            self.assertEqual(response_disabled_wallet.status_code, status.HTTP_400_BAD_REQUEST)
            data_2 = response_disabled_wallet.json().get('data', {})
            self.assertEqual(data_2.get('error'), 'Wallet is disabled')

    def test_transaction_list(self):
        account, token = create_account()
        wallet = WalletFactory(account=account, status='enabled')
        for _ in range(5):
            TransactionFactory(created_by=account, wallet=wallet)

        response = self.client.get(reverse('api-transactions'), HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json().get('data', {})
        self.assertEqual(len(data.get('transactions', [])), 5)
