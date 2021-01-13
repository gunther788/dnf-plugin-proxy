#global commit0 8a763340ac51ff2fcaa2fc3c50e40fd53f2fd1c0
#global date 20210107
#global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global tag 1

%global pluginpath %{python3_sitelib}/dnf-plugins
%global pluginconf %{_sysconfdir}/yum/pluginconf.d

Name:           dnf-plugin-proxy
Version:        1.1.0
Release:        0%{!?tag:.%{date}git%{shortcommit0}}%{?dist}
Summary:        Dynamically set the proxy and/or enable/disable repositories
License:        GPLv2+
URL:            https://github.com/gunther788/dnf-plugin-proxy
BuildArch:      noarch
BuildRequires:  python3-rpm-macros

%if 0%{?tag:1}
Source0:        %{url}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
%else
Source0:        %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%endif

Provides:       yum-plugin-proxy = %{version}-%{release}
Obsoletes:      yum-plugin-proxy <= %{version}-%{release}


%description
Dynamically set the proxy and/or enable/disable repositories based on various
criteria. Processes the already enabled repositories mid-flight and updates the
"enabled" and "proxy" parameters.
Nukes repo files that should not be used when we have internal repositories.


%install
install -m644 -D -p proxy.py   %{buildroot}%{pluginpath}/proxy.py
install -m644 -D -p proxy.conf %{buildroot}%{pluginconf}/proxy.conf


%prep
%if 0%{?tag:1}
%autosetup -p1
%else
%autosetup -p1 -n %{name}-%{commit0}
%endif


%build
# Nothing to build


%files
%license LICENSE
%doc README.md
%{pluginpath}/proxy.py
%if 0%{?rhel} >= 8
%{pluginpath}/__pycache__/proxy.cpython-%{python3_version_nodots}{,.opt-?}.pyc
%endif
%config(noreplace) %ghost %{pluginconf}/proxy.conf


%triggerin -p /usr/bin/bash -- centos-release centos-linux-repos
if [ -f /etc/yum/pluginconf.d/proxy.conf ]; then
    source <(grep = /etc/yum/pluginconf.d/proxy.conf | tr -d " ")
    if [ -n "${blacklistfiles}" ]; then
       for base in $(echo ${blacklistfiles} | tr "," "\n"); do
           echo ">> removing /etc/yum.repos.d/${base}.repo"
       done
    fi
fi


%changelog
* Wed Jan 13 2021 Frank Tropschuh <gunther@idoru.ch> - 1.1.0-0
- add a trigger that removes all repo files in the blacklist

* Thu Jan 07 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.6-2
- including byte-compiled artefacts
- using tags, dropping post again

* Thu Jan 07 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.5-0
- split into yum-plugin-proxy and dnf-plugin-proxy github repos

* Thu Jan 07 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.4-4
- several fixes for handling configuration parameters
- post to initialize config file

* Wed Jan 06 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.4-1
- onboarded F33, cleanup of python handling
- migrated to github

* Tue Jan 05 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.2-5
- need to supress all output by default for Ansible parsing
- using proxy="" for dnf

* Mon Jan 04 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.2-3
- show proxy settings all the time
- need to get the list of repos after config_hook
- skip already disabled plugins

* Mon Jan 04 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.1-0
- do all processing in init_hook, honor env variables and main yum.conf proxy

* Thu Dec 31 2020 Frank Tropschuh <gunther@idoru.ch> - 1.0.0-3
- initial package
