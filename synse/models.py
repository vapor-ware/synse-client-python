"""Synse client response model definitions."""

from typing import Type, Union

import iso8601


class BaseResponse:
    """The base class for all of the Synse client's response classes.

    Attributes:
        _data: The JSON data returned in the response, as a dictionary.
    """

    def __init__(self, data: dict):
        self._data = data

        for k, v in self._data.items():
            if hasattr(self, k):
                # The timestamp, created, and updated fields will all
                # hold an RFC3339-formatted timestamp string. Here, we
                # convert that string to a datetime.datetime instance.
                if k in ('timestamp', 'created', 'updated'):
                    v = iso8601.parse_date(v)
                setattr(self, k, v)


def make_response(
        response_class: Union[Type[BaseResponse], None],
        response: Union[dict, list],
):
    """Populate a Synse response object with data from the given HTTP response.

    Args:
        response_class: The Synse response class to load the data into.
        response: The JSON response from Synse Server.
    """

    if response_class is None:
        return response

    if isinstance(response, list):
        return [response_class(item) for item in response]

    return response_class(response)


class Config(BaseResponse):
    """Config models the response for Synse Server's v3 HTTP API
    ``/v3/config`` endpoint.

    It does not define any attributes. Instead, the configuration value
    should be taken from the response's ``data`` field, which holds the
    JSON data returned in the response.
    """

    def __init__(self, data: dict):
        super(Config, self).__init__(data)
        self.data = self._data


class DeviceInfo(BaseResponse):
    """DeviceInfo models the response for Synse Server's v3 HTTP API
    ``/v3/info/<device>`` endpoint.

    Attributes:
        alias (str): A human-readable name for the device.
        capabilities (dict): Specifies the actions which the device is able to
            perform (e.g. read, write).
        id (str): The globally unique ID for the device.
        info (str): A human readable string providing identifying info about a device.
        metadata (dict): A dictionary of arbitrary values that provide additional
            data for the device.
        outputs (list[dict]): A list of the output types that the device supports.
        plugin (str): The ID of the plugin that manages the device.
        sort_index (int): A custom sort index specified for the device by its plugin.
            The default value of 0 indicates no special sorting.
        tags (list[str]): A list of the tags associated with this device.
        timestamp (datetime.datetime): A timestamp describing the time that the
            device info was gathered.
        type (str): The device type, as specified by the plugin.
    """

    def __init__(self, data: dict):
        self.alias = None
        self.capabilities = None
        self.id = None
        self.info = None
        self.metadata = None
        self.outputs = None
        self.plugin = None
        self.sort_index = None
        self.tags = None
        self.timestamp = None
        self.type = None

        super(DeviceInfo, self).__init__(data)


class DeviceSummary(BaseResponse):
    """DeviceSummary models the response for Synse Server's v3 HTTP API
    ``/v3/scan`` endpoint.

    Attributes:
        alias (str): The human-readable alias for the device, if set.
        id (str): The globally unique ID for the device.
        info (str): A human readable string providing identifying info about a device.
        plugin (str): The ID of the plugin which the device is managed by.
        tags (list[str]): A list of the tags associated with this device.
        type (str): The type of the device, as defined by its plugin.
    """

    def __init__(self, data: dict):
        self.alias = None
        self.id = None
        self.info = None
        self.metadata = None
        self.plugin = None
        self.tags = None
        self.type = None

        super(DeviceSummary, self).__init__(data)


class PluginHealth(BaseResponse):
    """PluginHealth models the response for Synse Server's v3 HTTP API
    ``/v3/plugin/health`` endpoint.

    Attributes:
        active (int): The count of active plugins.
        healthy (list[str]): A list containing the plugin IDs for those plugins deemed
            to be healthy.
        inactive (int): The count of inactive plugins.
        status (str): A string describing the overall health state of the registered
            plugin(s). This can be either "healthy" or "unhealthy". It will only be
            healthy if all plugins are found to be healthy, otherwise the overall
            state is unhealthy.
        unhealthy (list[str]): A list containing the plugin IDs for those plugins
            deemed to be unhealthy.
        updated (datetime.datetime): A timestamp describing the time that the plugin
            health state was last updated.
    """

    def __init__(self, data: dict):
        self.active = None
        self.healthy = None
        self.inactive = None
        self.status = None
        self.unhealthy = None
        self.updated = None

        super(PluginHealth, self).__init__(data)


