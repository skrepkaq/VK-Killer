from account.models import Account


def find_all(request) -> list[Account]:
    '''Ищет пользователей по нику. Возвращает их список'''
    if request.method == 'POST':
        search = request.POST["search"]
        return Account.objects.filter(username__contains=search)
    return []
