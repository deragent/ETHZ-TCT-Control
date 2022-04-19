class TCTOutput():

    def __init__(self, prefix):
        self.prefix = prefix

    def storeCurve(self, x, y, metadata={}):
        raise NotImplementedError()

    def storeMetaData(self, metadata):
        raise NotImplementedError()