class PluginInfo(BaseResponse):
    """PluginInfo models the response for Synse Server's v3 HTTP API
    ``/v3/plugin/<plugin-id>`` endpoint.

    Attributes:
        active (bool): Specifies whether the plugin is currently active or not.
        description (str): A short description of the plugin.
        health (dict): Describes the overall health of the plugin.
        id (str): An ID hash for identifying the plugin, generated from plugin metadata.
        maintainer (str): The maintainer of the plugin.
        name (str): The name of plugin.
        network (dict): Describes the network configurations for the plugin.
        tag (str): The plugin tag. This is a normalized string made up of its name
            and maintainer.
        version (dict): The version information about the plugin.
        vcs (str): A link to the version control repo for the plugin.
    """

    def __init__(self, data: dict):
        self.active = None
        self.description = None
        self.health = None
        self.id = None
        self.maintainer = None
        self.name = None
        self.network = None
        self.tag = None
        self.version = None
        self.vcs = None

        super(PluginInfo, self).__init__(data)


class PluginSummary(BaseResponse):
    """PluginSummary models the response for Synse Server's v3 HTTP API
    ``/v3/plugin`` endpoint.

    Attributes:
        active (bool): Specifies whether the plugin is currently active or not.
        description (str): A short description of the plugin.
        id (str): An ID hash for identifying the plugin, generated from plugin metadata.
        maintainer (str): The maintainer of the plugin.
        name (str): The name of plugin.
        tag (str): The plugin tag. This is a normalized string made up of the
            name and maintainer.
    """

    def __init__(self, data: dict):
        self.active = None
        self.description = None
        self.id = None
        self.maintainer = None
        self.name = None
        self.tag = None

        super(PluginSummary, self).__init__(data)


class Reading(BaseResponse):
    """Reading models the response for Synse Server's v3 HTTP API
    ``/v3/read``, ``/v3/read/<device>``, and ``/v3/readcache`` endpoints.

    Attributes:
        context (dict): A mapping of arbitrary values to provide additional context
            for the reading.
        device (str): The ID of the device which the reading originated from.
        device_type (str): The type of the device.
        timestamp (datetime.datetime): A timestamp describing the time at which the
            reading was taken.
        type (str): The type of the reading.
        unit (dict): The unit of measure for the reading.
        value: The value of the reading.
    """

    def __init__(self, data: dict):
        self.context = None
        self.device = None
        self.device_type = None
        self.timestamp = None
        self.type = None
        self.unit = None
        self.value = None

        super(Reading, self).__init__(data)


class Status(BaseResponse):
    """Status models the response for Synse Server's v3 HTTP API
    ``/test`` endpoint.

    Attributes:
        status (str): "ok" if the endpoint returns successfully.
        timestamp (datetime.datetime): The time at which the status was tested.
    """

    def __init__(self, data: dict):
        self.status = None
        self.timestamp = None

        super(Status, self).__init__(data)


class TransactionInfo(BaseResponse):
    """TransactionInfo models the response for Synse Server's v3 HTTP API
    ``/v3/write/<device>`` endpoint.

    Attributes:
        context (dict): The data written to the device. This is provided as context
            info to help identify the write action.
        device (str): The ID of the device being written to.
        id (str): The ID for the transaction.
        timeout (str): The timeout for the write transaction, after which it will
            be cancelled. This is effectively the maximum wait time for the transaction
            to resolve.
    """

    def __init__(self, data: dict):
        self.context = None
        self.device = None
        self.id = None
        self.timeout = None

        super(TransactionInfo, self).__init__(data)


class TransactionStatus(BaseResponse):
    """TransactionStatus models the response for Synse Server's v3 HTTP API
    ``/v3/transaction/<transaction-id>`` and ``/v3/write/wait/<device>`` endpoints.

    Attributes:
        context (dict): The POSTed write data for the given write transaction.
        created (datetime.datetime): The time at which the transaction was created.
        device (str): The ID of the device being written to.
        id (str): The ID of the transaction.
        message (str): Any context information relating to a transaction's error
            state. If there is no error, this will be an empty string.
        status (str): The current status of the transaction. (pending, writing,
            done, error)
        timeout (str): A string representing the timeout for the write transaction
            after which it will be cancelled. This is effectively the maximum wait
            time for the transaction to resolve.
        updated (datetime.datetime): The last time the transaction state or status
            was updated. Once the transaction reaches a done status or error state,
            no further updates will occur.
    """

    def __init__(self, data: dict):
        self.context = None
        self.created = None
        self.device = None
        self.id = None
        self.message = None
        self.status = None
        self.timeout = None
        self.updated = None

        super(TransactionStatus, self).__init__(data)


class Version(BaseResponse):
    """Version models the response for Synse Server's v3 HTTP API
    ``/version`` endpoint.

    Attributes:
        api_version (str): The API version (v<major>) of the Synse Server instance.
        version (str): The full version (<major>.<minor>.<patch>) of the Synse
            Server instance.
    """

    def __init__(self, data: dict):
        self.api_version = None
        self.version = None

        super(Version, self).__init__(data)
