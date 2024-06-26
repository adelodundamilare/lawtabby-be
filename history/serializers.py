from rest_framework import serializers

from history.models import DownloadModel, HistoryModel, UploadModel

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryModel
        fields = '__all__'

class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadModel
        fields = '__all__'

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadModel
        fields = '__all__'