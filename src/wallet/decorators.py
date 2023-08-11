from rest_framework import status

from src.wallet.models import WalletModel, TransactionModel
from src.wallet.utils import jsend_response


def require_wallet():
    """ A custom decorator that checks if the user has a wallet and status is enabled.
    """

    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            code = status.HTTP_400_BAD_REQUEST
            data = {}
            wallet = WalletModel.objects.filter(account=request.user).first()
            response_status = 'fail'

            if wallet is None:
                data['error'] = 'Wallet is not found'
                return jsend_response(code=code, data=data, status=response_status)

            # Validate wallet status
            if wallet.status == WalletModel.StatusSelector.disabled:
                data['error'] = 'Wallet is disabled'
                return jsend_response(code=code, data=data, status=response_status)

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def require_reference_id():
    """ A custom decorator that checks if reference id has been used or not.
    """

    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            code = status.HTTP_400_BAD_REQUEST
            data = {}
            response_status = 'fail'

            reference_id = request.data.get('reference_id')
            if reference_id is None:
                data['error'] = 'Please input reference id'
                return jsend_response(code=code, data=data, status=response_status)

            # Validate reference id
            exist_reference_id = TransactionModel.objects.filter(reference_id=reference_id).first()
            if exist_reference_id is not None:
                data['error'] = 'Reference Id must be unique'
                return jsend_response(code=code, data=data, status=response_status)

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator
