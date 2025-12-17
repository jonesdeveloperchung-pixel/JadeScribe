import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.getcwd(), path)

if __name__ == "__main__":
    # Point to the internal app.py
    # When bundled, we will make sure src/app.py is in the root or accessible path
    app_path = resolve_path(os.path.join("src", "app.py"))
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
