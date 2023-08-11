from django.urls import path

from src.wallet.views import api_init, api_wallet, api_deposit, api_withdraw, api_reference_id, api_transactions

urlpatterns = [
    path('init', api_init, name='api-init'),
    path('wallet', api_wallet, name='api-wallet'),
    path('wallet/transactions', api_transactions, name='api-transactions'),
    path('wallet/deposits', api_deposit, name='api-deposit'),
    path('wallet/withdrawals', api_withdraw, name='api-withdraw'),
    path('reference-id', api_reference_id, name='api-reference-id'),
]