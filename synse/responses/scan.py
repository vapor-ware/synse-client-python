"""Response for the /scan endpoint."""

from synse.models import ScanRack


class Scan(object):
    """"""

    def __init__(self, response):
        self.response = response

        data = response.json()
        self.racks = [ScanRack(rack) for rack in data['racks']]

    def get_rack(self, rack_id):
        """"""
        for rack in self.racks:
            if rack.id == rack_id:
                return rack
        return None

    def __str__(self):
        return '<responses.Scan [{}]>'.format(self.response.status_code)

    def __repr__(self):
        return self.__str__()
