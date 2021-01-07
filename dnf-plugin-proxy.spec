
Name:           dnf-plugin-proxy
Version:        1.0.5
Release:        0%{?dist}
Summary:        Dynamically set the proxy and/or enable/disable repositories
License:        GPLv2+
URL:            https://github.com/gunther788/yum-plugin-proxy
Source0:        proxy.py
Source1:        proxy.conf
BuildArch:      noarch
Provides:       yum-plugin-proxy = %{version}
Obsoletes:      yum-plugin-proxy <= %{version}

%define pluginpath %{python3_sitelib}/dnf-plugins
%define pluginconf /etc/yum/pluginconf.d/proxy.conf


%description
Dynamically set the proxy and/or enable/disable repositories based on various criteria. Processes
the already enabled repositories mid-flight and updates the "enabled" and "proxy" parameters.


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{pluginpath}
install -m644 %{SOURCE0} %{buildroot}%{pluginpath}/proxy.py
find %{buildroot}%{pluginpath}
mkdir -p %{buildroot}/etc/yum/pluginconf.d
install -m644 %{SOURCE1} %{buildroot}%{pluginconf}
exit 0


%files
%defattr(0644,root,root,-)
%{pluginpath}/proxy.py
%config(noreplace) %{pluginconf}


%post
# copy install-time environment variables into the config file, this provides
# a mechanism to automate the installation during kickstart
# if unset, we end up initializing the plugin with all possible variables
egrep -e "^proxy=" %{pluginconf} || echo "proxy=${PROXY_PLUGIN_PROXY}" >> %{pluginconf}
egrep -e "^no_proxy=" %{pluginconf} || echo "no_proxy=${PROXY_PLUGIN_NO_PROXY}" >> %{pluginconf}
egrep -e "^blacklistfiles=" %{pluginconf} || echo "blacklistfiles=${PROXY_PLUGIN_BLACKLISTFILES}" >> %{pluginconf}
exit 0


%changelog
* Thu Jan 07 2021 Frank Tropschuh <gunther@idoru.ch> - 1.0.5-0
- split into yum-plugin-proxy and dnf-plugin-proxy github repos
- several fixes for handling configuration parameters
- %post to initialize config file

* Wed Jan 06 2021 Frank Tropschuh - 1.0.4-1
- onboarded F33, cleanup of python handling
- migrated to github

* Tue Jan 05 2021 Frank Tropschuh - 1.0.2-5
- need to supress all output by default for Ansible parsing
- using proxy="" for dnf

* Mon Jan 04 2021 Frank Tropschuh - 1.0.2-3
- show proxy settings all the time
- need to get the list of repos after config_hook
- skip already disabled plugins

* Mon Jan 04 2021 Frank Tropschuh - 1.0.1-0
- do all processing in init_hook, honor env variables and main yum.conf proxy

* Thu Dec 31 2020 Frank Tropschuh - 1.0.0-3
- initial package
