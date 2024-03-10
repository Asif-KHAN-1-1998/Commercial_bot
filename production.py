import requests
import os
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
from threading import Thread
import datetime
import time
from telegram import Bot
from dotenv import load_dotenv
load_dotenv()



updater = Updater(token=os.getenv('BOT_TOKEN'))
api_token = os.getenv('API_TOKEN')
version = os.getenv('VERSION')
id_cab = os.getenv('CABINET_ID')
money = int(os.getenv('MONEY'))
chat_id = os.getenv('CHAT_ID')
get_id=[]
pars_limit=[]
pars_spent = []
result_tab = []

def GetId():
    get_id.clear()
    print("""Получаем ID""")
    method = 'ads.getClients'
    url = f'https://api.vk.com/method/{method}'
    responce = requests.get(url, params={
        'access_token': api_token,
        'v': version,
        'account_id': id_cab
    })
    red = responce.json()
    time.sleep(1)
    for all_id in red['response']:
        get_id.append(str(all_id['id']))
    return get_id

def ParsLimit():
    pars_limit.clear()
    print("""Парсим данные с API""")
    method = 'ads.getClients'
    url = f'https://api.vk.com/method/{method}'
    r = requests.get(url, params={
        'access_token': api_token,
        'v': version,
        'account_id': id_cab
    })
    res = r.json()
    time.sleep(1)
    for all_id in res['response']:
        pars_limit.append((all_id['id'],
                           all_id['name'],
                           int(all_id['all_limit'])
                           ))
    return pars_limit

def ParsSpent(num):
    pars_spent.clear()
    print(""" Парсим затраты с API """)
    scr = ', '.join(num)
    method = 'ads.getStatistics'
    client = 'client'
    period = 'overall'
    date_from = '0'
    date_to = '0'
    url = f'https://api.vk.com/method/{method}'
    r = requests.get(url, params={
        'access_token': api_token,
        'v': version,
        'account_id': id_cab,
        'ids_type': client,
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'ids': scr
    })
    my_dict = r.json()['response']
    for elem in my_dict:
        if elem['stats']:
            pars_spent.append((elem['id'],
                               float(elem['stats'][0]['spent'])))
        elif not elem['stats']:
            pars_spent.append((elem['id'],
                               int(0)))
    return pars_spent
    
def Result(tup, tup2):
    result_tab.clear()    
    print("""Сравниваем значения и готовим сообщения""")
    for id, name, limit in tup:
        for id2, spent in tup2:
            if id == id2:
                balance = limit - spent
                if balance < money:
                    mon = "{:.2f}".format(limit - spent)
                    if float(spent) > 0:
                        result_tab.append(f'В {name} осталось {mon} рублей!')
    return result_tab

def say_result(update, context):
    print('Выводим данные')
    chat = update.effective_chat
    aidi = GetId()
    context.bot.send_message(chat_id=chat.id,
                             text=f'Получил ID')
    spent = ParsSpent(aidi)
    context.bot.send_message(chat_id=chat.id,
                             text=f'Расходы')
    limit = ParsLimit()
    context.bot.send_message(chat_id=chat.id,
                             text=f'Лимиты')
    final = Result(limit, spent)
    context.bot.send_message(chat_id=chat.id,
                             text=f'Считаем')
    time.sleep(1)
    result = '\n'.join((final))
    context.bot.send_message(chat_id=chat.id,
                             text=f'{result}')

def morning_message(bot):
    now = datetime.datetime.now()
    hour = now.hour
    print('hour:', hour)
    while True:
        if hour in [0]:
            say_result_morning(bot, chat_id)
        time.sleep(3600)

def say_result_morning(bot, chat_id):
    print('Выводим данные')
    aidi = GetId()
    spent = ParsSpent(aidi)
    limit = ParsLimit()
    final = Result(limit, spent)
    result = '\n'.join((final))
    bot.send_message(chat_id=chat_id, text=f'{result}')

bot = Bot(token=os.getenv('BOT_TOKEN'))
Thread(target=morning_message, args=(bot,)).start()

def say_asif(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text='Асиф! https://t.me/Asif_KHAS')


def say_hi(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text='Привет, я Money_Bot!')

def wake_up(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['Че там по городам?', 'Кто это наклепал?']
                                  ], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id, 
                             text='Привет, я Money_Bot! Спасибо, что включили меня',
                             reply_markup=button)
    

updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Кто это наклепал?'), say_asif))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Че там по городам?'), say_result))
updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
updater.start_polling()
updater.idle()