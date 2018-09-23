from vedis import Vedis
from config import *
import dbworker
import telebot

# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with Vedis(db_file) as db:
        try:
            return db[user_id]
        except KeyError:  # Если такого ключа почему-то не оказалось
            return States.S_START.value  # значение по умолчанию - начало диалога

# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    with Vedis(db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            # тут желательно как-то обработать ситуацию
            return False

@bot.message_handler(commands=exercises_list)
def cmd_start(message):
    global index
    index = ''.join(map(str, message.text.split('/test')))
    if members_dict[message.chat.id] == "admin":
        bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
        dbworker.set_state(message.chat.id, States.S_ENTER.value)
    elif members_dict[message.chat.id] == "player":
        if ex_dict['ex' + index]['enable'] is True:
            bot.send_message(message.chat.id, "Жду от тебя задание №{} в формате txt".format(index))
            dbworker.set_state(message.chat.id, States.S_DOC)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == States.S_ENTER.value)
def user_entering_name(message):
    if members_dict[message.chat.id] == "admin":
        if message.text.lower() == "On".lower():
            ex_dict['ex' + index]['enable'] = True
            bot.send_message(message.chat.id, "Отлично, проверка задания {} включена".format(index))
            dbworker.set_state(message.chat.id, config.States.S_START.value)
        elif message.text.lower() == 'Off'.lower():
            ex_dict['ex' + index]['enable'] = False
            bot.send_message(message.chat.id, "Проверка задания {} выключена".format(index))
            dbworker.set_state(message.chat.id, config.States.S_START.value)
        else:
            bot.send_message(message.chat.id, "Что-то не так, попробуй еще раз")
            bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
            return 

