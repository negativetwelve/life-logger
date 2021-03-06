import sqlite3
from copy import deepcopy
from datetime import datetime

KEY = "Key"
SCREEN = "Screen"
MOUSE = "Mouse"
TIME = 'time'

EMPTY_INDEX = '<no index>'
EMPTY_KEY_CODE = '<no code>'
EMPTY_DURATION = '<no duration>'
EMPTY_DATETIME = '<no datetime>'
EMPTY_CHAR = '<no char>'
EMPTY_TIME = '<no time>'
EMPTY_DATE = '<no date>'
EMPTY_MOD = '<no mod>'
EMPTY_POSITION = '<no position>'
EMPTY_NAME = '<no name>'
EMPTY_WINDOW = '<no window>'
empty_things = [EMPTY_INDEX, EMPTY_KEY_CODE, EMPTY_CHAR,
    EMPTY_TIME, EMPTY_DATE, EMPTY_MOD, EMPTY_POSITION,
    EMPTY_NAME, EMPTY_WINDOW]

reset_codes = {36: "\n", 48: "<TAB>", 51: "<BACK>"}
separating_codes = {36: "\n", 48: "<TAB>", 49: " "}


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Position({0}, {1})".format(self.x, self.y)


class Event:
    def __init__(self, time=EMPTY_TIME, date=EMPTY_DATE,
                    index=EMPTY_INDEX, window=EMPTY_WINDOW):
        self.time = time
        self.date = date
        self.datetime = EMPTY_DATETIME
        self.index = index
        self.window = window
        self.key = self.date

    def set_datetime(self):
        if self.time != EMPTY_TIME and self.date != EMPTY_DATE:
            time = []
            date = []
            time = self.time.split(":")
            date = self.date.split("-")
            time = [int(x) for x in time]
            date = [int(x) for x in date]
            self.datetime = datetime(*(date + time))

    def set_key(self, thing=None):
        if (not thing) and (thing not in empty_things):
            self.key = thing
        elif self.date not in empty_things:
            self.key = self.date

    def __repr__(self):
        return "Event({0}, {1})".format(self.date, self.time)

    def set_info(self, str, window=EMPTY_WINDOW):
        self.window = window
        words = str.split()

        # set date and time
        self.date = words[0]
        self.time = words[1]
        self.set_datetime()


class Screen(Event):
    def __init__(self, time=EMPTY_TIME, date=EMPTY_DATE, index=EMPTY_INDEX,
                    window=EMPTY_WINDOW, name=EMPTY_NAME,
                    duration=EMPTY_DURATION):
        Event.__init__(self, time, date, index)
        self.name = name
        self.window = window
        self.duration = duration

    def set_info(self, str):
        Event.set_info(self, str)

        words = str.split()
        for word in words:
            elements = word.split("=")
            if not len(elements) >= 2:
                continue
            field = elements[0]
            item = elements[1]
            if field == 'name':
                if item != '_':
                    self.name = item.replace("_", " ")
            elif field == "owner":
                self.window = item.replace("_", " ")

        self.set_key()

    def set_key(self):
        if self.window not in empty_things:
            self.key = self.window

    def __repr__(self):
        return "Screen({0}, {1})".format(self.window, self.name)


class Mouse(Event):
    def __init__(self, time=EMPTY_TIME, date=EMPTY_DATE, index=EMPTY_INDEX,
                        position=EMPTY_POSITION, window=EMPTY_WINDOW):
        Event.__init__(self, time, date, index, window)
        self.position = position

    def set_info(self, str, window):
        Event.set_info(self, str, window)
        words = str.split()

        x = None
        y = None

        for word in words:
            elements = word.split("=")
            if not len(elements) >= 2:
                continue
            field = elements[0]
            item = elements[1]
            if field == "x":
                x = float(item)
            elif field == "y":
                y = float(item)
        self.position = Position(x, y)
        self.set_key()

    def set_key(self):
        if self.position not in empty_things:
            self.key = self.position

    def __repr__(self):
        return "Mouse({0})".format(self.position)


