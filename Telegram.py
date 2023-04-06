import numpy as np
from telethon.sync import TelegramClient
from telethon import events
import cv2
import pytesseract
import pyperclip

API_ID = 'id'
API_HASH = 'hash'
client = TelegramClient('connection_name', API_ID, API_HASH)


@client.on(events.NewMessage(chats='#id'))
async def get_data(event):
    if event.media:
        await event.download_media(file='image.png')
        img = cv2.imread('image.png', cv2.COLOR_BGR2HSV)
        width, height, _ = img.shape
        img = img[int(0.5 * width):width, int(0.5 * height):height]
        mask = cv2.inRange(img, np.array([36, 25, 25]), np.array([86, 255, 255]))
        img[mask > 0] = np.array([255, 255, 255])
        new_img = cv2.medianBlur(img, 5)
        text = pytesseract.image_to_string(new_img).strip()
        with open('file.txt', 'w') as f:
            f.write(f'{text}/USDT')
        print(text)
        pyperclip.copy(f'{text}_USDT')
        quit()
    else:
        print(event.message.text)


def main():
    print('Zaczęto pracę')
    print('Zprawdzam połączenie z Telegramem')
    try:
        client.start()
        print("Działa. Czekam na kod.")
    except ConnectionError as e:
        print(f'Błąd: {e}')
        quit()
    client.run_until_disconnected()


if __name__ == '__main__':
    main()

