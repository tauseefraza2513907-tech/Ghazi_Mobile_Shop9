# Ghazi Mobile Shop (Streamlit)

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Deploy with GitHub + Streamlit Cloud
1. Create a new GitHub repo and upload all these files.
2. Go to share.streamlit.io, log in with GitHub -> New app -> pick the repo -> Main file: app.py -> Deploy.
3. App settings -> Secrets, add:  ADMIN_PASSWORD = "your-strong-password"
