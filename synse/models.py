"""Models for Synse Server response data.

The scope of the models here is similar to the scope of the
``responses``, so there may be some logical overlap. Generally,
a ``response`` serves as a wrapper around an HTTP response and
pulls out some simple data from the response JSON, if present.
A good example of this is the response for the ``/version`` endpoint.
We don't need a separate Version model, so we just expose the
version and api_version directly from the response.

More complicated responses have additional modeling to make things
easier for the consumer of the response. For example, the response for
the ``/scan`` endpoint can have multiple racks, with multiple boards
per rack, and multiple devices per board. Wrapping that nested structure
in some additional modeling makes it easier for the consumer to traverse
and use the response data.
"""


# Modeling for `/scan`

class ScanRack(object):
    """"""

    def __init__(self, data):
        self._board_data = data['boards']

        self.id = data['id']
        self.boards = [ScanBoard(self, board) for board in self._board_data]

    def __str__(self):
        return '<ScanRack {} ({} boards)>'.format(self.id, len(self.boards))

    def __repr__(self):
        return self.__str__()

    @property
    def devices(self):
        """"""
        devices = []
        for board in self.boards:
            devices.extend(board.devices)
        return devices

    def get_board(self, board_id):
        """"""
        for board in self.boards:
            if board.id == board_id:
                return board
        return None


class ScanBoard(object):
    """"""

    def __init__(self, parent, data):
        self.parent = parent
        self._device_data = data['devices']

        self.id = data['id']
        self.devices = [ScanDevice(self, device) for device in self._device_data]

    def __str__(self):
        return '<ScanBoard {} ({} devices)>'.format(self.id, len(self.devices))

    def __repr__(self):
        return self.__str__()

    def get_device(self, device_id):
        """"""
        for device in self.devices:
            if device.id == device_id:
                return device
        return None


class ScanDevice(object):
    """"""

    def __init__(self, parent, data):
        self.parent = parent
        self.id = data['id']
        self.info = data['info']
        self.type = data['type']

    def __str__(self):
        return '<ScanDevice {}>'.format(self.id)

    def __repr__(self):
        return self.__str__()
