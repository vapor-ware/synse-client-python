"""Response for the /config endpoint."""


class Config(object):
    """"""

    def __init__(self, response):
        self.response = response

        data = response.json()

    def __str__(self):
        return '<responses.Config [{}]>'.format(self.response.status_code)

    def __repr__(self):
        return self.__str__()
