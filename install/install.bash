

if [[ ${PWD} != */echoware ]]; then
	echo -e "\033[1;31m[ERROR]\033[1;30m Installer called from wrong directory: ${PWD}"
	return
fi

echo -e "\033[1;33m[INFO]\033[1;30m Installing Echoware"

if [[ ! -f env/bin/activate ]]; then
	echo -e "\033[1;33m[INFO]\033[1;30m Initializing virtual environment"
	python3 -m venv env
fi

source env/bin/activate

pip install --upgrade pip

pip install -r install/requirements.txt