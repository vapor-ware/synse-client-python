"""Response for the /version endpoint."""


class Version(object):
    """Version response for the Synse Server /version endpoint.

    Args:
        response (requests.Response): The HTTP response from Synse
            Server.

    Attributes:
        response (requests.Response): The HTTP response from Synse
            Server.
        version (str): The full version of Synse Server.
        api_version (str): The API version that can be used to
            construct additional request URLs.
    """

    def __init__(self, response):
        self.response = response

        data = response.json()
        self.version = data['version']
        self.api_version = data['api_version']

    def __str__(self):
        return '<responses.Version [{}]>'.format(self.response.status_code)

    def __repr__(self):
        return self.__str__()
