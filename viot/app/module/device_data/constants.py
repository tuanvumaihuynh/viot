from enum import IntEnum, StrEnum


class DeviceAttributeScope(IntEnum):
    """Device attribute scope

    SERVER_SCOPE = 0
    SHARED_SCOPE = 1
    CLIENT_SCOPE = 2
    """

    SERVER_SCOPE = 0
    SHARED_SCOPE = 1
    CLIENT_SCOPE = 2


class ConnectStatus(IntEnum):
    """Connect status

    DISCONNECTED = 0
    CONNECTED = 1
    FAILED = 2
    """

    DISCONNECTED = 0
    CONNECTED = 1
    FAILED = 2


class AggregationType(StrEnum):
    """Aggregation type

    AVG = avg
    SUM = sum
    MIN = min
    MAX = max
    COUNT = count
    """

    AVG = "avg"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"


class IntervalType(StrEnum):
    """Interval type

    MILLISECOND = millisecond
    HOUR = hour
    DAY = day
    WEEK = week
    MONTH = month
    YEAR = year
    """

    MILLISECOND = "millisecond"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Timezone(StrEnum):
    """
    Timezone represents a timezone string.
    """

    UTC = "UTC"
    VIETNAM = "Asia/Ho_Chi_Minh"
    SINGAPORE = "Asia/Singapore"
    NEW_YORK = "America/New_York"
