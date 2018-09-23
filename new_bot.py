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

@bot.message_handler(commands=["start"])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_START.value:
        bot.send_message(message.chat.id, "Кажется, ты хотел выбрать тест. Пиши /test[номер задания] "
                                          "и следуй дальнейшим инструкциям")
    elif state == config.States.S_ENTER.value:
        bot.send_message(message.chat.id, "Кажется, ты забыл включить/выключить проверку задания")
    elif state == config.States.S_DOC.value:
        bot.send_message(message.chat.id, "Кажется, кто-то хотел отправить txt файл с заданием, "
                                          "но так и не сделал этого :( Жду...")
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Привет! Выбирай задание с помощью команды "
                                          "/test[номер задания]")
        dbworker.set_state(message.chat.id, config.States.S_TEST.value)

@bot.message_handler(commands=exercises_list,
                     func=lambda message: dbworker.get_current_state(message.chat.id) == States.S_TEST.value)
def cmd_start(message):
    global index
    index = ''.join(map(str, message.text.split('/test')))
    if members_dict[message.chat.id] == "admin":
        bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
        dbworker.set_state(message.chat.id, States.S_SWITCH.value)
    elif members_dict[message.chat.id] == "player":
        if ex_dict['ex' + index]['enable'] is True:
            bot.send_message(message.chat.id, "Жду от тебя задание №{} в формате txt".format(index))
            dbworker.set_state(message.chat.id, States.S_DOC.value)
        elif ex_dict['ex' + index]['enable'] is False:
            bot.send_message(message.chat.id, "Проверка задания №{} пока закрыта".format(index))
            return
    else:
        bot.send_message(message.chat.id, " Ты не зарегистрирован в игре ")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == States.S_SWITCH.value)
def admin_set_pass(message):
    if members_dict[message.chat.id] == "admin":
        if message.text.lower() == "On".lower():
            ex_dict['ex' + index]['enable'] = True
            bot.send_message(message.chat.id, "Отлично, проверка задания {} включена".format(index))
            dbworker.set_state(message.chat.id, States.S_START.value)
        elif message.text.lower() == 'Off'.lower():
            ex_dict['ex' + index]['enable'] = False
            bot.send_message(message.chat.id, "Проверка задания {} выключена".format(index))
            dbworker.set_state(message.chat.id, States.S_START.value)
        else:
            bot.send_message(message.chat.id, "Что-то не так, попробуй еще раз")
            bot.send_message(message.chat.id, " Тест {} \n"
                                                 "On - включить проверку \n"
                                                 "Off - выключить проверку ".format(index))
            return 


@bot.message_handler(content_types=["document"],
                     func=lambda message: dbworker.get_current_state(message.chat.id) == States.S_DOC.value)
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
        dbworker.set_state(message.chat.id, States.S_TEST.value)
    else:
        bot.send_message(message.chat.id, " Задание №{} решено неверно, попробуй еще раз".format(index))
        bot.send_message(message.chat.id, " Если хочешь решить другое задание отправь /test[номер задания]")
        return

@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Для отправки заданий используй команду"
                                      "/test[номер задания]")
    dbworker.set_state(message.chat.id, States.S_TEST.value)

if __name__ == "__main__":
    bot.polling(none_stop=True)
