import sys
import os

# Ensure project root is in Python path (important for Jenkins/CI)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, calc

def test_add():
    with app.test_client() as c:
        rv = c.post("/", data={"a": "2", "b": "3", "op": "add"})
        assert rv.status_code == 200

def test_calc_add():
    assert calc("add", 2, 3) == 5

def test_calc_sub():
    assert calc("sub", 5, 2) == 3

def test_calc_div_by_zero():
    try:
        calc("div", 5, 0)
        assert False, "Expected an error"
    except ZeroDivisionError:
        pass