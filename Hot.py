import hotbit
from pandas import DataFrame, read_csv
from os.path import isfile
from os import remove
from datetime import date
from time import sleep
from telethon.sync import TelegramClient
from threading import Thread
import pyperclip


class Data:
    CLIENT = None
    MARKET = None

    @classmethod
    def process_maintenance(cls):
        while True:
            sleep(40)
            if Data.CLIENT is not None:
                Data.CLIENT.serverTime()


def save_trade(exit_price: str) -> None:
    if not isfile('data.csv'):
        data: DataFrame = DataFrame(columns=['Market', 'Cena wejścia', 'Ilość', 'Cena wyjścia', 'Różnica', '%'])
        data.index.name = 'Data'
    else:
        data: DataFrame = read_csv('data.csv', sep=',', encoding='utf-8', index_col='Data')
    if not isfile('buy.csv'):
        print('Error: Plik buy.csv nie istnieje')
        return
    else:
        buy_data: DataFrame = read_csv('buy.csv', sep=',', encoding='utf-8', index_col='X')
    index = date.today()
    last_buy = buy_data.tail(1)
    row_data = dict(zip(data.columns, [last_buy['Market'].values[0], last_buy['Cena wejścia'].values[0],
                                       last_buy['Ilość'].values[0], exit_price, '', '']))
    row_data['Różnica'] = float(exit_price) - float(row_data['Cena wejścia'])
    row_data['%'] = (row_data['Różnica'] / float(row_data['Cena wejścia'])) * 100
    data.loc[index] = row_data
    data.to_csv('data.csv')
    remove('buy.csv')


def save_buy(market: str, open_price: str, amount: float) -> None:
    if not isfile('buy.csv'):
        data: DataFrame = DataFrame(columns=['Market', 'Cena wejścia', 'Ilość'])
        data.index.name = 'X'
    else:
        data: DataFrame = read_csv('buy.csv', sep=',', encoding='utf-8', index_col='X')
    row_data = dict(zip(data.columns, [market, open_price, amount]))
    data.loc[0] = row_data
    data.to_csv('buy.csv')


def get_currency() -> str:
    API_ID = '#'
    API_HASH = '#'
    with TelegramClient('#', API_ID, API_HASH) as client:
        client: TelegramClient
        chat = client.get_entity('#')
        last_message = client.get_messages(chat, limit=1)[0].text.split()
        if len(last_message) == 1:
            pyperclip.copy(f'{last_message[0]}_USDT')
            return f'{last_message[0]}/USDT'
        else:
            print('Error: Nie wykryto monety na telegramie')
            quit()


def buy() -> None:
    client, market = starter()
    amount = 0.0
    current_price = ''
    try:
        current_price = client.marketPrice(market=market, side="BUY", amount=amount)
    except TypeError:
        print(f'Error: Rynek nie istnieje')
        exit()
    max_amount = float(amount) / float(current_price)
    data = client.order(market=market, side="BUY", price=current_price, amount=max_amount)
    print('')
    if data.get('Code') == 1100:
        print(f'Error: {data.get("Msg")}')
    else:
        print(f'Kupiono: {market}'
              f'\nZa: {amount}'
              f'\nIlość: {max_amount}'
              f'\nPo cenie:{current_price}')
        save_buy(market, current_price, max_amount)


def starter() -> list[hotbit.Hotbit, str]:
    global has_started
    if not has_started:
        client: hotbit.Hotbit = create_auth()
        Data.CLIENT = client
        market = get_currency()
        Data.MARKET = market
        has_started = True
        proces = Thread(target=Data.process_maintenance)
        proces.start()
        return [client, market]
    else:
        return [Data.CLIENT, Data.MARKET]


def sell():
    client, market = starter()
    best_price_arr = []
    amount_arr = []
    input('Zatwierdź aby sprzedać: ')
    for step in range(2):
        amount_arr.append(float(client.balanceQuery()['result'][market.split("/")[0]].get('available')))
        if amount_arr[step] == 0.0:
            amount_arr.pop()
            break
        print(f'Step: {step}')
        best_price_arr.append(client.marketPrice(market=market, side="sell", amount=amount_arr[step]))
        data = client.order(market=market, side="sell", price=best_price_arr[step], amount=amount_arr[step])
        if not data.get('Code') == 1100:
            print(f'Error: {data.get("Msg")}')
    best_ask = sum(best_price_arr)
    max_amount = sum(amount_arr)
    print('-------------'
          '\nPodsumowanie'
          f'\nSprzedałeś: {market}'
          f'\nIlość: {max_amount}'
          f'\nZa cenę: {best_ask}'
          f'\n-----------')
    save_trade(best_ask)


def create_auth() -> hotbit.Hotbit:
    auth = hotbit.auth.cookie(
        cookies="")
    return hotbit.Hotbit(auth)


if __name__ == '__main__':
    print('Trwa uruchamianie')
    has_started = False
    while True:
        print('1-Kupić'
              '\n2-Sprzedać'
              '\n3-All_in_One'
              '\n4-Wyjść')
        choice = input('Co wybierasz: ')
        print('')
        match choice:
            case '1':
                buy()
            case '2':
                sell()
            case '3':
                buy()
                sell()
            case '4':
                exit()
            case _:
                print('Error: Błąd wyboru')
                sleep(1)
