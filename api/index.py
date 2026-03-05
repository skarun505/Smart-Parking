import os
import sys

# Add the backend directory to the path so imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app

app = create_app()

# Vercel needs the app variable to be exposed
if __name__ == "__main__":
    app.run()
