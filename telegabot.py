import os
import telebot
import random
import json
import requests

if not os.path.exists('expenses.json'):
    with open('expenses.json', 'w') as f:
        json.dump({}, f)

bot = telebot.TeleBot('8664840739:AAGMgVYsa6nQKMCi0AQNJH9DGO9rqQioKhk')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_game = telebot.types.KeyboardButton("Играть в числа")
    btn_expense = telebot.types.KeyboardButton("Расходы")
    btn_total = telebot.types.KeyboardButton("Вывести все расходы")
    btn_dollar = telebot.types.KeyboardButton("Курсы валют")
    markup.add(btn_game, btn_expense, btn_total, btn_dollar)
    bot.send_message(message.chat.id, "Привет!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Играть в числа")
def generate_random_number(message):
    bot.send_message(message.chat.id, "Я сгенерировад случайное число от 1 до 100.")
    random_number = random.randint(1, 100)
    bot.register_next_step_handler(message, check_number, random_number)


def check_number(message, random_number):
    if message.text.isdigit():
        user_number = int(message.text)
        if user_number < random_number:
            bot.send_message(message.chat.id, "ваше число больше случайного.")
            bot.register_next_step_handler(message, check_number, random_number)
        elif user_number > random_number:
            bot.send_message(message.chat.id, "ваше число меньше случайного числа.")
            bot.register_next_step_handler(message, check_number, random_number)
        else:
            bot.send_message(message.chat.id, "Поздравляю! Вы угадали число!")
            bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число.")
        bot.register_next_step_handler(message, check_number, random_number)


@bot.message_handler(func=lambda message: message.text == "Расходы")
def add_expense(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add = telebot.types.KeyboardButton("Еда")
    btn_transport = telebot.types.KeyboardButton("Транспорт")
    btn_entertainment = telebot.types.KeyboardButton("Развлечения")
    btn_back = telebot.types.KeyboardButton("Назад")
    markup.add(btn_add, btn_transport, btn_entertainment)
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Выберите категорию расхода:", reply_markup=markup)
    bot.register_next_step_handler(message, get_expense_category)


def get_expense_category(message):
    if message.text == "Назад":
        start(message)
        return
    category = message.text
    bot.send_message(message.chat.id, f"Вы выбрали категорию: {category}. Теперь введите сумму расхода:")
    bot.register_next_step_handler(message, get_expense_amount, category=category)


def get_expense_amount(message, category):
    if message.text.isdigit():
        user_id = str(message.chat.id)
        amount = int(message.text)
        with open('expenses.json', 'r') as f:
            expenses = json.load(f)
        if user_id not in expenses or not isinstance(expenses[user_id], dict):
            expenses[user_id] = {}
        expenses[user_id][category] = expenses[user_id].get(category, 0) + amount
        with open('expenses.json', 'w') as f:
            json.dump(expenses, f)
        bot.send_message(message.chat.id, f"Расход добавлен! Сумма: {amount}")
        bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректную сумму.")
        bot.register_next_step_handler(message, get_expense_amount, category=category)


@bot.message_handler(func=lambda message: message.text == "Вывести все расходы")
def show_expenses(message):
    user_id = str(message.chat.id)
    with open('expenses.json', 'r') as f:
        expenses = json.load(f)
        user_data = expenses.get(user_id, {})
        if not user_data:
            bot.send_message(message.chat.id, "У вас нет расходов.")
            return
        text = "Ваши расходы:\n"
        total = 0
        for category, amount in user_data.items():
            text += f"Категория: {category}, Сумма: {amount}\n"
            total += amount
        text = f"{text}\nОбщая сумма: {total}"
        bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "Курсы валют")
def cnopca(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_eu = telebot.types.KeyboardButton("Курс евро")
    btn_rub = telebot.types.KeyboardButton("Курс доллара")
    btn_back = telebot.types.KeyboardButton("Назад")
    markup.add(btn_eu, btn_rub)
    markup.add(btn_back)
    bot.send_message(message.chat.id, "Выберите валюту:", reply_markup=markup)
    bot.register_next_step_handler(message, get_currency_rate)
    

def get_currency_rate(message):
    if message.text == "Назад":
        start(message)
        return
    elif message.text == "Курс евро":
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
            data = response.json()
            rate = data["rates"]["RUB"]
            bot.send_message(message.chat.id, f"Курс евро к рублю: {rate}")
            bot.register_next_step_handler(message, get_currency_rate)
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка при получении курса евро.")
    elif message.text == "Курс доллара":
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            rate = data["rates"]["RUB"]
            bot.send_message(message.chat.id, f"Курс доллара к рублю: {rate}")
            bot.register_next_step_handler(message, get_currency_rate)
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка при получении курса доллара.")  
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите корректную валюту.")
        bot.register_next_step_handler(message, get_currency_rate)


bot.infinity_polling()
