from .utils import log_message


class QueryEngine:
    """A query engine is present in order to modify results of a query. For , example integrating Query validators or differential Privacy."""

    def __init__(self):

        pass

    def call(self, result, dataset, operation: str):
        """method is called to modify a given query. Currently it just logs messages

        Args:
            result: The result retrieved by a given query
            dataset: The original dataset before obtained the result
            query[str]: The query performed on a given dataset

        returns:
            result: Returns the result after performing a given query
        """

        log_message("QueryEngine", "NONE")

        return result
