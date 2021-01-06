
from yum import config
from urlparse import urlparse
from yum.plugins import TYPE_CORE
import os

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)

proxy = ''
no_proxy = ''
blacklistfiles = []


def init_hook(conduit):
    """
    Initialize plugin with settings from /etc/yum/pluginconf.d/proxy.conf and the main yum.conf and
    amend with proxy variables from the environment.
    """

    global proxy, no_proxy, blacklistfiles

    mainconf = conduit.getConf()
    proxy = conduit.confString('main', 'proxy', default=mainconf.proxy)
    no_proxy = conduit.confString('main', 'no_proxy', default='')
    blacklistfileconf = conduit.confString('main', 'blacklistfiles', default='')
    blacklistfiles = ['/etc/yum.repos.d/%s.repo' % x.strip() for x in blacklistfileconf.split(',')]

    for e in ['http_proxy','https_proxy']:
        if e in os.environ:
            conduit.info(3, 'Using "%s" = "%s"' % (e, os.environ[e]))
            proxy = os.environ[e]

    conduit.info(3, 'Using proxy "%s", no_proxy "%s"' % (proxy, no_proxy))
    conduit.info(3, 'Blacklist')
    for b in blacklistfiles:
        conduit.info(3, ' * %s' % b)


def ignore_repo(repo):
    """
    Check if the file providing this repo is on the blacklist.
    """

    global blacklistfiles

    return repo.repofile in blacklistfiles


def in_house_repo(repo):
    """
    A repo is considered in-house if the domain matches one of the domains
    listed in "no_proxy".
    """

    global no_proxy

    no_proxies = [x.strip() for x in no_proxy.split(',')]

    for baseurl in repo.baseurl:
        domain = urlparse(baseurl).hostname
        return any([domain.endswith(x) for x in no_proxies])


def prereposetup_hook(conduit):
    """
    Process each yum repo with the above rules.o
    """
    
    for repo in conduit.getRepos().listEnabled():

        # if a repo is hosted on Foreman, make sure proxy is disabled
        if in_house_repo(repo):
            conduit.info(3, 'Ignoring proxy for "%s"' % (repo.name))
            repo.proxy = '_none_'

        # if a repo is defined in a repo file that is on the blacklist, disable it
        elif ignore_repo(repo):
            conduit.info(3, 'Disabled repo "%s", repo file blacklisted' % (repo.name))
            repo.enabled = False

        # if a repo is not in-house but we have a proxy, use it
        elif proxy is not None and proxy.startswith('http'):
            conduit.info(3, 'Set proxy for "%s", not in-house' % (repo.name))
            repo.proxy = proxy

        # if a repo is not in-house but we don't have a proxy, disable it
        else:
            conduit.info(3, 'Disabled repo "%s", not in-house and missing proxy' % (repo.name))
            repo.enabled = False
