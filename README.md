# Noir

Noir – /nwɑːr/ – is a template renderer based on [Renoir](https://github.com/emmett-framework/renoir) templating engine.

Typical use case for Noir is generating configuration files and manifests for services and applications.

Inspired by [mkolypto/j2cli](https://github.com/kolypto/j2cli)

## Installation

You can install Noir using [Homebrew](https://brew.sh/):

    brew install gi0baro/tap/noir

or you can manually download the packages from the [releases page](https://github.com/gi0baro/noir/releases).

## Usage

```console
$ noir --help
Usage: noir [OPTIONS] SOURCE

  Render a SOURCE template file or string using specified contexts and vars.

Arguments:
  SOURCE  The template file to use.  [required]

Options:
  -e, --eval                      Parse source as template string.
  -v, --var TEXT                  Context variable(s) to apply.
  -c, --context PATH              Context file(s) to use.
  -f, --format [env|ini|json|toml|yaml|yml]
                                  Context file format (default: guess from
                                  file extension).
  -o, --output FILENAME           Target output (default: stdout)
  --delimiters TEXT               Template delimiters  [default: {{,}}]
  --version                       Show the version and exit.
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```

The `noir` command accepts as the only argument the template file or string to render.

Contextual data con be loaded from a file, using the `-c/--context` option, which supports the formats:

- env
- ini
- json
- toml
- yaml

or directly from the command using the `-v/--var` option.

Both options support defining a namespace using the `namespace:var` notation.

### Context helpers

#### libraries

The default context in Noir already imports the following modules from the Python standard library:

- base64
- datetime
- hashlib
- random
- uuid

> **Note:** additional modules from standard library might be loaded with the `import` statement

#### env

An object containing environment variables.

```ini
foo="{{ =env.VAR_FOO }}"
bar="{{ =env["VAR_BAR"] }}"
```

#### Base64 shortcuts

Shortcuts for `base64.b64encode` and `base64.b64decode` handling encoding/decoding:

```yaml
hash: {{ =base64encode("foobar") }}
decoded_hash: {{ =base64decode(hash) }}
```

#### CIDR helpers

Functions to interact with IPv4/IPv6 objects:

```
cidr.subnet(prefix, newbits, netnum)
cidr.host(prefix, hostnum)
cidr.netmask(prefix)
cidr.subnets(prefix, *newbits)
```

#### Pathlib Path

```yaml
target: {{ =Path.cwd() / "target" / "foo.bar" }}
```

#### indent

A function to indent a text with the given number of spaces.

```yaml
data: |-
  {{ =indent(multiline_str, 2) }}
```

#### to_json

A function to render json content. Accepts an optional integer indent parameter.

```json
{
    "key": "value",
    "data": {{ =to_json(data, indent=None) }}
}
```

#### to_toml

A function to render TOML content.

```toml
[data]
foo = "bar"
{{ =to_toml(data) }}
```

#### to_yaml

A function to render YAML content.

```yaml
data:
  {{ =indent(to_yaml(data), 2) }}
```

## Examples

Suppose you have an nginx configuration file template `nginx.conf.tpl`:

```
server {
  listen 80;
  server_name {{ =nginx.hostname }};

  root {{ =nginx.webroot }};
  index index.htm;
}
```

and you have a YAML file `nginx.yaml`:

```yaml
nginx:
  hostname: localhost
  webroot: /var/www/project
```

Then you can render you configuration file as:

```console
$ noir nginx.conf.tpl -c nginx.yaml > nginx.conf
```

which will produce the following `nginx.conf`:

```
server {
  listen 80;
  server_name localhost;

  root /var/www/project;
  index index.htm;
}
```

You can reach the same result passing variables directly, like:

```console
$ noir nginx.conf.tpl \
    -v nginx:hostname=localhost \
    -v nginx:webroot=/var/www/project \
    > nginx.conf
```

Since [Renoir](https://github.com/emmett-framework/renoir) supports fully-functional Python code, you can also define structures and import libraries, for example you can produce a `secrets.yaml` manifest for kubernetes using environment variables starting with `K8S_`:

```yaml
{{ secrets = {k.strip("K8S_"): v for k, v in env.items() if k.startswith("K8S_")} }}
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: secret
data:
  {{ for k, v in secrets.items(): }}
  {{ =k }}: "{{ =base64.b64encode(v.encode("utf-8")) }}"
  {{ pass }}
```

and render it:

```console
$ export K8S_VAR1=val1
$ export K8S_VAR2=val2
$ noir secrets.yaml
```

Here are some additional examples:

```console
$ # use environment variables
$ noir -e 'Hello, {{ =env.USER }}'
Hello, gi0baro

$ # do some math
$ noir -e 'the answer is: {{ =6 * 7 }}'
the answer is: 42

$ # ranges
$ noir -e '{{ for i in range(5, 0, -1): }}{{ =f"{i} " }}{{ if i == 1: }}{{ ="blastoff".upper() }}{{ pass }}{{ pass }}'
5 4 3 2 1 BLASTOFF

$ # context from curl requests
$ curl -s https://ipinfo.io | noir -c ip:- -f json -e 'country code: {{ =ip.country }}'
country code: IT

$ # pretty printing from stdin
$ echo '{"cities":["London", "Rome", "New York"]}' | noir -c - -f json -e '{{ =", ".join(cities) }}'
London, Rome, New York
```
