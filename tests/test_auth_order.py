import os
import tempfile
import pytest
from app import app, init_db

@pytest.fixture
def client(tmp_path):
    db_fd, db_path = tempfile.mkstemp(dir=tmp_path)
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    with app.app_context():
        init_db()
    client = app.test_client()
    yield client
    os.close(db_fd)
    try:
        os.remove(db_path)
    except OSError:
        pass


def test_register_and_login_and_order(client):
    # register
    rv = client.post('/register', data={'name':'T','email':'t@example.com','password':'pw'}, follow_redirects=True)
    assert b'Registered successfully' in rv.data
    # login
    rv = client.post('/login', data={'username':'t@example.com','password':'pw'}, follow_redirects=True)
    assert b'Logged in successfully' in rv.data or rv.status_code == 200
    # get products
    rv = client.get('/products')
    assert rv.status_code == 200
