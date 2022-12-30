# Импорт TELEBOT | https://github.com/eternnoir/pyTelegramBotAPI
import time

import requests
import os
from pprint import pprint
import telebot
# Импортируем types
from telebot import types
# Импорт "секретных данных"
from botdates import *
# Импорт TELEGRAPH
from telegraph import Telegraph
# Импорт баблиотеки для работы в APIGoogle
import gspread
# Импорт библиотеки даты и времени
import datetime

# Токен для связи с ботом
bot = telebot.TeleBot(botkey)

# Командa start
@bot.message_handler(commands = ['start'])
def start(message):
    start_message(message)
# Команды по кнопкам в чате
@bot.message_handler(content_types= ['text'])
def func(message):
    if (message.text == "Все каналы"):
        channelInfo(message)
    elif (message.text == "Сформировать страницы комиксов"):
        createPagesWithComics(message)
    elif (message.text == "Добавить комикс"):
        createNewComix(message)
    elif (message.text == "Опубликовать рандомный комикс"):
        postInChannelRandomComix(message)
    elif (message.text == "Кнопка для GoogleSheets"):
        workWithGoogleSheets(message)
    else:
        senderrormessage(message)

#Функция начала диалога(start)
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Все каналы")
    btn2 = types.KeyboardButton("🤷‍♂️Эх🤷‍♂️")
    btn3 = types.KeyboardButton("Сформировать страницы комиксов")
    btn4 = types.KeyboardButton("Добавить комикс")
    btn5 = types.KeyboardButton("Опубликовать рандомный комикс")
    btn6 = types.KeyboardButton("Кнопка для GoogleSheets")
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот для постинга комиксов".format(
                         message.from_user))
    if (message.chat.id == id):
        markup.add(btn1, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id,
                         text="Введите команду:", reply_markup=markup)
    else:
        markup.add(btn2)
        bot.send_message(message.chat.id, text="У вас нет доступа!", reply_markup=markup)

#Функция отправки ошибки ввода сообещния
def senderrormessage(message):
    text = "Я что-то ничего не понимаю( Кликните по кнопке, пожалуйста"
    bot.send_message(message.chat.id, text)

#Функция отправки всех каналов
def channelInfo(message):
    text = "Отображаю информацию о канале постинга"
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, "ID канала куда постим:\n" + channel_id)
    bot.send_message(message.chat.id, "Название TELEGRAM канала:\n" + channel_name)
    bot.send_message(message.chat.id, "Ссылка на канал:\n" + channel_url)

#Функция создания страниц tepegraph
def createPagesWithComics(message):
    # Создаём аккаунт
    telegraph = Telegraph()
    telegraph.create_account(short_name='Александра Андреевна')
    # Путь до папки с комиксами
    pathcomix = './comix/'
    # Получаем список подпапок
    directory_list = os.listdir(pathcomix)
    print("directory_list: ", directory_list)
    # Запускаем цикл формирования комиксов
    j = 0
    while j < len(directory_list):
        # Формируем путь до каждой папке в массиве
        way_file_list = pathcomix + directory_list[j] + "/"
        print("way_file_list: ", way_file_list)
        # Формируем список фаилов в этой папке
        file_list = os.listdir(way_file_list)
        print("file_list: ", file_list)
        if len(file_list):
            file_list2 = []
            i = 0
            content = ""
            # Пробегаемся по фаилам в папке
            while i < len(file_list):
                endpath = way_file_list + file_list[i]
                with open(endpath, 'rb') as f:
                    path = requests.post(
                        'https://telegra.ph/upload',
                        files={directory_list[j]: (directory_list[j], f, 'image/jpg')}
                        # image/gif, image/jpeg, image/jpg, image/png, video/mp4
                    ).json()[0]['src']
                    # Загружаем их в телеграмм
                    file_list2.append(path)
                    print(path)
                i = i + 1
                # Формируем строку для создания страницы
                content += "<img src='{}'/>".format(path)
            # Создаём страницу с контентом, который подготовили
            response = telegraph.create_page(
                directory_list[j],
                html_content=content
            )
            # Отправляем сообщение об удачной публикации комикса
            textmessage = "Комикс: " + directory_list[j] + "\n" + "Доступен по ссылке: " + response['url']
            bot.send_message(message.chat.id, textmessage)
            print(response['url'])
            now = datetime.datetime.now()
            nowdatetime = now.strftime("%d-%m-%Y %H:%M")
            addedNewDatesInSheet(directory_list[j], nowdatetime, response['url'])
            j = j + 1
        else:
            text = "В папке " + directory_list[j] + " нет фаилов"
            bot.send_message(message.chat.id, text)
            j = j + 1
            continue

    text = "Комиксы успешно загружены."
    bot.send_message(message.chat.id, text)

