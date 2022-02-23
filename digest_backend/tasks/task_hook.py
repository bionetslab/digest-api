class TaskHook:

    def __init__(self, parameters, set_status,set_result, mapper):
        self.__parameters = parameters
        self.__set_result = set_result
        self.__set_status = set_status
        self.__mapper = mapper


    @property
    def parameters(self):
        """
        Returns parameters selected for the algorithm.

        :return: Parameters as dictionary (e.g. {"proteins": [...], "paramA": 123, "paramB": True, ...})
        """
        return self.__parameters


    def get_mapper(self):
        print("getting mapper with boole: "+str(self.__mapper.load))
        """
        Returns parameters selected for the algorithm.

        :return: Parameters as dictionary (e.g. {"proteins": [...], "paramA": 123, "paramB": True, ...})
        """
        return self.__mapper

    def set_status(self, status):
        """
        To be called to indicate computation progress.

        :param progress: A float between 0.0 and 1.0 (e.g. 0.5 for 50% progress)
        :param status: A string indicating the status (e.g. 'Parsing file')
        :return:
        """
        self.__set_status(status)

    def set_results(self, results):
        """
        To be called when the computation is finished.

        :param results: A dictionary containing a networks entry, each network having nodes and edges.
        (e.g. {"network": {"nodes": ["P61970", "Q9H4P4"], "edges": [{"from": "P61970", "to": "Q9H4P4"}]}})
        """
        self.__set_result(results)
