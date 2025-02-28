# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
from collections import OrderedDict

import pytest

# Reference:
# https://docs.pytest.org/en/latest/writing_plugins.html#hookwrapper-executing-around-other-hooks
# https://docs.pytest.org/en/latest/writing_plugins.html#hook-function-ordering-call-example
# https://docs.pytest.org/en/stable/reference.html#pytest.hookspec.pytest_runtest_makereport
#
# Inspired by:
# https://github.com/pytest-dev/pytest/blob/master/src/_pytest/terminal.py


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # enable only in a workflow of GitHub Actions
    # ref: https://help.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return

    if report.when == "call" and report.failed:
        # collect information to be annotated
        filesystempath, line_num, _ = report.location

        runpath = os.environ.get("PYTEST_RUN_PATH")
        if runpath:
            filesystempath = os.path.join(runpath, filesystempath)

        # try to convert to absolute path in GitHub Actions
        workspace = os.environ.get("GITHUB_WORKSPACE")
        if workspace:
            full_path = os.path.abspath(filesystempath)
            try:
                rel_path = os.path.relpath(full_path, workspace)
            except ValueError:
                # os.path.relpath() will raise ValueError on Windows
                # when full_path and workspace have different mount points.
                # https://github.com/utgwkk/pytest-github-actions-annotate-failures/issues/20
                rel_path = filesystempath
            if not rel_path.startswith(".."):
                filesystempath = rel_path

        if line_num is not None:
            # 0-index to 1-index
            line_num += 1

        # get the name of the current failed test, with parametrize info
        long_repr = report.head_line or item.name

        # get the error message and line number from the actual error
        try:
            long_repr += "\n\n" + report.longrepr.reprcrash.message
            line_num = report.longrepr.reprcrash.line_num

        except AttributeError:
            pass

        print(
            _error_workflow_command(filesystempath, line_num, long_repr), file=sys.stderr
        )

def _error_workflow_command(filesystempath, line_num, long_repr):
    # Build collection of arguments. Ordering is strict for easy testing
    details_dict = OrderedDict()
    details_dict["file"] = filesystempath
    if line_num is not None:
        details_dict["line"] = line_num

    details = ",".join("{}={}".format(k, v) for k, v in details_dict.items())

    if long_repr is None:
        return "\n::error {}".format(details)
    long_repr = _escape(long_repr)
    return "\n::error {}::{}".format(details, long_repr)


def _escape(s):
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
