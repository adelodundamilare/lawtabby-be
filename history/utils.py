from history.models import UploadModel
from history.repository import DownloadRepository, HistoryRepository, UploadRepository
from history.serializers import DownloadSerializer, UploadSerializer

# HISTORY
def find_all(user):
    repo = HistoryRepository()
    return repo.find_by_user(user)

def latest(user):
    repo = HistoryRepository()
    return repo.find_latest(user)

def add_to_history(user, title):
    history_repo = HistoryRepository()
    history_repo.create({
        'user':user,
        'title':title
    })

# DOWNLOADS
def add_to_downloads(user, file, file_name):
    repo = DownloadRepository()
    repo.create({
        'user':user,
        'file': file,
        'file_name': file_name
    })

def fetch_user_downloads(user):
    repo = DownloadRepository()
    downloads = repo.find_by_user(user)
    return DownloadSerializer(downloads, many=True).data

# UPLOADS
def add_to_uploads(user, input_file):
    instance = UploadModel(user=user)
    instance.file.save(input_file.name, input_file)
    instance.file_name.save(input_file.name)
    instance.save()


def fetch_user_uploads(user):
    repo = UploadRepository()
    uploads = repo.find_by_user(user)
    return UploadSerializer(uploads, many=True).data