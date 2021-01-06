Name:           yum-plugin-proxy
Version:        1.0.3
Release:        0%{?dist}
Summary:        Dynamically set the proxy and/or enable/disable repositories

License:        GPLv2+
URL:            https://github.com/gunther788/yum-plugin-proxy
Source0:        proxy.py
Source1:        proxy.conf
BuildArch:      noarch

%define pluginpath /usr/lib/yum-plugins

%description
Dynamically set the proxy and/or enable/disable repositories based on various criteria. Processes
the already enabled repositories mid-flight and updates the "enabled" and "proxy" parameters.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{pluginpath}
install -m644 %{SOURCE0} %{buildroot}%{pluginpath}/proxy.py
mkdir -p %{buildroot}/etc/yum/pluginconf.d
install -m644 %{SOURCE1} %{buildroot}/etc/yum/pluginconf.d/proxy.conf

%files
%defattr(0644,root,root,-)
%{pluginpath}/proxy.py
%config /etc/yum/pluginconf.d/proxy.conf

%changelog
* Wed Jan 06 2021 Frank Tropschuh - 1.0.3-0
- need to supress all output by default for Ansible parsing
- using proxy="" for dnf
- do all processing in init_hook, honor env variables and main yum.conf proxy

