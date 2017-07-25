# coding: utf-8

"""
    data.world API

    data.world's mission is to build the most meaningful, collaborative, and abundant data resource in the world, so that people who work with data can solve problems faster.&nbsp;&nbsp; In the context of that mission, this API ensures that our users are able to easily access data and manage their data projects regardless of system or tool preference.

    OpenAPI spec version: 0.2.2
    Contact: help@data.world
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class UserDataResponse(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'avatar_url': 'str',
        'created': 'str',
        'display_name': 'str',
        'id': 'str',
        'updated': 'str'
    }

    attribute_map = {
        'avatar_url': 'avatarUrl',
        'created': 'created',
        'display_name': 'displayName',
        'id': 'id',
        'updated': 'updated'
    }

    def __init__(self, avatar_url=None, created=None, display_name=None, id=None, updated=None):
        """
        UserDataResponse - a model defined in Swagger
        """

        self._avatar_url = None
        self._created = None
        self._display_name = None
        self._id = None
        self._updated = None

        if avatar_url is not None:
          self.avatar_url = avatar_url
        self.created = created
        if display_name is not None:
          self.display_name = display_name
        self.id = id
        self.updated = updated

    @property
    def avatar_url(self):
        """
        Gets the avatar_url of this UserDataResponse.
        URL of profile image.

        :return: The avatar_url of this UserDataResponse.
        :rtype: str
        """
        return self._avatar_url

    @avatar_url.setter
    def avatar_url(self, avatar_url):
        """
        Sets the avatar_url of this UserDataResponse.
        URL of profile image.

        :param avatar_url: The avatar_url of this UserDataResponse.
        :type: str
        """
        if avatar_url is not None and len(avatar_url) > 256:
            raise ValueError("Invalid value for `avatar_url`, length must be less than or equal to `256`")
        if avatar_url is not None and len(avatar_url) < 0:
            raise ValueError("Invalid value for `avatar_url`, length must be greater than or equal to `0`")

        self._avatar_url = avatar_url

    @property
    def created(self):
        """
        Gets the created of this UserDataResponse.
        Date and time when account was created.

        :return: The created of this UserDataResponse.
        :rtype: str
        """
        return self._created

    @created.setter
    def created(self, created):
        """
        Sets the created of this UserDataResponse.
        Date and time when account was created.

        :param created: The created of this UserDataResponse.
        :type: str
        """
        if created is None:
            raise ValueError("Invalid value for `created`, must not be `None`")

        self._created = created

    @property
    def display_name(self):
        """
        Gets the display_name of this UserDataResponse.
        User's name.

        :return: The display_name of this UserDataResponse.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Sets the display_name of this UserDataResponse.
        User's name.

        :param display_name: The display_name of this UserDataResponse.
        :type: str
        """
        if display_name is not None and len(display_name) > 128:
            raise ValueError("Invalid value for `display_name`, length must be less than or equal to `128`")
        if display_name is not None and len(display_name) < 0:
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `0`")

        self._display_name = display_name

    @property
    def id(self):
        """
        Gets the id of this UserDataResponse.
        User name and unique identifier.

        :return: The id of this UserDataResponse.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this UserDataResponse.
        User name and unique identifier.

        :param id: The id of this UserDataResponse.
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")

        self._id = id

    @property
    def updated(self):
        """
        Gets the updated of this UserDataResponse.
        Date and time when account was last updated.

        :return: The updated of this UserDataResponse.
        :rtype: str
        """
        return self._updated

    @updated.setter
    def updated(self, updated):
        """
        Sets the updated of this UserDataResponse.
        Date and time when account was last updated.

        :param updated: The updated of this UserDataResponse.
        :type: str
        """
        if updated is None:
            raise ValueError("Invalid value for `updated`, must not be `None`")

        self._updated = updated

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, UserDataResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other