# Sample Hardhat Project

Tools used to run project:
```shell
curl https://get.volta.sh | bash
curl https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile
```

# Install Dependencies
```shell
python3 -m venv ./.venv
source .venv/bin/activate
pip3 install ecdsa fastecdsa sympy
pip3 install cairo-lang
```

# Run Project
```shell
npm ci
npx hardhat compile
```

# Run Demo
```shell
python3 scripts/demo.py
```

### virtual env
```shell
volta install node@18
pyenv install 3.9
```

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a script that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat run scripts/deploy.ts
```

```shell
cairo-compile provable/main.cairo --output provable/main.json
cairo-run --program=provable/main.json --program_input=provable/input.json --print_output --layout small
cairo-hash-program --program=provable/main.json
```

Goerli faucet https://goerli-faucet.pk910.de/
