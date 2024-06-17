from history.models import HistoryModel


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