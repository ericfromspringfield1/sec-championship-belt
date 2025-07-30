# Ensure that app.py exists in the same directory or adjust the import as needed
from . import app

if __name__ == '__main__':
    app.run(debug=True)
