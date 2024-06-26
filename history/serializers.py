from rest_framework import serializers

from helpers.function import compute_pdf_url
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

    def get_file(self, obj):
        return compute_pdf_url(obj.file.name)