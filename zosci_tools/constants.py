import os

APP_NAME = 'zosci-tools'
USER_AGENT = os.environ.get('ZOSCI_TOOLS_USER_AGENT', 'zosci-tools/0.1')
CACHE_DIR = os.environ.get('ZOSCI_TOOLS_CACHE_DIR',
                           os.path.expanduser('~/.cache/zosci-tools/'))
OSCI_YAML = 'osci.yaml'
DEFAULT_CHARMCRAFT_CHANNEL = os.environ.get('DEFAULT_CHARMCRAFT_CHANNEL',
                                            '1.5/stable')
DEFAULT_BRANCH_NAME = 'master'
