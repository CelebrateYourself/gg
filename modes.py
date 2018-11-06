
import abc
import os
import random
import re

from setting import Setting

modes = []


def mode(mode_class):
    modes.append(mode_class)



class Mode(abc.ABC):

    info = 'Abstract mode text'

    def __init__(self, *, window, resource_name, on_exit, settings=None):
        if settings:
            self.settings = settings

        self._window = window
        self._on_exit = on_exit
        self._parse_resource(resource_name)

    
    @property
    def display(self):
        return self._window.display

    @display.setter
    def display(self, text):
        self._window.display = text

    @classmethod
    def get_name(cls):
        return cls.name if hasattr(cls, 'name') else cls.__name__

    @classmethod
    def get_resources_names(cls):
        if hasattr(cls, 'path'):
            resources_path = cls.path
        else:
            current_file = os.path.abspath(__file__)
            resources_path = os.path.join(
                os.path.dirname(current_file), 
                'resources',
                cls.get_name().lower()
            )
            cls.path = resources_path

        files = [
            file for file in os.listdir(resources_path) 
                if os.path.isfile(os.path.join(resources_path, file))
        ]
        return files

    @abc.abstractmethod
    def on_answer(self, answer_text):
        """ """

    @abc.abstractmethod
    def launch(self):
        """ """
        
    @abc.abstractmethod
    def _parse_resource(self, resource_name):
        """ """


@mode
class DictMode(Mode):

    # a sound card, audio card | комментарий = 
    #     звуковая карта | комментарий
    #
    # Количество вариантов вопроса и ответа могут не совпадать.
    # Вопрос выбирается произвольно, ответ сравнивается со всеми
    # доступными.
    _RESOURCE_PATTERN = 'q1, ... qn | comment = a1, ... am | comment'

    name = 'Словари'
    info = 'Напишите перевод слова:'
    settings = {
        'count': Setting(
                    type='range',
                    default=5,
                    widget='range',
                    from_=1,
                    to=100,
                    label='Количество слов',
                 ),
        'reverse': Setting(
                       type='bool',
                       default=False,
                       widget='bool',
                   ),
    }

    def on_answer(self, answer_text):
        current_question = self.question
        true_answer = self.qa_dict[current_question]
        if answer_text not in true_answer:
            self.bad_answers[current_question] = answer_text
        try:
            self.question = next(self.questions_i)
        except StopIteration:
            bad_answers = ''
            for q,a in self.bad_answers.items():
                # ', '.join(...) because key:value - tuples
                bad_answers += '{} - {} >> {}\n'.format(
                    ', '.join(q), 
                    a, 
                    ', '.join(self.qa_dict[q])
                )
            result_text = 'Результаты:\n{} из {}\n\n{}'.format(
                self.length - len(self.bad_answers),
                self.length,
                bad_answers
            )
            self._on_exit(result_text)
        else:
            self.display = self.pattern.format(
                self.info,
                # если формулировок вопроса несколько "монитор, дисплей"
                random.choice(self.question)
            )

    def launch(self):
        # При парсинге мы сохранили весь файл, здесь же
        # выбирается некоторое количество произвольных
        # позиций для тестирования. В дальнейшем, можно
        # сохранять только выбранные пары.
        count = self.settings['count']
        questions = random.sample(self.qa_dict.keys(), count)
        random.shuffle(questions)
    
        self.questions_i = iter(questions)
        self.pattern = '{}\n\n>> {}'
        self.length = count
        self.bad_answers = {}
 
        try:
            self.question = next(self.questions_i)
        except StopIteration:
            self._on_exit('Нет доступных вопросов!')
        else:
            self.display = self.pattern.format(
                self.info,
                # если формулировок вопроса несколько "монитор, дисплей"
                random.choice(self.question)
            )

    def _parse_resource(self, resource_name):
        file_path = os.path.join(self.path, resource_name)
        qa_dict = {}
        reverse = self.settings['reverse']
        with open(file_path, 'rt', encoding='utf8') as file:
            for string in file:
                try:
                    question, answer = string.replace('\n', '').split('=')
                except Exception as e:
                    continue
                # remove additional info (comments)
                question = question.split('|')[0]
                answer = answer.split('|')[0]
                # create a tuple of variables from string 
                # like "alfa, beta, gamma"
                # tuple is a hashable sequence, we use it for dict key
                q_tuple = tuple(
                    map(str.strip, question.split(','))
                )
                a_tuple = tuple(
                    map(str.strip, answer.split(','))
                )
                
                if q_tuple and a_tuple:
                    # simple dummy realisation
                    if reverse:
                        qa_dict[a_tuple] = q_tuple
                    else:
                        qa_dict[q_tuple] = a_tuple

        self.qa_dict = qa_dict


