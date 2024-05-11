## Get Started

1. Create a virtual environment `python -m venv .env`
2. Activate environment For CMD `.\venv\scripts\activate` For bash `source ./.env/Scripts/activate`
3. Install dependencies using pip `python -m pip install -r requirements.txt`


## Setup Markov Chain
1. Use build_markov.py to convert corpus to a model.json file (adjust variables as necessary)
2. The model.json should've been written in a folder under `./models/`
3. Use main.py to run main program (adjust variables and uncomment code blocks as necessary)

## Misc
1. clean.py was used to post-process the raw corpus into text that is easier to convert to a Markov model.