#Функция рандомного поста в канал
def postInChannelRandomComix(message):
    #Пост будет производиться в канал, который прописан в botdates.py
    #Заходим в таблицу комиксов
    cread_file = "token.json"
    gc = gspread.service_account(cread_file)
    table = gc.open(name_sheet)
    worksheet = table.worksheet("Лист1")
    dates = worksheet.get_all_records()
    #Формируем кнопки с комиксами
    i = 0
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    while i < len(dates):
        btn = types.KeyboardButton(dates[i]['Название комикса'])
        markup.add(btn)
        i = i + 1
    bot.send_message(message.chat.id,
                     text="Выберите комикс который нужно опубликовать:", reply_markup=markup)
    bot.register_next_step_handler(message, postInChannelRandomComix2)
#Функция рандомного поста в канал
def postInChannelRandomComix2(message):
    bot.register_next_step_handler(message, start_message)
    if (message.text == "Ураган Силы #01"):
        bot.send_message(message.chat.id,"Запощено!")

#Функция добавления комикса на комп
def createNewComix(message):
    text = "Что будем делать?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = "Добавить в существующий"
    btn2 = "Создать новый"
    btn3 = "Выйти из добавления"
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text, reply_markup = markup)
    bot.register_next_step_handler(message, createNewComix2)
#Функция добавления комикса на комп2
def createNewComix2(message):
    namefolder = message.text
    path = "/Users/Резервный2/PycharmProjects/comixonlinebot/comix/" + namefolder
    os.mkdir(path)
    nexttext = "Загрузите картинки. По одной и в порядке с начала до конца."
    bot.send_message(message.chat.id, nexttext)
    bot.register_next_step_handler(message, createNewComix3, path)
#Функция добавления комикса на комп3
def createNewComix3(message, folderpath):
    #Получаем информацию о фаиле
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    #Загружаем из TELEGRAM фаил и помещаем его в нужную папку
    downloaded_file = bot.download_file(file_info.file_path)
    #Добавляем фотографию как последнюю
    # Получаем список фаилов в папке
    directory_list = os.listdir(folderpath)
    last_number = len(directory_list) + 1
    path = folderpath + "/" + str(last_number) + ".jpg"
    with open(path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.reply_to(message, "Пожалуй, я сохраню это")

#Функция работы с GoogleSheets
def workWithGoogleSheets(message):
    cread_file = "token.json"
    gc = gspread.service_account(cread_file)
    table = gc.open(name_sheet)
    worksheet = table.worksheet("Лист1")
    tableUrl = "Таблица находится по адресу: " + table.url
    bot.send_message(message.chat.id, tableUrl)
    dates = worksheet.get_all_records()
    print(dates)
    pprint(dates)
# Функция добавления данных в GoogleSheets
def addedNewDatesInSheet(namecomix, dategenerationcomix, url):
    cread_file = "token.json"
    gc = gspread.service_account(cread_file)
    table = gc.open(name_sheet)
    worksheet = table.worksheet("Лист1")
    newstr = len(worksheet.col_values(1))+1
    newnumber = newstr-1
    worksheet.update_cell(newstr,1,newnumber)
    worksheet.update_cell(newstr,2,namecomix)
    worksheet.update_cell(newstr,3,dategenerationcomix)
    worksheet.update_cell(newstr,5,url)

# Функция генерации времени поста
def generationPostDateTime(namecomix):
    cread_file = "token.json"
    gc = gspread.service_account(cread_file)
    table = gc.open(name_sheet)
    worksheet = table.worksheet("Лист1")
    allcomix = worksheet.col_values(2)
    publishdatetime = worksheet.col_values(4)
    pprint(allcomix)
    pprint(publishdatetime)
    print(namecomix)
    nowdatetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    i = 0
    while i < len(allcomix):
        if (allcomix[i] == namecomix):
            print("Такой комикс есть. Дата его последней публикации: " + publishdatetime[i])
            newpublishdatetime = datetime.datetime.now() + datetime.timedelta(days=10)
            print("Новое время публикации комикса: " + newpublishdatetime.strftime("%d-%m-%Y %H:%M"))
            return newpublishdatetime
        else:
            return nowdatetime
        i = i + 1

# Запустил постоянный опрос бота Telegram
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)