class Key(Event):

    def __init__(self, time=EMPTY_TIME, date=EMPTY_DATE, index=EMPTY_INDEX,
                    window=EMPTY_WINDOW, char=EMPTY_CHAR,
                    code=EMPTY_KEY_CODE, mod=EMPTY_MOD):
        Event.__init__(self, time, date, index, window)
        self.char = char
        self.code = code
        self.mod = mod

    def set_info(self, str, window):
        Event.set_info(self, str, window)
        str = str.replace('" "', "~~~~~")
        words = str.split()
        for i, word in enumerate(words):
            word = word.replace("~~~~~", '" "')

            # set char, key, mods
            word = word.replace('"="', "^^^^^")
            elements = word.split("=")
            if len(elements) < 2:
                continue
            field = elements[0]
            info = elements[1]
            info = info.replace("^^^^^", '"="')
            if field == "char":
                info = info.replace('"', '')
                self.char = info
            elif field == "key":
                self.code = int(info)
            elif field == "mods":
                info = info.replace("[", " ")
                info = info.replace("]", " ")
                info = info.replace("'", " ")
                info = info.replace("'", " ")
                info = info.strip()
                if info != "":
                    self.mod = info
        self.reset()

    def set_key(self):
        if self.char not in empty_things:
            self.key = self.char

    def reset(self):
        """Resets the char attribute if it is a whitespace
        character to something more readily printed and resets
        char if there is a mod"""
        if self.code in reset_codes:
            self.char = reset_codes[self.code]
        if self.mod != EMPTY_MOD:
            self.char = "<{0}-{1}>".format(self.mod, self.char)
        self.set_key()

    def __repr__(self):
        #return "CharTime(char={0}, code={1}, date={2},
        # time={3})".format(self.char, self.code, self.date, self.time)
        return "Key({0})".format(self.char)

    def __str__(self):
        return self.char


class Word(Key):
    def __init__(self, other=None):
        if other:
            Key.__init__(self, other.time, other.date, other.index,
                    other.window, other.char, other.code, other.mod)
        else:
            Key.__init__(self)

    def reset_char(self, new_char):
        self.char = new_char

    def __repr__(self):
        return "Word({0})".format(self.char)


def make_keycode_dict():
    assert False, "I'm making this error because it shouldn't work right now"
    keycodes = {}
    f = open('./raw_data/one_of_key.txt', 'r')
    content = f.read()

    chars, dict = make_charlist_dict(content)
    for key, value in dict.items():
        keycodes[key] = value.code
    return keycodes


def make_charlist_dict(content):
    def add_to_dicts(dict, obj, time_dict):
        if obj.key not in dict:
            dict[obj.key] = []
        dict[obj.key].append(obj)
        if obj.time not in time_dict:
            time_dict[obj.time] = []
        time_dict[obj.time].append(obj)
    chars = []
    master_dict = {KEY: {}, SCREEN: {}, MOUSE: {}, TIME: {}}
    current_screen = Screen()
    lines = content.split('\n')
    for line in lines:
        words = line.split()
        if len(words) < 3:
            continue
        event_type = words[2]
        obj = Event()
        if event_type == KEY:
            obj = Key()
            obj.set_info(line, current_screen)
            add_to_dicts(master_dict[KEY], obj, master_dict[TIME])
            chars.append(obj)
        elif event_type == SCREEN:
            obj = Screen()
            obj.set_info(line)
            add_to_dicts(master_dict[SCREEN], obj, master_dict[TIME])
            if current_screen.datetime != EMPTY_DATETIME:
                current_screen.duration = int((obj.datetime -
                            current_screen.datetime).total_seconds())
            current_screen = obj
        elif event_type == MOUSE:
            obj = Mouse()
            obj.set_info(line, current_screen)
            add_to_dicts(master_dict[MOUSE], obj, master_dict[TIME])
    return chars, master_dict


def make_basic_dictionary(chars_list):
    """ Should return a dictionary of space/tab/enter
        separated words, where the key is the entire
        built up word and the value is a Word object.

        Note that this dictionary has mispelled words,
        which include <BACK> chars, and normal words,
        where the user never hit backspace. """
    basic, built = {}, []
    for char in chars_list:
        if char.code not in separating_codes:
            built.append(char)
        elif char.code in separating_codes:
            if len(built) == 0:
                continue
            last_char = built[-1]
            last_word = "".join([x.char for x in built]).strip()
            word = Word(last_char)
            word.reset_char(last_word)
            # basic[last_word] = word
            basic.setdefault(last_word, []).append(word)  # Maybe...
            built = []
        else:
            print 'poop'
    return basic

def make_all_dictionaries(basic_dictionary):
    """ Should take in a basic dictionary from the
        previous method and convert it into:
            1) "By words", a dictionary from corrected
                words to a list of Word objects
            2) "By times", a dictionary from times
                to a list of word objects
            3) "Mispelled", a dictionary from mispelled
                words to a list of Word objects.
                Mispelled words include <BACK> chars
    """
    # print basic_dictionary
    by_words, by_times, mispelled = dict(), dict(), dict()
    count = 0
    for word_wat, word_list in basic_dictionary.items():
        index = word_wat.find(reset_codes[51])  # Backspace
        if index >= 0:
            mispelled[word_wat] = deepcopy(word_list)
        #if count in [4,5,6]:
            #print word_wat
        while index >= 0:
            if index == 0:
                while index == 0:
                    word_wat = word_wat[len(reset_codes[51]):]
                    index = word_wat.find(reset_codes[51])
            else: 
                word_wat = word_wat[:index-1] + word_wat[index+len(reset_codes[51]):]  # TODO
                # print string
                index = word_wat.find(reset_codes[51])
        for word in word_list:
            word.reset_char(word_wat)
            by_times.setdefault(word.time, []).append(word)
        by_words[word_wat] = deepcopy(word_list)
        #count += 1
    return by_words, by_times, mispelled


