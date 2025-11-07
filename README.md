# Description

This project is an attempt to create a local infrastructure to run a kubernetes cluster using libvirt. For starters, Bash was chosen as the language to orchestrate it. Then, the main focus shifted to Python for better maintainability and extensibility (and because of YAML temlating needs).

## Run

```bash
    {
        cd python-way/
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        python main.py
    }
```

## Futere improvements

- Move to CLI-styled application using `argparse` or `click` or `typer`.

- Add logging instead of print statements;

- Add unit tests using `unittest` or `pytest`;

- Add configuration file support for `json`;
