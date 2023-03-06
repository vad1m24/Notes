import json
import datetime
import config
import telebot


bot = telebot.TeleBot(token=config.Token)


notes = {}
full_note = {}
keys = []
results = {}
global choice_message
global note_time


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.chat.id, "___  Добро пожаловать в \"Заметки\"  ___\n\n"
                                      "Для выполнения определенных операций введите их команды:\n\n"
                                      "Добавление - /add\n"
                                      "Удаление - /del\n"
                                      "Поиск - /search\n"
                                      "Изменение - /correct\n"
                                      "Вывод всех заметок - /show\n"
                                      "Для вывода меню операций - /help")


@bot.message_handler(commands=['add'])
def adding_message(message):
    bot.send_message(message.chat.id, "Давайте запишем новую заметку.")
    adding_head_note(message)


def adding_head_note(message):
    msg = bot.send_message(message.chat.id, 'Введите заголовок заметки')
    bot.register_next_step_handler(msg, adding_body_note)


def adding_body_note(message):
    global full_note
    full_note['head note'] = str(message.text)
    msg = bot.send_message(message.chat.id, 'Введите тело заметки')
    bot.register_next_step_handler(msg, adding_date_time_note)


def adding_date_time_note(message):
    now = datetime.datetime.now()
    full_note['body note'] = str(message.text)
    full_note['date time'] = str(now.strftime("%d-%m-%Y %H:%M:%S"))
    adding_id_note(message)


def adding_id_note(message):
    try:
        with open('notes.json', 'r') as file:
            data = json.load(file)
    except:
        with open('notes.json', 'w') as db_notes:
            json.dump(notes, db_notes, indent=4)
        with open('notes.json', 'r') as file:
            data = json.load(file)
    for k, v in data.items():
        keys.append(k)
    if int(len(keys) - 1) < 0:
        new_note_key = 1
    else:
        new_note_key = int(keys[-1]) + 1
    data[new_note_key] = full_note
    with open('notes.json', 'w') as file:
        json.dump(data, file, indent=4)
    bot.send_message(message.chat.id, "Новая заметка добавлена.")


@bot.message_handler(commands=['show'])
def showing_notes(message):
    try:
        bot.send_message(message.chat.id, "Заметки:")
        with open('notes.json', 'r') as file:
            data = json.load(file)
        if len(data) < 1:
            bot.send_message(message.chat.id, "Список ваших заметок пока пуст")
            bot.send_message(message.chat.id, "Для проведения новой операции с заметками "
                                              "введите соответствующую команду.")
        else:
            bot.send_message(message.chat.id, json.dumps(data, ensure_ascii=False, indent=4))
        with open('notes.json', 'w') as f:
            json.dump(data, f, indent=4)
    except:
        bot.send_message(message.chat.id, "Список ваших заметок пока пуст")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")


@bot.message_handler(commands=['search'])
def search_notes(message):
    global results
    results = {}
    msg = bot.send_message(message.chat.id, "Введите заголовок, тело или дату вашей заметки для её поиска.")
    bot.register_next_step_handler(msg, search_note_json)


def search_note_json(message):
    global results
    msg = message.text
    searching_elements(msg)
    if results != {}:
        bot.send_message(message.chat.id, json.dumps(results, ensure_ascii=False, indent=4))
    else:
        bot.send_message(message.chat.id, "По данным критериям не удалось найти заметку.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")


def searching_elements(msg):
    try:
        with open('notes.json', 'r') as file:
            data = json.load(file)
            for k, v in data.items():
                for i in range(len(msg)):
                    if v['head note'] == msg:
                        results[k] = v
                    elif v['body note'] == msg:
                        results[k] = v
                    elif v['date time'] == str(msg):
                        results[k] = v
                    elif k == msg:
                        results[k] = v
    except:
        with open('notes.json', 'w') as db_notes:
            json.dump(notes, db_notes, indent=4)