def make_timeword_dictionaries_old(chars_list):
    def add_to_dictionaries(word):
        if word.key not in word_dict['by words']:
            word_dict['by words'][word] = []
        word_dict['by words'][word].append(word)
        if word.time not in word_dict['by times']:
            word_dict['by times'][word.time] = []
        word_dict['by times'][word.time].append(word)
    output = []
    word_dict = {'by words': {}, 'by times': {}}
    current_word = []
    length = len(chars_list)
    for i, char in enumerate(chars_list):
        if char.code in reset_codes:
            if len(output) > 0 and char.code == 51:  # backspace
                output.pop(len(output) - 1)
            else:
                output.append(char.char)
            current_char = Word(char)
            add_to_dictionaries(current_char)

            if len(current_word) > 0:
                word = Word(current_word[len(current_word) - 1])
                word.reset_char("".join([x.char for x in
                                    current_word]).strip())
                add_to_dictionaries(word)
                current_word = []
        else:
            if char.code == 49 or i == length - 1:  # space
                current_word.append(char)
                word = Word(char)
                word.reset_char("".join([x.char for x
                                    in current_word]).strip())
                add_to_dictionaries(word)
                current_word = []
            else:
                current_word.append(char)
            output.append(char.char)
    output_str = "".join(output)
    # print(time_dict)
    return output_str, word_dict


def parse():
    f = open('./raw_data/output.txt', 'r')
    content = f.read()

    #keycodes = make_keycode_dict()
    #print(keycodes)

    chars, master_dict = make_charlist_dict(content)
    basic = make_basic_dictionary(chars)
    by_words, by_times, mispelled = make_all_dictionaries(basic)
    return by_words, by_words, mispelled, master_dict


if __name__ == '__main__':
    random_datetime = '2012-01-01'
    conn = sqlite3.connect('../db/development.sqlite3')
    c = conn.cursor()
    start_index = 0
    try:
        c.execute('''CREATE TABLE events (start_index real, word text,
                date text, time text, datetime1 text, datetime2 text,
                event_type text, window text, duration text)''')
    except Exception:
        c.execute('SELECT * FROM events')
        start_index = len(c.fetchall())

    # output_str, master_dict, word_dicts = parse()
    by_words, by_time, mispelled, master_dict = parse()
    insertion = []
    for event, values in master_dict.items():
        for key, lists in values.items():
            for item in lists:
                duration = 0
                if event == KEY:
                    word = item.char
                elif event == SCREEN:
                    word = item.window
                    duration = item.duration
                elif event == MOUSE:
                    word = str(item.position.x) + ',' + str(item.position.y)
                elif event == TIME:
                    word = key
                else:
                    print 'poop'
                    word, window = 'poop', 'poop'
                window = item.window

                # Needed for everything but Screen events
                if not isinstance(window, str):
                    window = window.window

                # For the event that the user is still typing in the terminal
                # and hasn't created a Screen event
                if window.find('<no window>') >= 0:
                    window = window.replace('<no window>', 'possibly terminal')

                insertion.append((start_index, str(word), item.date, item.time,
                    random_datetime, random_datetime, event, window, str(duration)))
                start_index += 1
    #duration = 0
    #for event, values in by_words.items():
        #if event == 'by_times':
            #continue
        #for key, words in values.items():
            #for word in words:
                #window = word.window
                #if not isinstance(window, str):
                    #window = window.window
                #insertion.append((start_index, str(word), word.date, word.time,
                        #random_datetime, random_datetime, "WORD", window, str(duration)))
                #start_index += 1

    for correct, words in by_words.items():
        for word in words:
            window = word.window
            if not isinstance(window, str):
                window = window.window
            insertion.append((start_index, correct, word.date, word.time,
                    random_datetime, random_datetime, "WORD", window, str(0)))
            start_index += 1

    for mispelled, words in mispelled.items():
        for word in words:
            window = word.window
            if not isinstance(window, str):
                window = window.window
            insertion.append((start_index, mispelled, word.date, word.time,
                        random_datetime, random_datetime, "Miss", window, str(0)))
            start_index += 1

    c.executemany('INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', insertion)
    conn.commit()
    conn.close()
