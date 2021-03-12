import requests, time, config, logging
from urllib.parse import urlencode


logger = logging.getLogger(__name__)


class Request(object):
    """
        class to handle the request type.
    """
    def __init__(self, base_url, endpoint):
        """
            Constructor.

            :param endpoint.
                Endpoint to make the get request.
        """
        self.counter = 1
        self.base_url = base_url
        self.endpoint = endpoint


    def get(self, headers=None, query=None):
        """
            Get data from api. 
            Raises Errors if needed to handled by the errors handler.

            :param headers
                Headers to add to the request object. Defaults to None.
            :param query
                Query dict to be urlencoded. Defaults to None.
        """
        url = self.base_url + self.endpoint
        if query != None:
            url = url + "?" + urlencode(query)

        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            logger.debug(req.text)
            rsl = req.json()
            self.counter = 1
            return rsl
        elif req.status_code == 429:
            logging.warning(
                "ConnectionError: MaximumRequests from {}. Waiting: {}".format(
                    url, int(self.counter * config.API_SERVER_CALLS_TIMEOUT)
            ))
            time.sleep(self.counter * config.API_SERVER_CALLS_TIMEOUT)
            self.counter += 1
            self.get(headers, query)
        elif req.status_code >= 500:
            logger.warning(
                "ServerError: from {}. Waiting: {}".format(
                    url, 
                    int(self.counter * config.API_SERVER_NOT_AVAILABLE_TIMEOUT)
                ))
            time.sleep(self.counter * config.API_SERVER_NOT_AVAILABLE_TIMEOUT)
            self.counter += 1
            self.get(headers, query)


    def post(self, headers, data=None):
        """
            Post data to exchange API.
            Raises Errors if needed to handled by the errors handler.

            :param headers
                Headers to add to the request object. Defaults to None.
            :param data
                Data to be encoded and added to the request.
        """
        url = self.base_url + self.endpoint
        req = requests.post(url, headers=headers, data=data)
        rsl = req.json()
        return rsl
