from account.models import Account


def find_all(request) -> list[Account]:
    '''Ищет пользователей по нику. Возвращает их список'''
    if request.method == 'POST':
        search = request.POST.get("search", "").strip()
        if not search:
            return []
        return Account.objects.filter(username__contains=search)
    return []
