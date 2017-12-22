#/usr/bin/env bash
venv_dir=~/.venvs/restcli

[[ -d ${venv_dir} ]] || python3 -m venv ${venv_dir}
source ${venv_dir}/bin/activate

pip install -r requirements.dev.txt
pip install -r requirements.txt

export PYTHONPATH="$PYTHONPATH:$(pwd)/restcli"
