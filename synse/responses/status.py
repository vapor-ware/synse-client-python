"""Response for the /test endpoint."""

import iso8601


class Status(object):
    """"""

    def __init__(self, response):
        self.response = response

        data = response.json()
        self.status = data['status']
        self.timestamp = iso8601.parse_date(data['timestamp'])

    @property
    def ok(self):
        """"""
        return self.status == 'ok'

    def __str__(self):
        return '<responses.Status [{}]>'.format(self.response.status_code)

    def __repr__(self):
        return self.__str__()
