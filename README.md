# zosci tools

Automation tools for
[zosci](https://github.com/openstack-charmers/zosci-config/)


List of the most relevant commands, for a comprehensive list of arguments pass
the `--help` flag.

* `zosci-lp-recipe sync`, update the Launchpad charm build recipe based on the
  information available in the git repository of the charm.

Environment variables:

| Name                         | Default Value           | Description                                                                                                                                                                                                                                                                                      |
|------------------------------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ZOSCI_TOOLS_CACHE_DIR`      | `~/.cache/zosci-tools/` | Cache dir                                                                                                                                                                                                                                                                                        |
| `DEFAULT_CHARMCRAFT_CHANNEL` | `1.5/stable`            | Charmcraft channel to use in recipe auto build channels map when the osci.yaml file doesn't have an explicit value set.                                                                                                                                                                          |
| `LP_CREDENTIALS_FILE`        |                         | Set this environment variable to a file path where the Launchpad credentials are stored, this is automatically read and used by [launchpadlib](https://help.launchpad.net/API/launchpadlib), it's a convenience to allow backend systems to authenticate without the need of user's interaction. |


## Installation

```bash
pip install git+https://github.com/freyes/zosci-tools.git
```


## Usage Examples

### Syncing Launchpad charm build recipes

```bash
git clone https://opendev.org/openstack/charm-manila-generic
cd charm-manila-generic
zosci-lp-recipe sync  # --i-really-mean-it  # <- flag to commit changes.
```
