# -*- coding: utf-8 -*-
import contextlib
import sys
import os
from subprocess import run, CalledProcessError
from pathlib import Path
try:
    import plac
except ModuleNotFoundError:
    print('Installing workflow_script requirments (plac)')
    run(args=[sys.executable, '-m', 'pip', 'install', 'plac'])
    print("\nPLEASE RUN SCRIPT AGAIN")
    sys.exit()


plac.opt('name')
plac.opt('python')
plac.flg('jupyter')
plac.flg('pre_commit')
plac.flg('no_block')
plac.flg('git')


def main(name=None, python='python3.11', jupyter=True, pre_commit=True, no_block=False, git=True):
    if name is None:
        print('Please enter directory name')
        name = input()
        jupyter = yesno("Install jupyter?")
        pre_commit = yesno("Install pre_commit?")
    # TODO: 1.	sudo apt-get install python3-venv

    directory = Path.cwd() / name
    run(['mkdir', directory])
    run(['mkdir', directory / 'src'])
    os.chdir(directory)
    run(['mkdir', Path.home() / 'venvs'])
    run([python, '-m', 'venv', f"{Path.home() / 'venvs' / name}"])
    run(['ln', '-s', f"{Path.home() / 'venvs' / name}",
        f"{directory / 'venv'}"])

    python = directory / 'venv' / 'bin' / 'python'
    pip = directory / 'venv' / 'bin' / 'pip'

    run([pip, 'install', '--upgrade', 'pip'])

    if not no_block:
        while True:
            run(['touch', directory / 'requirements.txt'])
            print('close editor window to proceed')
            try:
                run(['code', '--wait', directory / 'requirements.txt'])
            except FileNotFoundError:
                with contextlib.suppress(FileNotFoundError):
                    run(['nano', directory / 'requirements.txt'])

            try:
                run([pip, 'install', '-r', 'requirements.txt'], check=True)
            except CalledProcessError:
                continue
            else:
                break
    else:
        run([pip, 'install', '-r', 'requirements.txt'])

    with open(directory / '.gitignore', 'w') as gitignore:
        gitignore.write('venv\n')
        gitignore.write('.gitignore\n')
        gitignore.write('.pre-commit-config.yaml\n')
        gitignore.write('.cache\n')

    with open(directory / 'venv.sh', 'w') as venvsh:
        venvsh.write('source ./venv/bin/activate\n')

    if git:
        run(['git', 'init', directory])

    if pre_commit:
        run([pip, 'install', 'pre-commit'])
        pre_commit = directory / 'pre-commit'
        with open(directory / '.pre-commit-config.yaml', 'w') as pre_commit_config_yaml:
            pre_commit_config_yaml.write(pre_commit_config)
        run([python, '-m', 'pre_commit', 'install'])

    if pre_commit and jupyter:
        with open(directory / '.pre-commit-config.yaml', 'a') as pre_commit_config_yaml:
            pre_commit_config_yaml.write(pre_commit_hook_jupytext)

    if jupyter:
        run([pip, 'install', 'jupyter', 'ipython', 'jupytext'])
        ipython = Path.cwd() / 'venv' / 'bin' / 'ipython'
        run([ipython, 'kernel', 'install', '--user', f'--name={name}'])
        with open(directory / 'workbook.ipynb', 'w') as ipython_notebook:
            ipython_notebook.write(jupyter_notebook_template)
        run([python, '-m', 'jupytext', '--set-formats',
            'ipynb,py:percent', 'workbook.ipynb'])

    """
    # TODO: jupytext syncing

    # TODO:  Jupyther
    1. Pasting the following commands into the first field in Jupyther, allows to refere to a python file and the functions in that file are reloaded whenever the file is modified.
    %load_ext autoreload
        %autoreload 2
    3.  This simplies and shortens the error messages (can also go into the first field)
    %xmode Plain
    2. In the second file you need to import the according python fire e.G.
    import src.myfunctions as main
    from src.myfunctions import *  # new functions need to be called with
                        # main.function


    # TODO: tree = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset%n' --abbrev-commit --date=relative --branches --tags

    """
    print('\n\n')
    print('**************************************************************')
    print("*** Activate environment with source './venv/bin/activate' ***")
    print("*** Deactivate environment with 'deactivate'               ***")

    if jupyter:
        print('***                                                        ***')
        print(
            f'*** Please restart VSCode, and select {name} is kernal     ***')

    print('**************************************************************')


pre_commit_config = """# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.2.0
    hooks:
    -   id: trailing-whitespace
        files: '(.*)\.py'
    -   id: end-of-file-fixer
        files: '(.*)\.py'
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-json
    -   id: check-merge-conflict
    -   id: check-xml
    -   id: debug-statements
    -   id: detect-private-key
    -   id: fix-encoding-pragma
    -   id: mixed-line-ending
    -   id: name-tests-test
    -   id: requirements-txt-fixer

-   repo: https://github.com/hhatto/autopep8
    rev: '5b9110b'
    hooks:
    -   id: autopep8

-   repo: https://github.com/pre-commit/mirrors-yapf
    rev: 'v0.32.0'  # Use the sha / tag you want to point at
    hooks:
    -   id: yapf
        args:
        - "--style={based_on_style: pep8, column_limit: 110}"
        additional_dependencies: [toml]

-   repo: https://github.com/pycqa/flake8
    rev: '4.0.1'
    hooks:
    -   id: flake8
        args:
        - --ignore=E501,E122,W503

"""  # noqa

pre_commit_hook_jupytext = """- repo: https://github.com/pycqa/isort
    rev: 5.11.2
    hooks:
    - id: isort
      args: [--treat-comment-as-code, "# %%", --float-to-top]

- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.0.275
  hooks:
    - id: ruff
      args: [--fix, --exit-non-zero-on-fix]

-   repo: https://github.com/mwouts/jupytext
    rev: v1.14.7  # CURRENT_TAG/COMMIT_HASH
    hooks:
    - id: jupytext
      args: [--sync]



"""

jupyter_notebook_template = ("""{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%load_ext autoreload"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "% autoreload 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "% xmode Plain"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  },
  "orig_nbformat": 4
 },
 "nbformat": 4,
 "nbformat_minor": 2
}""").replace('\n', '')


def yesno(text):
    print(f'{text} (y/n)?')
    while True:
        command = input()
        if command in ['Y', 'y', 'Yes', 'yes', 'YES']:
            return True
        elif command in ['N', 'n', 'No', 'no', 'NO']:
            return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        plac.call(main)
    else:
        main()
