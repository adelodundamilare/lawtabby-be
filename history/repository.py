from history.models import DownloadModel, HistoryModel, UploadModel


class HistoryRepository():
    def create(self, data):
        return HistoryModel.objects.create(**data)

    def find_by_user(self, user):
        try:
            return HistoryModel.objects.filter(user=user).order_by('-created_at')
        except HistoryModel.DoesNotExist:
            return None

    def find_latest(self, user):
        try:
            return HistoryModel.objects.filter(user=user).order_by('-created_at')[:5]
        except HistoryModel.DoesNotExist:
            return None

class DownloadRepository():
    def create(self, data):
        return DownloadModel.objects.create(**data)

    def find_by_user(self, user):
        try:
            return DownloadModel.objects.filter(user=user).order_by('-created_at')
        except DownloadModel.DoesNotExist:
            return None

    def find_latest(self, user):
        try:
            return DownloadModel.objects.filter(user=user).order_by('-created_at')[:5]
        except DownloadModel.DoesNotExist:
            return None

class UploadRepository():
    def create(self, data):
        return UploadModel.objects.create(**data)

    def find_by_user(self, user):
        try:
            return UploadModel.objects.filter(user=user).order_by('-created_at')
        except UploadModel.DoesNotExist:
            return None

    def find_latest(self, user):
        try:
            return UploadModel.objects.filter(user=user).order_by('-created_at')[:5]
        except UploadModel.DoesNotExist:
            return None