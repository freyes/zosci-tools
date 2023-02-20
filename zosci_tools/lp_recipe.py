#
# Copyright (C) 2023 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys

import click
import git
import yaml

try:
    from importlib_resources import files, as_file  # type: ignore
except ImportError:
    from importlib.resources import files, as_file  # type: ignore
from charmhub_lp_tools.charm_project import (
    DEFAULT_RECIPE_FORMAT,
)
from charmhub_lp_tools.launchpadtools import (
    LaunchpadTools,
)
from charmhub_lp_tools.main import (
    get_group_config_filenames,
    GroupConfig,
)
from charmhub_lp_tools.parsers import (
    parse_channel,
)
from zosci_tools.constants import (
    DEFAULT_CHARMCRAFT_CHANNEL,
    OSCI_YAML,
)
from zosci_tools.utils import (
    get_branch_name,
)


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def main(ctxt):
    pass


@main.command()
@click.option(
    '--i-really-mean-it',
    default=False,
    help=('This flag must be supplied to indicate that the sync/apply command '
          'really should be used.'),
)
@click.option(
    '--repo-dir',
    default=os.getcwd(),
    help=('Path to charm repository, by default uses the current working '
          'directory'),
)
@click.pass_context
def sync(ctxt, i_really_mean_it, repo_dir):
    if not i_really_mean_it:
        click.echo('Running in dry-run mode...')

    config_dir = files(
        'charmed_openstack_info.data.lp-builder-config'
    )
    lpt = LaunchpadTools()
    gc = GroupConfig(lpt)

    with as_file(config_dir) as cfg_dir:
        lp_builder_configs = get_group_config_filenames(cfg_dir)
        gc.load_files(lp_builder_configs)

    if not list(gc.projects()):
        click.echo('No projects found; '
                   'are you sure the path is correct?: %s', config_dir)
        sys.exit(1)

    git_repo = git.Repo(repo_dir, search_parent_directories=True)
    git_root = git_repo.git.rev_parse('--show-toplevel')
    with open(os.path.join(git_root, OSCI_YAML)) as f:
        osci = yaml.safe_load(f)
    branch_name = get_branch_name(git_repo)

    for section in osci:
        if 'project' not in section:
            continue

        charm_name = section['project']['vars']['charm_build_name']
        if not list(gc.projects(select=[charm_name])):
            click.echo(
                'No charms found; are you sure the arguments are correct'
            )
            sys.exit(1)

        charm_project = list(gc.projects(select=[charm_name]))[0]
        branch = charm_project.branches[f'refs/heads/{branch_name}']
        for channel in branch['channels']:
            (track, risk) = parse_channel(channel)
            recipe_name = DEFAULT_RECIPE_FORMAT.format(
                project=charm_project.lp_project.name,
                branch=branch_name.replace('/', '-'),
                track=track)
            recipes = charm_project.lpt.get_charm_recipes(
                charm_project.lp_team,
                charm_project.lp_project)
            try:
                lp_recipe = [r for r in recipes if r.name == recipe_name][0]
                click.echo('Using recipe %s' % lp_recipe.web_link)
            except IndexError:
                click.echo('Recipe %s not found' % recipe_name)
                sys.exit(2)

            # TODO(freyes): extend this code to handle multiple auto build
            # channels keys.
            try:
                project_vars = section['project']['vars']
                charmcraft_chan = project_vars['charmcraft_channel']
            except KeyError:
                charmcraft_chan = DEFAULT_CHARMCRAFT_CHANNEL

            auto_build_channels = lp_recipe.auto_build_channels
            if auto_build_channels.get('charmcraft') != charmcraft_chan:
                click.echo('Updating charmcraft channel from %s to %s' %
                           (auto_build_channels.get('charmcraft'),
                            charmcraft_chan))
                if i_really_mean_it:
                    auto_build_channels['charmcraft'] = charmcraft_chan
                    lp_recipe.auto_build_channels = auto_build_channels
                    lp_recipe.lp_save()
                else:
                    click.echo('Dry-run mode: NOT committing the change.')
            else:
                click.echo('Recipe auto build channels already in sync')
