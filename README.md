# my-vote-backend

This repository contains code for the server-side part of the application.

### [Website](https://front-7.vercel.app/)

### [Google Colab notebook with training code](https://colab.research.google.com/drive/1uYy6426mAx55jy4FWK1xUucn-BHRNJQr?usp=sharing)

### [GitHub repository with front-end code](https://github.com/digital-fracture/my-vote-frontend)

## Run by yourself

### Docker

```shell
docker pull kruase/my-vote-backend
docker run kruase/my-vote-backend
```

### Pipenv

```shell
git clone https://github.com/digital-fracture/my-vote-backend
cd constructor-jobs-backend
pipenv install
pipenv run python3 server.py
```

### Pure python 3.11

Windows (PowerShell) (not tested):
```powershell
git clone https://github.com/digital-fracture/constructor-jobs-backend.git
cd constructor-jobs-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

Linux / MacOS:
```shell
git clone https://github.com/digital-fracture/constructor-jobs-backend.git
cd constructor-jobs-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

## Stack

- [python 3.11](https://python.org/) - programming language
- [FastAPI](https://pypi.org/project/fastapi/) - web server engine
- [PyTorch](https://pypi.org/project/torch/), [catboost](https://pypi.org/project/catboost/), [transformers](https://pypi.org/project/transformers/) - model processing
- [Supabase](https://supabase.com/) - database
- And more
