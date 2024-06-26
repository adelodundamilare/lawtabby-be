from rest_framework import serializers

from helpers.function import compute_file_url
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

    def get_file_url(self, obj):
        return compute_file_url(obj.file.name)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['file'] = self.get_file_url(instance)
        return representation