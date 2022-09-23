class TCTData():

    def __init__(self, prefix):
        self.prefix = prefix

    def metadata(self):
        raise NotImplementedError()

    def count(self):
        raise NotImplementedError()

    def curve(self, idx):
        raise NotImplementedError()

    def copy(self, target):
        raise NotImplementedError()
