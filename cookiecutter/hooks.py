#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cookiecutter.hooks
------------------

Functions for discovering and executing various cookiecutter hooks.
"""

import logging
import os
import sys

PY3 = sys.version > '3'
if PY3:
    import subprocess
else:
    import subprocess32 as subprocess

from .utils import make_sure_path_exists, unicode_open, work_in

_HOOKS = [
    'pre_gen_project',
    'post_gen_project',
    # TODO: other hooks should be listed here
]

def find_hooks():
    '''
    Must be called with the project template as the current working directory.
    Returns a dict of all hook scripts provided.
    Dict's key will be the hook/script's name, without extension, while
    values will be the absolute path to the script.
    Missing scripts will not be included in the returned dict.
    '''
    hooks_dir = 'hooks'
    r = {}
    logging.debug("hooks_dir is {0}".format(hooks_dir))
    if not os.path.isdir(hooks_dir):
        logging.debug("No hooks/ dir in template_dir")
        return r
    for f in os.listdir(hooks_dir):
        basename = os.path.splitext(os.path.basename(f))[0]
        if basename in _HOOKS:
            r[basename] = os.path.abspath(os.path.join(hooks_dir, f))
    return r


def _run_hook(script_path, cwd='.', environ=None):
    '''
    Run a sigle external script located at `script_path` (path should be
    absolute).
    If `cwd` is provided, the script will be run from that directory.
    '''

    if environ is None:
        environ = os.environ.copy()

    # Make sure everything is available even when running from a
    # non-active virtualenv or doing some other weirdness.
    environ["PATH"] = "%s:%s" % (environ["PATH"], os.path.dirname(sys.executable))

    subprocess.call(script_path, cwd=cwd, env=environ)


def run_hook(hook_name, project_dir, context_file=""):
    '''
    Try and find a script mapped to `hook_name` in the current working directory,
    and execute it from `project_dir`.
    '''
    # with work_in(os.path.dirname(project_dir)):
    script = find_hooks().get(hook_name)
    if script is None:
        logging.debug("No hooks found")
        return

    environ = os.environ.copy()
    environ["COOKIECUTTER_CONTEXT_FILE"] = context_file
    return _run_hook(script, project_dir, environ)
