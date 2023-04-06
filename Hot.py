import hotbit
from pandas import DataFrame, read_csv
from os.path import isfile
from datetime import date


def to_file(*args) -> None:
    if not isfile('data.csv'):
        data: DataFrame = DataFrame(columns=['Market', 'Cena wejścia', 'Ilość', 'Cena wyjścia', 'Różnica', '%'])
        data.index.name = 'Data'
    else:
        data: DataFrame = read_csv('data.csv', sep=',', encoding='utf-8', index_col='Data')
    index = date.today()
    row_data = dict(zip(data.columns, args))
    data.loc[index] = row_data
    data.to_csv('data.csv')


auth = hotbit.auth.cookie(
    cookies="cookie")
client = hotbit.Hotbit(auth)

i = 0
print("Zacząłem działanie")
while True:
    with open('file.txt', 'r') as f:
        lines = f.readlines()
        if lines:
            market = lines[-1].strip()
            print(f'Odczytano wartość: {market}')
            amount = 4.5
            z = client.marketPrice(market=market, side="BUY", amount=amount)
            max_amount = float(amount) / float(z)
            print(client.order(market=market, side="BUY", price=z, amount=max_amount))
            best_price_arr = []
            amount_arr = []
            input(f'Kiedy sprzedać ({z}): ')
            for i in range(4):
                amount_arr.append(float(client.balanceQuery()['result'][market.split("/")[0]].get('available')))
                if amount_arr[i] == 0.0:
                    amount_arr.pop()
                    break
                best_price_arr.append(client.marketPrice(market=market, side="sell", amount=amount_arr[i]))
                print(client.order(market=market, side="sell", price=best_price_arr[i], amount=amount_arr[i]))
            with open('file.txt', 'w') as f:
                f.write('')
            best_ask = sum(best_price_arr)
            max_amount = sum(amount_arr)
            print(f'\nMarket: {market} \nCena: {z} Ilość: {max_amount}\nZa:{best_ask}\nRóźnica: {best_ask - z} '
                  f'{(best_ask - z) / z * 100:.3f}%')
            to_file(market, z, max_amount, best_ask, f'{best_ask - z}', f'{(best_ask - z) / z * 100:.3f}')
            break

    if i % 30 == 0:
        client.serverTime()
