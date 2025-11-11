import os
import tempfile
import shutil
import pytest

import app as app_module
from werkzeug.security import generate_password_hash

@pytest.fixture()
def client():
    # isolate a temp DB
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, 'test.db')
    app = app_module.app
    app.config['DATABASE'] = db_path
    # Ensure FORCE_SQLITE so no Postgres is attempted
    os.environ['FORCE_SQLITE'] = '1'
    with app.test_client() as client:
        with app.app_context():
            app_module.init_db()
            # seed admin user with known credentials
            db = app_module.get_db()
            db.execute("DELETE FROM users")
            db.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                       ('admin', 'admin@example.com', generate_password_hash('admin123'), 'admin'))
            # seed a product and a customer
            db.execute("INSERT INTO products (name, price, qty, reorder_level) VALUES (?, ?, ?, ?)",
                       ('Block A', 100.0, 50, 5))
            db.execute("INSERT INTO customers (name, email, phone, password, address) VALUES (?, ?, ?, ?, ?)",
                       ('John Doe', 'john@example.com', '123', generate_password_hash('pass'), ''))
            db.commit()
        yield client
    shutil.rmtree(tmpdir)


def login(client):
    return client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)


def test_order_creates_notification(client):
    # login as admin to access admin pages later
    rv = login(client)
    assert rv.status_code == 200
    # Create an order as a logged-in admin on behalf of a customer (route is login_required)
    with app_module.app.app_context():
        db = app_module.get_db()
        cust_id = db.execute("SELECT id FROM customers WHERE email = ?", ('john@example.com',)).fetchone()['id']
        prod_id = db.execute("SELECT id FROM products WHERE name = ?", ('Block A',)).fetchone()['id']
    resp = client.post('/orders/add', data={
        'customer_id': cust_id,
        'product_id': prod_id,
        'qty': 2,
        'account_number': '123-456'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # View notifications
    notif_page = client.get('/admin/notifications')
    assert notif_page.status_code == 200
    assert b'New order #' in notif_page.data
