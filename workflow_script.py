# -*- coding: utf-8 -*-
import contextlib
import sys
import os
from subprocess import run, CalledProcessError
from pathlib import Path


def main():
    """ This script installs:
            - a python virtual environment
            - git (default)
            - pre-commit (default)
            - jupyter if jupyter is in given as parameter

        Args:
            first parameter is the name of the new subdirectory with the python project

            second parameter (optional) 'pythonX.XX' for python version (must be installed on system)

            'jupyter' / 'nojupyter' whether to install jupyter

            'pre_commit' / 'nopre_commit' whether to install precommit

            'norequirements', if you dont want to install requirements

            'nogit', to not install git

        Notes:
            The virtual environment is installed in basepath 'venv' (e.G. ~/home/davoud/venv/my_project_name)
            and linked in the project venv subdirectory.


    """
    if flag_in_arguments('help', 'nohelp', default=False) or '-h' in sys.argv:
        print(main.__doc__)
        sys.exit()
    if len(sys.argv) == 1:
        print('Please enter directory name')
    else:
        name = sys.argv[1]

    try:
        python = sys.argv[2] if 'python' in sys.argv[2] else 'python'
    except IndexError:
        python = 'python'

    jupyter = flag_in_arguments(
        'jupyter', 'nojupyter', question="Install jupyter?")
    precommit = flag_in_arguments(
        'precommit', 'noprecommit', question="Install pre_commit?")
    requirements = flag_in_arguments(
        'requirements', 'norequirements', default=True)
    git = flag_in_arguments('git', 'nogit', default=True)

    # TODO: 1.	sudo apt-get install python3-venv

    directory = Path.cwd() / name
    run(['mkdir', directory])
    run(['mkdir', directory / 'src'])
    os.chdir(directory)
    run(['mkdir', Path.home() / 'venvs'])
    if not (Path.home() / 'venvs' / name).exists():
        run([python, '-m', 'venv',
            f"{Path.home() / 'venvs' / name}"], check=True)
    run(['ln', '-s', f"{Path.home() / 'venvs' / name}",
        f"{directory / 'venv'}"])

    python = directory / 'venv' / 'bin' / 'python'
    pip = directory / 'venv' / 'bin' / 'pip'

    run([pip, 'install', '--upgrade', 'pip'])

    if requirements:
        while True:
            run(['touch', directory / 'requirements.txt'])
            print('close editor window to proceed')
            try:
                run(['code', '--wait', directory / 'requirements.txt'], check=True)
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

    with open(directory / 'venv.sh', 'w') as venvsh:
        venvsh.write('source ./venv/bin/activate\n')

    if git:
        run(['git', 'init', directory])
        run(['git', 'config', '--local', '--add', 'alias.tree',
            '''"log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset%n' --abbrev-commit --date=relative --branches --tags"'''])
        with open(directory / '.gitignore', 'w') as gitignore:
            gitignore.write("""venv
                .gitignore
                .pre-commit-config.yaml
                .cache""")

    if precommit:
        run([pip, 'install', 'pre-commit'])
        with open(directory / '.pre-commit-config.yaml', 'w') as pre_commit_config_yaml:
            pre_commit_config_yaml.write(pre_commit_config)
        run([python, '-m', 'pre_commit', 'install'])

    if precommit and jupyter:
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

    print('\n\n')
    print('**************************************************************')
    print("*** Activate environment with source './venv/bin/activate' ***")
    print("*** Deactivate environment with 'deactivate'               ***")
    print('***                                                        ***')
    print("*** git tree command installed                             ***")

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

pre_commit_hook_jupytext = """
-   repo: https://github.com/mwouts/jupytext
    rev: 'v1.14.7'
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
    "%autoreload 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%xmode Plain"
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


def filter_arguments(arguments):
    return [arg.replace('-', '').replace('_', '') for arg in arguments]


def flag_in_arguments(flag, non_flag, default=None, question=None):
    if flag in filter_arguments(sys.argv[1:]):
        return True
    elif non_flag in filter_arguments(sys.argv[1:]):
        return False
    elif default is None:
        return yesno(question)
    else:
        return default


if __name__ == '__main__':
    main()
