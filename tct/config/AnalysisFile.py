from .ConfigFile import ConfigFile
from .AnalysisDefinition import AnalysisDefinition

class AnalysisFile(ConfigFile):

    def __init__(self, file):
        super().__init__(file)

        # Load all the data - This also verifies the file
        self.analysis = self._getAnalysis()


    def _getAnalysis(self):
        analysis = self._get(['analysis'], required=False)
        if analysis is None:
            return []

        if isinstance(analysis, dict):
            analysis = [analysis]

        definitions = []
        for entry in analysis:
            definitions.append(AnalysisDefinition(entry))

        return definitions
