from rest_framework import serializers

from src.wallet.models import WalletModel, TransactionModel


class InitSerializer(serializers.Serializer):
    customer_xid = serializers.CharField(required=True)


class WalletSerializer(serializers.ModelSerializer):
    owned_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WalletModel
        fields = ['id', 'owned_by', 'status', 'enabled_at', 'balance']

    def get_owned_by(self, instance):
        return instance.account.id


class TransactionSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    reference_id = serializers.CharField(required=True)


class DepositSerializer(serializers.ModelSerializer):
    deposited_by = serializers.SerializerMethodField(read_only=True)
    deposited_at = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TransactionModel
        fields = ['id', 'deposited_by', 'status', 'deposited_at', 'amount', 'reference_id']

    def get_deposited_by(self, instance):
        return instance.created_by.id

    def get_deposited_at(self, instance):
        return instance.created.isoformat()

    def get_status(self, instance):
        return "success"


class WithdrawnSerializer(serializers.ModelSerializer):
    withdrawn_by = serializers.SerializerMethodField(read_only=True)
    withdrawn_at = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TransactionModel
        fields = ['id', 'withdrawn_by', 'status', 'withdrawn_at', 'amount', 'reference_id']

    def get_withdrawn_by(self, instance):
        return instance.created_by.id

    def get_withdrawn_at(self, instance):
        return instance.created.isoformat()

    def get_status(self, instance):
        return "success"


class TransactionListSerializer(serializers.ModelSerializer):
    """
    {
        "id": "7ae5aa7b-821f-4559-874b-07eea5f47962",
        "status": "success",
        "transacted_at": "1994-11-05T08:15:30-05:00",
        "type": "deposit",
        "amount": 14000,
        "reference_id": "305247dc-6081-409c-b418-e9d65dee7a94"
      }
    """
    transacted_at = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TransactionModel
        fields = ['id', 'status', 'transacted_at', 'type', 'amount', 'reference_id']

    def get_transacted_at(self, instance):
        return instance.created.isoformat()

    def get_type(self, instance):
        return instance.transaction_type

    def get_status(self, instance):
        return "success"
