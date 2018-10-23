
import abc
import os
import random


modes = []


def mode(mode_class):
    modes.append(mode_class)



class Mode(abc.ABC):

    info = 'Abstract mode text'

    def __init__(self, *, display, resource_name, on_exit):
        self._display = display
        self._on_exit = on_exit
        self._parse_resource(resource_name)

    @property
    def display(self):
        return self._display.get()

    @display.setter
    def display(self, text):
        self._display.set(text)

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
    def _parse_resource(self):
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
                bad_answers += '{} - {} -> {}\n'.format(
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
        self.pattern = '{}\n\n-> {}'
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