@bot.message_handler(commands=['del'])
def delete_notes(message):
    global results
    results = {}
    msg = bot.send_message(message.chat.id, "Введите заголовок, тело, дату или номер вашей заметки для её удаления.")
    bot.register_next_step_handler(msg, delete_notes_json)


def delete_notes_json(message):
    msg = message.text
    searching_elements(msg)
    if results == {}:
        bot.send_message(message.chat.id, "По данным критериям не удалось найти заметку.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")
    elif len(results) > 1:
        bot.send_message(message.chat.id, json.dumps(results, ensure_ascii=False, indent=4))
        bot.send_message(message.chat.id, "Попробуйте сократить количество критериев поиска в следующий раз.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")
    else:
        bot.send_message(message.chat.id, "Вот ваша заметка.")
        bot.send_message(message.chat.id, json.dumps(results, ensure_ascii=False, indent=4))
        del_notes(msg)
        bot.send_message(message.chat.id, "Заметка удалена.")
        with open('notes.json', 'r') as file:
            data = json.load(file)
        bot.send_message(message.chat.id, json.dumps(data, ensure_ascii=False, indent=4))


def del_notes(msg):
    with open('notes.json', 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if v['head note'] == msg:
                del data[k]
                break
            elif v['body note'] == msg:
                del data[k]
                break
            elif v['date time'] == msg:
                del data[k]
                break
            elif k == msg:
                del data[k]
                break
    with open('notes.json', 'w') as file:
        json.dump(data, file, indent=4)


@bot.message_handler(commands=['correct'])
def correction_mode(message):
    global results
    results = {}
    msg = bot.send_message(message.chat.id, "Введите заголовок, тело или дату вашей заметки для её поиска.")
    bot.register_next_step_handler(msg, search_note_for_correction)


def search_note_for_correction(message):
    global note_time
    global choice_message
    msg = message.text
    searching_elements(msg)
    if results == {}:
        bot.send_message(message.chat.id, "По данным критериям не удалось найти заметку.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметкаами введите соответствующую команду.")
    elif len(results) > 1:
        bot.send_message(message.chat.id, json.dumps(results, ensure_ascii=False, indent=4))
        bot.send_message(message.chat.id, "Попробуйте сократить количество критериев поиска в следующий раз.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")
    else:
        bot.send_message(message.chat.id, "Вот ваша заметка.")
        bot.send_message(message.chat.id, json.dumps(results, ensure_ascii=False, indent=4))
        for k, v in results.items():
            note_time = v['date time']
        choice_message = bot.send_message(message.chat.id, "Что вы хотите в ней изменить?\n"
                                                           "Если заглавие - напишите 1\n"
                                                           "Если тело - напишите 2")
        bot.register_next_step_handler(choice_message, correct_note)


def correct_note(message):
    global choice_message
    choice_message = message.text
    if choice_message == "1" or choice_message == "2":
        msg = bot.send_message(message.chat.id, "Впишите желаемое изменение")
        bot.register_next_step_handler(msg, change_note)
    else:
        bot.send_message(message.chat.id, "Такой операции не существует.")
        bot.send_message(message.chat.id, "Для проведения новой операции с заметками введите соответствующую команду.")


def change_note(message):
    now = datetime.datetime.now()
    msg = message.text
    if choice_message == "1":
        for k, v in results.items():
            if v['date time'] == note_time:
                v['head note'] = msg
                v['date time'] = str(now.strftime("%d-%m-%Y %H:%M:%S"))
                with open('notes.json', 'r') as file:
                    data = json.load(file)
                    data.update(results)
                with open('notes.json', 'w') as file:
                    json.dump(data, file, indent=4)
    if choice_message == "2":
        for k, v in results.items():
            if v['date time'] == note_time:
                v['body note'] = msg
                v['date time'] = str(now.strftime("%d-%m-%Y %H:%M:%S"))
                with open('notes.json', 'r') as file:
                    data = json.load(file)
                    data.update(results)
                with open('notes.json', 'w') as file:
                    json.dump(data, file, indent=4)
    bot.send_message(message.chat.id, json.dumps(data, ensure_ascii=False, indent=4))


bot.polling()
