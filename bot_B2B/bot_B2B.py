# -*- coding: cp1251 -*-
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import datetime
import requests


WEBHOOK_HOST = 'https://github.com/TsvyakhVova/Bot_B2B_Insight/blob/main/bot_B2B/bot_B2B.py'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 5000

class UserState(StatesGroup):
    name = State()
    insite = State()

CREDENTIALS_FILE = 'telegram-bot-b2b-374237aaeb9f.json'
spreadsheet_id = '1G_B6z0R0JB3KNN87g000Og1fSmwj3niQIQchy2ZJdzM'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    [' https://www.googleapis.com/auth/spreadsheets ',
    'https://www.googleapis.com/auth/drive '])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

API_TOKEN = '6188981370:AAFOjbyJHLnlCx7lvkf-B9rG0WB5VxA2TB8'

button_yes = KeyboardButton('Äà')
button_no = KeyboardButton('Íåò')
button_yes_photo = KeyboardButton('Äà, ôîòî åñòü')
button_no_photo = KeyboardButton('Íåò, ôîòî íåò')
button1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_yes).add(button_no)
button2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_yes_photo).add(button_no_photo)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())
 
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
   await message.reply("Ïðèâåò, ñàìûé ïðîäâèíóòûé è çàèíòåðåñîâàííûé â ðàçâèòèè B2B!")
   await message.reply("Ðàññêàæè ñâîè èíñàéòû")
   await message.reply("Ãîòîâ íà÷àòü ðàáîòàòü ?", reply_markup=button1)
   
@dp.message_handler(filters.Text("Äà"))
async def with_puree(message: types.Message):
    await message.reply("Ââåäè ñâîè èìÿ è ôàìèëèþ")
    await UserState.name.set()

with open("Index.txt") as file:
    I_index = file.read()

@dp.message_handler(state=UserState.name)
async def get_username(message: types.Message, state: FSMContext):
    print(I_index)
    await state.update_data(name=message.text)
    data = await state.get_data()
    Date = datetime.datetime.now()
    await message.answer(f"Èìÿ: {data['name']}\n")
    await message.answer("Äàòà:"+ str(Date))
    text = data['name']
    Date_Values = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range = "A"+ str(I_index),
        valueInputOption="RAW",
        body={
            "values": [[""+str(Date)+""]]}
        ).execute()
    Name_Values = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range = "B"+ str(I_index),
        valueInputOption="RAW",
        body={
            "values": [[""+str(text)+""]]}
        ).execute()
    await state.finish()
    await message.reply("Êðàòêî ðàññêàæè ñâîþ èäåþ")
    await UserState.insite.set()
    
@dp.message_handler(state=UserState.insite)
async def get_username(message: types.Message, state: FSMContext):
    global I_index
    await state.update_data(insite=message.text)
    data = await state.get_data()
    await message.answer(f"Èíñàéò: {data['insite']}\n")
    text = data['insite']
    Insite_Values = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range = "C" + str(I_index),
        valueInputOption="RAW",
        body={
            "values": [[""+str(text)+""]]}
        ).execute()
    await state.finish()
    await message.reply("Õîðîøàÿ èäåÿ, ÿ å¸ çàïèñàë. Ó òåáÿ åñòü ôîòî ?", reply_markup=button2)

@dp.message_handler(filters.Text("Äà, ôîòî åñòü"))
async def with_puree(message: types.Message):
    await message.reply("Îòïðàâü ìíå ôîòî èç ãàëëåðåè, ÿ åãî ñîõðàíþ ó ñåáÿ")

@dp.message_handler(filters.Text("Íåò, ôîòî íåò"))
async def with_puree(message: types.Message):
    global I_index
    await message.reply("Õîðîøî, ôîòî íåò. Åñëè ïîÿâèòñÿ íîâûé èíñàéò ïèøè /start")
    I_index = int(I_index) + 1
    my_file = open("Index.txt", "w")
    my_file.write(str(I_index))
    my_file.close()

URI = f"https://api.telegram.org/bot{API_TOKEN}/getFile?file_id="
URI_new = f"https://api.telegram.org/file/bot{API_TOKEN}/"

@dp.message_handler(content_types=['photo'])
async def URL_Photo(message: types.Message):
    global I_index
    file_id = message.photo[3].file_id
    resp = requests.get(URI+file_id)
    img_path = resp.json()['result']['file_path']
    requests.get(URI_new+img_path)
    print(URI_new+img_path)
    photo_link = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range = "D" + str(I_index),
        valueInputOption="RAW",
        body={
            "values": [[URI_new+img_path]]}
        ).execute()
    I_index = int(I_index) + 1
    my_file = open("Index.txt", "w")
    my_file.write(str(I_index))
    my_file.close()
    await message.reply("Õîðîøî, ôîòî ÿ ñîõðàíèë. Åñëè ïîÿâèòñÿ íîâûé èíñàéò ïèøè /start")

@dp.message_handler(filters.Text("Íåò"))
async def with_puree(message: types.Message):
    await message.reply("Õîðîøî, ÿ òåáÿ ïîíÿë. Åñëè ïîÿâèòñÿ íîâûé èíñàéò ïèøè /start")


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start

async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)
   start_webhook(
       dispatcher=dp,
       webhook_path=WEBHOOK_PATH,
       on_startup=on_startup,
       on_shutdown=on_shutdown,
       skip_updates=True,
       host=WEBAPP_HOST,
       port=WEBAPP_PORT,
       )
