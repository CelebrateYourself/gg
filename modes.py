
import abc
import os
import random


modes = []


def mode(mode_class):
    modes.append(mode_class)



class Mode(abc.ABC):

    info = 'Abstract mode text'

    def __init__(self, *, window, resource_name, on_exit):
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
    settings = {}

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
        TEST_LENGTH = 10
        questions = random.sample(self.qa_dict.keys(), TEST_LENGTH)
        random.shuffle(questions)
    
        self.questions_i = iter(questions)
        self.pattern = '{}\n\n>> {}'
        self.length = len(questions)
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
                    qa_dict[q_tuple] = a_tuple

        self.qa_dict = qa_dict


@mode
class TestMode(Mode):
    """Режим тестирования. Формат данных описан ниже, если не указаны неправильные ответы,
    они берутся из правильных ответов на другие вопросы"""
    RESOURCE_PATTERN = 'question = correct_answer_1(ca1) | ca2 | ... ca3 ?' \
                       ' (optional) incorrect_answer_1(ia1) | ia2 | ... ia3'
    INCORRECT_ANSWERS_MIN = 2  # Минимальное кол-во неправильных ответов, если они не заданы в файле
    INCORRECT_ANSWERS_MAX = 5
    name = 'Тесты'
    info = 'Выбор правильных ответов на вопрос из предложенного списка (числа через пробел)'
    settings = {}

    def on_answer(self, answer_text):  # todo check errors
        ans = []
        for ind in answer_text.split(' '):
            ans.append(self._cur_q_list[int(ind.strip()) - 1])
        self._answers.append(ans)
        self._counter += 1
        if self._counter == len(self._questions):
            self._display_result()
        else:
            self._cur_q_list = self._prepare_question()
            self._display()

    def launch(self):
        print(self._qa_list)
        test_length = 5
        self._questions = random.sample(self._qa_list, test_length)
        random.shuffle(self._questions)
        self._counter = 0
        self._answers = []
        self._cur_q_list = self._prepare_question()
        self._display()

    def _parse_resource(self, resource_name):
        file_path = os.path.join(self.path, resource_name)
        qa_list = []  # [вопрос, [правильные ответы], [неправильные ответы]]
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
        for q in qa_list:  # Если неправильные отверы не указаны, натаскать их из правильных на другие вопросы
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

    def _display(self):
        cur_q = self._questions[self._counter]
        d_str = cur_q[0]
        for i in range(len(self._cur_q_list)):
            d_str += '\n' + str(i + 1) + '. ' + self._cur_q_list[i]
        self.display = d_str

    def _display_result(self):
        res_str = ''
        for i in range(len(self._questions)):
            q = self._questions[i]
            res_str += '\n' + q[0] + ' (' + ', '.join(q[1]) + ') (' +\
                       ', '.join(self._answers[i]) + ')\n'
        self._on_exit(res_str)