@mode
class TestMode(Mode):
    """Test mode. Required data format:
    question = correct_answer_1(ca1) | ca2 | ... ca3 ?
    (optional) incorrect_answer_1(ia1) | ia2 | ... ia3
    If no incorrect answers they are randomly selected from correct answers
    to others questions
    """

    INCORRECT_ANSWERS_MIN = 2  # Minimum and ...
    INCORRECT_ANSWERS_MAX = 5  # Maximum number of randomly selected incorrect answers (if need)
    name = 'Тесты'
    info = 'Выбирайте правильные ответы на вопросы из предложенного списка' \
           '(необходимо вводить числа, соответсвующие правильным ответам,' \
           'через пробел)'

    settings = {
        'count': Setting(
            type='range',
            default=5,
            widget='range',
            from_=4,
            to=6,
            label='Количество вопросов',
        )
    }

    def on_answer(self, answer_text):
        ans = []
        answer_text = answer_text.strip()
        err = False

        try:
            if len(answer_text) == 0:
                raise ValueError()
            for ind in re.split('\s+', answer_text):
                ind = int(ind.strip())
                if ind < 1 or ind > len(self._cur_q_list):
                    raise ValueError()
                ans.append(self._cur_q_list[ind - 1])
        except ValueError:
            err = True
        else:
            self._answers.append(ans)
            self._counter += 1
            if self._counter == len(self._questions):
                self._display_result()
                return
            self._cur_q_list = self._prepare_question()

        self._display_question()
        if err:
            self.display += '\nНекорректный индекс ответа'

    def launch(self):
        count = self.settings['count']
        self._questions = random.sample(self._qa_list, count)
        random.shuffle(self._questions)
        self._counter = 0
        self._answers = []
        self._cur_q_list = self._prepare_question()
        self._display_question()

    def _parse_resource(self, resource_name):
        file_path = os.path.join(self.path, resource_name)
        qa_list = []  # [question, [correct answers], [incorrect answers]]
        with open(file_path, 'rt', encoding='utf8') as file:
            for string in file:
                try:
                    question, answers = string.strip().split('=')
                    answers = answers.split('?')
                    cas = [ans.strip() for ans in answers[0].split('|')]
                    ias = []
                    if len(answers) > 1:
                        ias = [ans.strip() for ans in answers[1].split('|')]
                    qa_list.append([question.strip(), cas, ias])
                except IOError:
                    continue
        for q in qa_list:  # If no incorrect answers
            if not len(q[2]):
                i = 0
                limit = random.randint(__class__.INCORRECT_ANSWERS_MIN,
                                       __class__.INCORRECT_ANSWERS_MAX)
                while i < limit:
                    rand_q = random.choice(qa_list)
                    if rand_q[0] == q[0]:
                        continue  # not very good
                    rand_ans = random.choice(rand_q[1])
                    if rand_ans in q[1]:
                        continue  # not very good too
                    q[2].append(rand_ans)
                    i += 1
        self._qa_list = qa_list

    def _prepare_question(self):
        cur_q = self._questions[self._counter]
        cur_ans = list(cur_q[1]) + list(cur_q[2])
        random.shuffle(cur_ans)
        return cur_ans

    def _display_question(self):
        cur_q = self._questions[self._counter]
        d_str = cur_q[0]
        for i in range(len(self._cur_q_list)):
            d_str += '\n' + str(i + 1) + '. ' + self._cur_q_list[i]
        self.display += d_str

    def _display_result(self):
        res_str = ''
        for i in range(len(self._questions)):
            q = self._questions[i]
            forgotten = []
            for ans in q[1]:
                if ans not in self._answers[i]:
                    forgotten.append(ans)
            excess = []
            for ans in self._answers[i]:
                if ans not in q[1]:
                    excess.append(ans)
            res_str += q[0]
            res_str += '\nУказанные ответы: ' + ', '.join(self._answers[i])
            if not len(forgotten) and not len(excess):
                res_str += '\nВсе верно!'
            if len(forgotten) != 0:
                res_str += '\nЗабытые ответы: ' + ', '.join(forgotten)
            if len(excess) != 0:
                    res_str += '\nЛишние ответы: ' + ', '.join(excess)
            if i < len(self._questions) - 1:
                res_str += '\n\n'

        self._on_exit(res_str)


@mode
class GallowsMode(Mode):
    """Gallows mode. Required data format:
    word\nword ...\nword
    """

    name = 'Виселица'
    info = 'Открывайте буквы, угадывая слово'
    settings = {
        'count': Setting(
            type='range',
            default=10,
            widget='range',
            from_=5,
            to=20,
            label='Количество открываемых букв',
        )
    }

    def on_answer(self, answer_text):
        answer_text = answer_text.upper()
        err = ''
        if len(answer_text) == 1:
            if answer_text in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
                if self._countdown != 0:
                    self._letters.add(answer_text)
                    self._countdown -= 1
                    if self._is_word_open():
                        self._finish()
                        return
                else:
                    err = 'Необходимо ввести слово'
        else:
            self._finish(answer_text)
            return
        self._print_word()
        if err:
            self.display += '\n\n' + err
        str_mess = 'Введите слово'
        if self._countdown != 0:
            str_mess += ' или букву'
        str_mess += ':'
        self.display += '\n\n' + str_mess
        if self._countdown != 0:
            self.display += '\n\n' + 'Ходов осталось: ' + str(self._countdown)

    def launch(self):
        print(self._word)
        self._countdown = self.settings['count']
        self._letters = set()
        self._print_word()  # todo test

    def _parse_resource(self, resource_name):
        file_path = os.path.join(self.path, resource_name)
        with open(file_path, 'rt', encoding='utf8') as file:
            words = [word for word in file]  # todo optimize
            self._word = random.choice(words).upper()
            self._word = self._word[0:-1]

    def _print_word(self):
        str_word = ''
        for letter in self._word:
            str_word += ' ' + (letter if letter in self._letters else '_') + ' '
        self.display = str_word

    def _is_word_open(self):
        for letter in self._word:
            if letter not in self._letters:
                return False
        return True

    def _finish(self, ans=None):
        if not ans or ans == self._word:
            self.display = 'Вы угадали, это слово ' + self._word
        else:
            self.display = 'К сожалению Вы не угадали, это слово ' + self._word
