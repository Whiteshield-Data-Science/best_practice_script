This script installs:
    - a python virtual environment
    - git (default)
    - pre-commit (default)
    - jupyter if jupyter is in given as parameter
    - the git tree command, which displays the commit tree

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