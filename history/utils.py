from history.repository import HistoryRepository

def find_all(user):
    repo = HistoryRepository()
    return repo.find_by_user(user)

def latest(user):
    repo = HistoryRepository()
    return repo.find_latest(user)