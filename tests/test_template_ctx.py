import base64

from noir.templating import (
    _base64decode,
    _base64encode,
    _cidr_host,
    _cidr_netmask,
    _cidr_subnet,
    _cidr_subnets
)


def test_cidr_host():
    assert _cidr_host("10.12.112.0/20", 16) == "10.12.112.16"
    assert _cidr_host("10.12.112.0/20", 268) == "10.12.113.12"
    assert _cidr_host("fd00:fd12:3456:7890:00a2::/72", 34) == "fd00:fd12:3456:7890::22"


def test_cidr_netmask():
    assert _cidr_netmask("172.16.0.0/12") == "255.240.0.0"


def test_cidr_subnet():
    assert _cidr_subnet("172.16.0.0/12", 4, 2) == "172.18.0.0/16"
    assert _cidr_subnet("10.1.2.0/24", 4, 15) == "10.1.2.240/28"
    assert _cidr_subnet("fd00:fd12:3456:7890::/56", 16, 162) == "fd00:fd12:3456:7800:a200::/72"


def test_cidr_subnets():
    assert set(_cidr_subnets("10.1.0.0/16", 4, 4, 8, 4)) == {
        "10.1.0.0/20",
        "10.1.16.0/20",
        "10.1.32.0/24",
        "10.1.48.0/20",
    }


def test_base64decode():
    exp = base64.b64encode(b"test").decode()
    assert _base64encode("test") == exp


def test_base64encode():
    v = base64.b64encode(b"test")
    exp = base64.b64decode(v).decode()
    assert _base64decode(v.decode()) == exp
