class CommandHandler():

    class Exception(Exception):
        pass

    class NA():
        def __str__(self):
            return '= NA'

    class Value():
        def __init__(self, value):
            self._value = value
        def __str__(self):
            return f'= {self._value}'

    class Text():
        def __init__(self, text):
            if isinstance(text, list):
                self._lines = text
            else:
                self._lines = [text]
        def __str__(self):
            return '\n'.join(self._lines)

    class Error():
        def __init__(self, error):
            self._error = error
        def __str__(self):
            return self._error

    class Warning():
        def __init__(self, error):
            self._warning = error
        def __str__(self):
            return self._warning

    def __init__(self, log):
        self._log = log

    def commandDict(self):
        raise NotImplementedError()

    def handle(self, input):
        raise NotImplementedError()

    def echoValue(self, value):
        print('= ', value)

    def echoNA(self):
        pring('= NA')
