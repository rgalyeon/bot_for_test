# -*- coding: utf-8 -*-

from enum import Enum
import telebot


token = '636092085:AAFzl3MqRQP4MAz_43PpxTeq3rX0X7vk8HQ'
db_file = 'database.vdb'

class States(Enum):
    S_START = "0"
    S_TEST = "1"
    S_SWITCH = "2"
    S_DOC = "3"

bot = telebot.TeleBot(token)

# Member's list in game
members_dict = {
    180085543: 'admin',
    225295894: 'player',
    316095229: 'player'
}

# Command's list for checking tasks
exercises_list = [
                    'test1', 'test2',
                    'test3', 'test4',
                    'test5', 'test6',
                    'test7', 'test8',
                    'test9', 'test10'
                ]

ex_dict = {
    'ex1': {
        'enable': False
    },
    'ex2': {
        'enable': False
    },
    'ex3': {
        'enable': False
    },
    'ex4': {
        'enable': False
    },
    'ex5': {
        'enable': False
    },
    'ex6': {
        'enable': False
    },
    'ex7': {
        'enable': False
    },
    'ex8': {
        'enable': False
    },
    'ex9': {
        'enable': False
    },
    'ex10': {
        'enable': False
    }
}

# Answer's list
answers = ['_', '10', '23', '26', '4', '5', '6', '33', '12', '8', '7']