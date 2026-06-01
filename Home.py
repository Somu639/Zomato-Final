"""Streamlit Community Cloud entry — set Main file to `Home.py`."""

from streamlit_app.app import main

# Must call main() every rerun (importing app.py does NOT re-run main on form submit).
main()
