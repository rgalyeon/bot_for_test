# -*- coding: utf-8 -*-

from vedis import Vedis
from config import *
import dbworker
import telebot
from enum import Enum


"""
Этот хэндлер работает с участниками по команде /start.
Если это новый игрок, то бот его приветствует и направляет далее.
Если это старый игрок, то бот проверяет его состояние и направляет далее.
Отлично работает при краше сервера, т.к. состояния сохраняются
"""
@bot.message_handler(commands=["start"])
def cmd_start(message):
    # Проверяем состояние игрока
    state = dbworker.get_state(message.chat.id)
    if state == States.S_TEST.value:
        bot.send_message(message.chat.id, "Кажется, ты хотел выбрать тест. Пиши /test[номер задания] "
                                          "и следуй дальнейшим инструкциям")
    elif state == States.S_SWITCH.value:
        bot.send_message(message.chat.id, "Кажется, ты забыл включить/выключить проверку задания")
    elif state == States.S_DOC.value:
        bot.send_message(message.chat.id, "Кажется, кто-то хотел отправить txt файл с заданием, "
                                          "но так и не сделал этого :( Жду...")
    elif state == States.S_START.value:
        bot.send_message(message.chat.id, "Ты можешь выбрать следующее задание с помощью команды"
                                          "/test[номер задания]")
        dbworker.update_state(message.chat.id, States.S_TEST.value)
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Привет! Выбирай задание с помощью команды "
                                          "/test[номер задания]")
        dbworker.remove_id(message.chat.id)
        dbworker.add_states(message.chat.id, States.S_TEST.value)

"""
Этот хэндлер работает с командами /test[n].
Админов он перенаправляет на On/Off теста
Игроков на отправку документа
"""
@bot.message_handler(commands=exercises_list,
                     func=lambda message: dbworker.get_state(message.chat.id) == States.S_TEST.value)
def cmd_start(message):
    global index
    # Считывание номера задания
    index = ''.join(map(str, message.text.split('/test')))
    if members_dict[message.chat.id] == "admin":
        bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
        dbworker.update_state(message.chat.id, States.S_SWITCH.value)
    elif members_dict[message.chat.id] == "player":
        if ex_dict['ex' + index]['enable'] is True:
            bot.send_message(message.chat.id, "Жду от тебя задание №{} в формате txt".format(index))
            dbworker.update_state(message.chat.id, States.S_DOC.value)
        elif ex_dict['ex' + index]['enable'] is False:
            bot.send_message(message.chat.id, "Проверка задания №{} пока закрыта".format(index))
            return
    else:
        bot.send_message(message.chat.id, " Ты не зарегистрирован в игре ")


"""
Данных хэндлер работает только для админов
С помощью текстового сообщения админ выбирает On или Off задания
После выбора состояние админа возвращается на /test
"""
@bot.message_handler(func=lambda message: dbworker.get_state(message.chat.id) == States.S_SWITCH.value)
def admin_set_pass(message):
    if members_dict[message.chat.id] == "admin":
        if message.text.lower() == "On".lower():
            ex_dict['ex' + index]['enable'] = True
            bot.send_message(message.chat.id, "Отлично, проверка задания {} включена".format(index))
            dbworker.update_state(message.chat.id, States.S_TEST.value)
        elif message.text.lower() == 'Off'.lower():
            ex_dict['ex' + index]['enable'] = False
            bot.send_message(message.chat.id, "Проверка задания {} выключена".format(index))
            dbworker.update_state(message.chat.id, States.S_TEST.value)
        else:
            bot.send_message(message.chat.id, "Что-то не так, попробуй еще раз")
            bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
            return 

"""
Данных хэндлер работает только для игроков
Хэндлер ожидает от игрока txt файл с ответом
Если задание решено верно, то состояние игрока меняется на /test
Если неверно, то игроку предлагается еще раз отправить файл
"""
@bot.message_handler(content_types=["document"],
                     func=lambda message: dbworker.get_state(message.chat.id) == States.S_DOC.value)
def check_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_text = downloaded_file.decode().rstrip()
    except UnicodeDecodeError:
        bot.send_message(message.chat.id, " Это не txt файл ")
        return

    if file_text == answers[index]:
        bot.send_message(message.chat.id, " Задание №{} решено верно".format(index))
        bot.send_message(message.chat.id, " Для отправки остальных заданий напиши команду /test[номер задания]")
        dbworker.update_state(message.chat.id, States.S_TEST.value)
    else:
        bot.send_message(message.chat.id, " Задание №{} решено неверно, попробуй еще раз".format(index))
        #bot.send_message(message.chat.id, " Если хочешь решить другое задание отправь /test[номер задания]")
        return

"""
Дополнительная команда для возвращения к состонию /test
если вдруг что не так
"""
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Для отправки заданий используй команду"
                                      "/test[номер задания]")
    dbworker.update_state(message.chat.id, States.S_TEST.value)



if __name__ == "__main__":
    bot.polling(none_stop=True)
