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

import configparser
import logging
import os

import git

from zosci_tools.constants import (
    DEFAULT_BRANCH_NAME,
)


logger = logging.getLogger(__name__)


def get_branch_name(git_repo: git.Repo) -> str:
    """Get branch name from gitreview file.

    The branch name defined in the gitreview file in the 'defaultbranch'
    section is used, if it's not set, then DEFAULT_BRANCH_MASTER is returned.

    :param git_repo: the repo to operate on.
    """
    config = get_gitreview(git_repo)
    try:
        return config['gerrit']['defaultbranch']
    except KeyError:
        return DEFAULT_BRANCH_NAME


def get_gitreview(git_repo: git.Repo) -> configparser.ConfigParser:
    """Get gitreview file content.

    :param git_repo: the repo to operate on.
    :returns: the content of the gitreview file parsed.
    """
    config = configparser.ConfigParser()
    git_root = git_repo.git.rev_parse('--show-toplevel')
    config.read(os.path.join(git_root, '.gitreview'))
    return config
