
import dnf
from urllib.parse import urlparse
import os

verbose = False
proxy = ''
no_proxy = ''
blacklistfiles = []


class Proxy(dnf.Plugin):

    name = "proxy"

    def __init__(self, base, cli):
        """
        Initialize plugin with settings from /etc/yum/pluginconf.d/proxy.conf and the main yum.conf and
        amend with proxy variables from the environment.
        """
        super(Proxy, self).__init__(base, cli)

        global verbose, proxy, no_proxy, blacklistfiles

        conf = self.base.conf

        cp = self.read_config(self.base.conf)
        if cp.has_section('main'):

            # default to global settings if not provided in the plugin settings
            try:
                verbose = (cp.has_option('main', 'verbose') and cp.get('main', 'verbose')) or conf.verbose
            except:
                verbose = False

            try:
                proxy = (cp.has_option('main', 'proxy') and cp.get('main', 'proxy')) or conf.proxy
            except:
                proxy = ''

            try:
                no_proxy = (cp.has_option('main', 'no_proxy') and cp.get('main', 'no_proxy')) or conf.no_proxy
            except:
                no_proxy = ''

            # override with environment variables if currently set
            for e in ['http_proxy','https_proxy']:
                if e in os.environ:
                    if verbose:
                        print('Using "%s" = "%s"' % (e, os.environ[e]))
                    proxy = os.environ[e]

            for e in ['no_proxy']:
                if e in os.environ:
                    if verbose:
                        print('Using "%s" = "%s"' % (e, os.environ[e]))
                    no_proxy = os.environ[e]

            if verbose:
                print('Using proxy "%s", no_proxy "%s"' % (proxy, no_proxy))

            blacklistfileconf = (cp.has_option('main', 'blacklistfiles') and cp.get('main', 'blacklistfiles')) or ''
            blacklistfiles = ['/etc/yum.repos.d/%s.repo' % x.strip() for x in blacklistfileconf.split(',')]
            if verbose:
                print('Blacklist')
                for b in blacklistfiles:
                    print(' * %s' % b)


    def ignore_repo(self, repo):
        """
        Check if the file providing this repo is on the blacklist.
        """

        global blacklistfiles

        return repo.repofile in blacklistfiles


    def in_house_repo(self, repo):
        """
        A repo is considered in-house if the domain matches one of the domains
        listed in "no_proxy".
        """

        global no_proxy

        no_proxies = [x.strip() for x in no_proxy.split(',')]

        for baseurl in repo.baseurl:
            domain = urlparse(baseurl).hostname
            return any([domain.endswith(x) for x in no_proxies])


    def config(self):
        """
        Process each yum repo with the above rules.
        """

        global verbose

        for repo_id, repo in self.base.repos.items():

            # skip if a repo is already disabled anyway
            if bool(repo.enabled) == False:
                if verbose:
                    print('Repo "%s" is already disabled' % (repo.name))

            # if a repo is defined in a repo file that is on the blacklist, disable it
            elif self.ignore_repo(repo):
                if verbose:
                    print('Disabled repo "%s", repo file blacklisted' % (repo.name))
                repo.enabled = False

            # we have no definition of what's in-house or not
            elif no_proxy == '':

                if proxy is not None and proxy.startswith('http'):
                    if verbose:
                        print('Set proxy for "%s"' % (repo.name))
                    repo.proxy = proxy

                else:
                    if verbose:
                        print('Disable proxy for "%s"' % (repo.name))
                    repo.proxy = ''

            # if a repo is hosted internally, make sure proxy is disabled
            elif self.in_house_repo(repo):
                if verbose:
                    print('Ignoring proxy for "%s"' % (repo.name))
                repo.proxy = ''

            # if a repo is not in-house but we have a proxy, use it
            elif proxy is not None and proxy.startswith('http'):
                if verbose:
                    print('Set proxy for "%s", not in-house' % (repo.name))
                repo.proxy = proxy

            # if a repo is not in-house but we don't have a proxy, disable it
            else:
                if verbose:
                    print('Disabled repo "%s", not in-house and missing proxy' % (repo.name))
                repo.enabled = False
