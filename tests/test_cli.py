import os

from pathlib import Path

import pytest

from typer.testing import CliRunner
from noir.cli import app

_expected_output = """server {
  listen 80;
  server_name localhost;

  root /var/www/project;
  index index.htm;

  access_log /var/log/nginx/http.access.log combined;
  error_log  /var/log/nginx/http.error.log;
}
"""


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture(scope="function")
def asset():
    cwd = Path(os.getcwd())
    local = Path(__file__).resolve().parent / "assets"

    def m(file: str) -> str:
        return str((local / file).relative_to(cwd))

    return m


def test_env(runner, asset):
    res = runner.invoke(
        app, [asset("nginx.ns.tpl"), "-c", f"nginx:{asset('ctx.env')}"]
    )
    assert res.exit_code == 0
    assert res.output == _expected_output

    res = runner.invoke(app, [
        asset("nginx.ns.tpl"),
        "-c", f"nginx:{asset('ctx.empty.env')}",
        "-v", "nginx:hostname=localhost",
        "-v", "nginx:webroot=/var/www/project",
        "-v", "nginx:logs=/var/log/nginx/"
    ])
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_ini(runner, asset):
    res = runner.invoke(app, [asset("nginx.ns.tpl"), "-c", asset('ctx.ini')])
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_json(runner, asset):
    res = runner.invoke(app, [asset("nginx.ns.tpl"), "-c", asset('ctx.json')])
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_toml(runner, asset):
    res = runner.invoke(app, [asset("nginx.ns.tpl"), "-c", asset('ctx.toml')])
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_yaml(runner, asset):
    res = runner.invoke(app, [asset("nginx.ns.tpl"), "-c", asset('ctx.yaml')])
    assert res.exit_code == 0
    assert res.output == _expected_output

    res = runner.invoke(app, [asset("nginx.ns.tpl"), "-c", asset('ctx.yml')])
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_osenv(runner, asset):
    res = runner.invoke(app, [asset("nginx.osenv.tpl")], env={
        "NGINX_HOSTNAME": "localhost",
        "NGINX_WEBROOT": "/var/www/project",
        "NGINX_LOGS": "/var/log/nginx/"
    })
    assert res.exit_code == 0
    assert res.output == _expected_output


def test_vars(runner, asset):
    res = runner.invoke(app, [
        asset("nginx.var.tpl"),
        "-v", "hostname=localhost",
        "-v", "webroot=/var/www/project",
        "-v", "logs:path=/var/log/nginx/"
    ])
    assert res.exit_code == 0
    assert res.output == _expected_output
