from rest_framework import serializers

from history.models import HistoryModel

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryModel
        fields = '__all__'