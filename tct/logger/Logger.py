import time

class Logger():

    def __init__(self, file="/dev/null", print=False, debug=False):
        self.file = file

        self.print = print
        self.debug = debug

        self.out = None
        self.out = open(file, 'a')
        self.log("LOGGER", "Opened the file")

    def __del__(self):
        if self.out and not self.out.closed:
            self.log("LOGGER", "Closed the file")
            self.out.close()

    def log(self, cat, msg):
        line = "(%s) [%s]: %s"%(time.strftime("%Y-%m-%d %H:%M:%S"), cat, '\n>> '.join(msg.split('\n')))
        if not self.out.closed:
            self.out.write(line + "\n")
        if self.print:
            print(line)
