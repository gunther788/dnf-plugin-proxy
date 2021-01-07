# yum-plugin-proxy

Dynamically set the proxy and/or enable/disable repositories based on various criteria. Processes
the already enabled repositories mid-flight and updates the "enabled" and "proxy" parameters.

This plugin was originally designed for environments where by default, packages are consumed from an
in-house Foreman/Katello or Satellite, but occasionally, the need arises to tap into additional
external resources that are only reachable by proxy. Over the course of CentOS 7 and 8 and Fedora
releases, the various proxy settings in `yum`/`dnf` and `rhsm` has caused a lot of grief, especially
when some subsystems honor the `no_proxy` environment variable and other do not.

Furthermore, this package also addresses the need to blacklist repositories that have been mirrored
in-house (such as those installed with `centos-linux-release`) and are subject to updates. Simply
zeroing out those files and then cleaning up the `*.repo.rpmnew` files is a bit unsatisfactory.

## Configuration

The plugin is configured in `/etc/yum/pluginconf.d/proxy.conf`:

### `enabled`

Toggle the plugin on (1) or off (0).

### `proxy`/`no_proxy`

`proxy` is of the form `http://proxy.host.example.com:3128/` and points at a http proxy server in your organization.

`no_proxy` is a comma-separated list of domains without trailing dots, e.g. `no_proxy=example.com,internal.net`.

The behaviour of these settings for each repository, in the order they are evaluated:

| repo state | repo url     | `proxy`     | `no_proxy` | result                              |
| ---------- | ------------ | ----------- | ---------- | ----------------------------------- |
| *disabled* | any          | any         | any        | repo is ignored                     |
| *disabled by blacklist* | any | any | any | repo is disabled by blacklisting the repo file |
| enabled    | any          | *set*       | *empty*    | all requests are made via the proxy |
| enabled    | any          | *empty*     | *empty*    | plugin does not affect behaviour    |
| enabled    | *match (1)*  | any         | set        | repo is considered in-house and enabled, proxy is disabled |
| enabled    | *no match (2)* | *set*     | set        | repo is considered off-site and enabled via proxy |
| enabled    | no match (2) | *empty*     | set        | repo is considered off-site and disabled (missing proxy) |

(1) a match of at least one of the `no_proxy` entries and the fqdn in the repo url
(2) no match of any of the `no_proxy` entries and the fqdn in the repo url

## Blacklistfiles

In addition to the above logic, you can also list any number of repo files to be disabled:

`blacklistfiles=CentOS-Linux-Devel,CentOS-Linux-Sources`

will take all repositories contained in `/etc/yum.repos.d/CentOS-Linux-Devel.repo` and `/etc/yum.repos.d/CentOS-Linux-Sources.repo`
and disable them, regardless of the other settings.

## Installation

To ease the installation and configuration of this plugin, environment variables may be set to inject values into the
configuration file:

The `%post` of the package contains:
```
egrep -e "^proxy=" %{pluginconf} || echo "proxy=${PROXY_PLUGIN_PROXY}" >> %{pluginconf}
egrep -e "^no_proxy=" %{pluginconf} || echo "no_proxy=${PROXY_PLUGIN_NO_PROXY}" >> %{pluginconf}
egrep -e "^blacklistfiles=" %{pluginconf} || echo "blacklistfiles=${PROXY_PLUGIN_BLACKLISTFILES}" >> %{pluginconf}
```

## Environment Variables

The `http_proxy`/`https_proxy` environment variables will override (or set) the `proxy` entry in the configuration file.

The `no_proxy` environment variable will override (or set) the `no_proxy` entry in the configuration file.
