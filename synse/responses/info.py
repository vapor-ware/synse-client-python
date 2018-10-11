"""Response for the /info endpoint."""


class Info(object):
    """"""

    def __init__(self, response):
        self.response = response

        data = response.json()

    def __str__(self):
        return '<responses.Info [{}]>'.format(self.response.status_code)

    def __repr__(self):
        return self.__str__()
