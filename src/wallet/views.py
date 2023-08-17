import uuid

from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from src.wallet.models import AccountModel, WalletModel, TransactionModel
from src.wallet.serializers import InitSerializer, WalletSerializer, DepositSerializer, WithdrawnSerializer, \
    TransactionSerializer, TransactionListSerializer
from src.wallet.utils import jsend_response
from src.wallet.decorators import require_wallet, require_reference_id


@api_view(['POST'])
def api_init(request):
    """This endpoint is used to create an account as well as getting the token for the other API endpoints."""

    serializer = InitSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        xid = serializer.data.get('customer_xid')

        account, create = AccountModel.objects.get_or_create(customer_xid=xid)
        if create:
            token = Token.objects.create(user=account)
            account.token = str(token)

        account.last_login = timezone.now()
        account.save()

        WalletModel.objects.get_or_create(account=account)

        data = {
            "token": str(account.token)
        }
        return jsend_response(code=status.HTTP_201_CREATED, data=data, status='success')

    except serializers.ValidationError:
        data = {
            "error": serializer.errors
        }
        return jsend_response(code=status.HTTP_400_BAD_REQUEST, data=data, status='fail')


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, ])
def api_wallet(request):
    code = status.HTTP_201_CREATED
    data = {}
    response_status = 'success'

    try:
        wallet = WalletModel.objects.get(account=request.user)

        if request.method == 'POST':

            if wallet.status == WalletModel.StatusSelector.disabled:
                wallet.status = WalletModel.StatusSelector.enabled
                wallet.save()
                data['wallet'] = WalletSerializer(wallet).data

            else:
                data['error'] = "Already enabled"
                code = status.HTTP_400_BAD_REQUEST
                response_status = 'fail'

        if request.method == 'PATCH':
            if wallet.status == WalletModel.StatusSelector.enabled:
                wallet.status = WalletModel.StatusSelector.disabled
                wallet.save()
                data['wallet'] = WalletSerializer(wallet).data
                code = status.HTTP_200_OK

            else:
                data['error'] = "Already disabled"
                code = status.HTTP_400_BAD_REQUEST
                response_status = 'fail'

        if request.method == 'GET':
            # View
            data['wallet'] = WalletSerializer(wallet).data
            code = status.HTTP_200_OK

    except WalletModel.DoesNotExist:
        data['error'] = "Wallet is not found"
        code = status.HTTP_400_BAD_REQUEST

    return jsend_response(code=code, data=data, status=response_status)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
@require_wallet()
@require_reference_id()
def api_deposit(request):
    """ API for withdraw money from wallet"""

    serializer = TransactionSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data

        # Get Wallet Data
        wallet = WalletModel.objects.filter(account=request.user).first()

        # Add balance
        wallet.balance += serializer_data.get('amount', 0)
        wallet.save()

        # Create transaction record
        transaction = TransactionModel.objects.create(
            amount=serializer_data.get('amount', 0),
            transaction_type=TransactionModel.TypeSelector.deposit,
            reference_id=serializer_data.get('reference_id'),
            wallet=wallet,
            created=timezone.now(),
            created_by=request.user,
        )

        data = {'deposit': DepositSerializer(transaction).data}
        return jsend_response(code=status.HTTP_201_CREATED, data=data, status='success')

    except serializers.ValidationError:
        data = {"error": serializer.errors}
        return jsend_response(code=status.HTTP_400_BAD_REQUEST, data=data, status='fail')


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
@require_wallet()
@require_reference_id()
def api_withdraw(request):
    """ API for withdraw money from wallet"""

    # Validate request body
    serializer = TransactionSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data

        # Get Wallet
        wallet = WalletModel.objects.filter(account=request.user).first()

        # Validate balance
        if wallet.balance < serializer_data.get('amount', 0):
            data = {'error': 'Not enough balance'}
            return jsend_response(code=status.HTTP_400_BAD_REQUEST, data=data, status='fail')

        # Reduce balance
        wallet.balance -= serializer_data.get('amount', 0)
        wallet.save()

        # Create transaction record
        transaction = TransactionModel.objects.create(
            amount=serializer_data.get('amount', 0),
            transaction_type=TransactionModel.TypeSelector.withdraw,
            reference_id=serializer_data.get('reference_id'),
            wallet=wallet,
            created=timezone.now(),
            created_by=request.user,
        )

        data = {
            'withdrawal': WithdrawnSerializer(transaction).data
        }
        return jsend_response(code=status.HTTP_201_CREATED, data=data, status='success')

    except serializers.ValidationError:
        data = {"error": serializer.errors}
        return jsend_response(code=status.HTTP_400_BAD_REQUEST, data=data, status='fail')


@api_view(['GET'])
def api_reference_id(request):
    data = {"reference_id": str(uuid.uuid4())}
    return jsend_response(code=status.HTTP_200_OK, data=data, status='success')


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@require_wallet()
def api_transactions(request):
    transactions = TransactionModel.objects.filter(created_by=request.user).all()
    data = {'transactions': TransactionListSerializer(transactions, many=True).data}
    return jsend_response(code=status.HTTP_200_OK, data=data, status='success')