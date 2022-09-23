import time

class Logger():

    def __init__(self, files="/dev/null", print=False, debug=False):
        if isinstance(files, list):
            self.files = files
        else:
            self.files = [files]

        self.print = print
        self.debug = debug

        self.out = []
        for ff, file in enumerate(self.files):
            self.out.append(open(file, 'a'))
            self.log("LOGGER", f"Opened the file [{self.files[ff]}].")

    def close(self):
        for ff, stream in enumerate(self.out):
            if stream and not stream.closed:
                self.log("LOGGER", f"Closed the file [{self.files[ff]}].")
                stream.close()
        self.stream = []

    def __del__(self):
        self.close()

    def log(self, cat, msg):
        line = "(%s) [%s]: %s"%(time.strftime("%Y-%m-%d %H:%M:%S"), cat, '\n>> '.join(msg.split('\n')))
        for stream in self.out:
            if not stream.closed:
                stream.write(line + "\n")
        if self.print:
            print(line)
