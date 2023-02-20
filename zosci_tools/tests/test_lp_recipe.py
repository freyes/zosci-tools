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

import os
import unittest

from unittest import mock

from click.testing import CliRunner

from zosci_tools import lp_recipe


class TestSync(unittest.TestCase):

    def setUp(self):
        self.fake_repo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'fixtures/fake_repo/'))
        self.runner = CliRunner()

    @mock.patch.object(lp_recipe, 'LaunchpadTools')
    def test_unknown_repo(self, LaunchpadTools):

        result = self.runner.invoke(
            lp_recipe.main, ['sync', '--repo-dir', '/tmp/missing-path'],
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Running in dry-run mode', result.output)

    @mock.patch.object(lp_recipe, 'GroupConfig')
    @mock.patch('git.Repo')
    @mock.patch.object(lp_recipe, 'LaunchpadTools')
    def test_repo(self, LaunchpadTools, Repo, GroupConfig):
        git_repo = mock.MagicMock()
        git_repo.git.rev_parse.return_value = self.fake_repo_path
        Repo.return_value = git_repo

        gc = mock.MagicMock()
        GroupConfig.return_value = gc

        charm_project = mock.MagicMock()
        charm_project.lp_project.name = 'charm-fake'
        charm_project.branches = {
            'refs/heads/stable/jammy': {'channels': ['22.04/edge']},
        }
        recipe = mock.MagicMock()
        recipe.name = 'charm-fake.stable-jammy.22.04'
        recipe.web_link = 'https://example.com/charm-fake/%s' % recipe.name
        recipe.auto_build_channels = {}
        recipes = [recipe]
        charm_project.lpt.get_charm_recipes.return_value = recipes
        gc.projects.return_value = [charm_project]
        result = self.runner.invoke(
            lp_recipe.main,
            ['sync', '--repo-dir', self.fake_repo_path],
        )
        print(result.output)
        self.assertIn(
            'Using recipe %s' % recipe.web_link,
            result.output,
        )
        self.assertIn(
            'Updating charmcraft channel from None to 2.0/stable',
            result.output,
        )
        self.assertIn(
            'Dry-run mode: NOT committing the change.',
            result.output,
        )
        self.assertEqual(result.exit_code, 0)
