import sys
import os

# Ensure project root is in Python path (important for Jenkins/CI)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

def test_add():
    with app.test_client() as c:
        rv = c.post("/", data={"a": "2", "b": "3", "op": "add"})
        assert rv.status_code == 200