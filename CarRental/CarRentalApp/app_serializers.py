from rest_framework import serializers

from .models import Coverage
from .models import Claim
from .models import Payment
from .models import History

class SignUpSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)

class SignInSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=False)

class SignVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)

class RequestVerifySerializer(serializers.Serializer):
    confirmation_hash = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)

class RequestPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required = False)
    paymentMethod = serializers.JSONField(required = False)

class AddCoverageSerializer(serializers.ModelSerializer):

    # name = serializers.CharField(max_length=200)
    # latitude = serializers.FloatField()
    # longitude = serializers.FloatField()
    # address = serializers.CharField()
    # company_id = serializers.IntegerField(required = False)
    # start_at = serializers.DateTimeField(required = False)
    # end_at = serializers.DateTimeField(required = False)
    # video_mile = serializers.CharField(max_length=200, required = False)
    # video_vehicle = serializers.CharField(max_length=200, required = False)
    # state = serializers.IntegerField(required = False)  # COVERED: 1, UNCOVERED: 2

    class Meta:
        model = Coverage
        fields = '__all__'

class AddClaimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Claim
        fields = '__all__'

class AddPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'

class AddHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = '__all__'
