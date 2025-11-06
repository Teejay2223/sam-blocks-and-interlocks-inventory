import os
import sqlite3
import csv
import io
from datetime import datetime
from flask import (Flask, g, render_template, request, redirect, url_for,
            flash, jsonify)
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-this'
app.config['DATABASE'] = os.path.join(BASE_DIR, 'database.db')

# Startup check: warn if DATABASE_URL is obviously a placeholder so users
# running locally don't get confusing psycopg2 connection errors.
db_url_check = os.environ.get('DATABASE_URL')
if db_url_check and ('<' in db_url_check or '>' in db_url_check):
    app.logger.warning("DATABASE_URL appears to contain placeholder values like '<host>' or '<user>'.\n"
                    "Unset DATABASE_URL or set it to a real Postgres URL to avoid connection errors.")

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --- Database helpers ---
def get_db():
    """Return a DB connection. If DATABASE_URL is set, return a lightweight
    Postgres wrapper (using psycopg2) that exposes an execute()/executescript()
    API compatible with the existing sqlite3 usage. Otherwise return the
    sqlite3.Connection as before.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        return db

    # Allow an explicit override to force SQLite even when DATABASE_URL is set.
    # This is useful while developing locally or if you want to postpone the
    # Postgres migration temporarily. Set FORCE_SQLITE=1 or FORCE_SQLITE=true
    # to force SQLite mode.
    FORCE_SQLITE = os.environ.get('FORCE_SQLITE')
    if FORCE_SQLITE and str(FORCE_SQLITE).lower() in ('1', 'true', 'yes'):
        app.logger.info('FORCE_SQLITE enabled: using local SQLite database regardless of DATABASE_URL')
        DATABASE_URL = None
    else:
        DATABASE_URL = os.environ.get('DATABASE_URL')
    # If DATABASE_URL looks like a placeholder (contains angle-brackets), ignore it so
    # the app falls back to the builtin SQLite DB. This prevents accidental
    # misconfiguration like DATABASE_URL="postgresql://<user>:<pass>@<host>:5432/db"
    if DATABASE_URL:
        if '<' in DATABASE_URL or '>' in DATABASE_URL:
            # treat placeholder as unset
            DATABASE_URL = None
        else:
            # trim whitespace just in case
            DATABASE_URL = DATABASE_URL.strip() or None
    if DATABASE_URL:
        # Lazy import so the app can still run for sqlite-only setups without
        # having psycopg2 installed.
        try:
            import psycopg2
            import psycopg2.extras
        except Exception:
            raise RuntimeError('psycopg2 not installed. Install psycopg2-binary to use Postgres or unset DATABASE_URL.')

        class _PGConn:
            """A tiny wrapper around psycopg2 connection to provide
            .execute() and .executescript() similar to sqlite3.Connection so
            the rest of the app doesn't need massive changes.
            """
            def __init__(self, conn):
                self._conn = conn

            def execute(self, sql, params=()):
                # convert sqlite-style ? placeholders to psycopg2 %s
                sql_conv = sql.replace('?', '%s')
                cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql_conv, params)
                return cur

            def executemany(self, sql, seq_of_params):
                sql_conv = sql.replace('?', '%s')
                cur = self._conn.cursor()
                cur.executemany(sql_conv, seq_of_params)
                return cur

            def executescript(self, script):
                # Execute multiple statements. Split on ';' conservatively.
                cur = self._conn.cursor()
                statements = [s.strip() for s in script.split(';') if s.strip()]
                for stmt in statements:
                    cur.execute(stmt)
                return cur

            def commit(self):
                return self._conn.commit()

            def close(self):
                return self._conn.close()

            def cursor(self):
                return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        conn = psycopg2.connect(DATABASE_URL)
        g._database = _PGConn(conn)
        return g._database

    # default: sqlite3
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    g._database = db
    return db

@app.teardown_appcontext
def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            # some wrappers may not expose close() in the same way
            try:
                db._conn.close()
            except Exception:
                pass

def init_db():
    db = get_db()
    # If using Postgres, use the Postgres schema file; for sqlite keep the existing schema
    # Respect FORCE_SQLITE in init path as well so migrations and schema
    # selection remain consistent with the runtime DB choice.
    FORCE_SQLITE = os.environ.get('FORCE_SQLITE')
    if FORCE_SQLITE and str(FORCE_SQLITE).lower() in ('1', 'true', 'yes'):
        DATABASE_URL_env = None
        app.logger.info('FORCE_SQLITE enabled: init_db will apply SQLite schema and migrations')
    else:
        DATABASE_URL_env = os.environ.get('DATABASE_URL')
    if DATABASE_URL_env:
        if '<' in DATABASE_URL_env or '>' in DATABASE_URL_env:
            DATABASE_URL_env = None
        else:
            DATABASE_URL_env = DATABASE_URL_env.strip() or None
    if DATABASE_URL_env:
        # Postgres: apply schema_pg.sql (contains CREATE TABLE IF NOT EXISTS statements)
        try:
            with open('schema_pg.sql', 'r', encoding='utf-8') as f:
                db.executescript(f.read())
        except Exception:
            pass

        # create demo admin if not exists (upsert style)
        try:
            cur = db.execute("SELECT * FROM users WHERE username = %s", ('admin',))
            if cur.fetchone() is None:
                db.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                        ('admin', 'samventuresblocksinterlocks@gmail.com', generate_password_hash('Sam1991@'), 'admin'))
            db.execute("UPDATE users SET email = %s WHERE username = %s", ('samventuresblocksinterlocks@gmail.com', 'admin'))
            db.commit()
        except Exception:
            pass
        return

    # SQLite path: keep previous behavior and safe PRAGMA-based migrations
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
    except Exception:
        pass

    # ensure `address` column exists on customers (safe migration for existing DBs)
    try:
        cols = [r['name'] for r in db.execute("PRAGMA table_info(customers)").fetchall()]
        if 'address' not in cols:
            db.execute("ALTER TABLE customers ADD COLUMN address TEXT")
    except Exception:
        # If customers table doesn't exist yet or PRAGMA fails, ignore and continue
        pass
    # ensure products have qty and reorder_level column
    try:
        prod_cols = [r['name'] for r in db.execute("PRAGMA table_info(products)").fetchall()]
        if 'qty' not in prod_cols:
            db.execute("ALTER TABLE products ADD COLUMN qty INTEGER DEFAULT 0")
        if 'reorder_level' not in prod_cols:
            db.execute("ALTER TABLE products ADD COLUMN reorder_level INTEGER DEFAULT 0")
    except Exception:
        pass
    # ensure payments has account_number
    try:
        pay_cols = [r['name'] for r in db.execute("PRAGMA table_info(payments)").fetchall()]
        if 'account_number' not in pay_cols:
            db.execute("ALTER TABLE payments ADD COLUMN account_number TEXT")
    except Exception:
        pass
    # ensure sales table has product_id, qty and buyer_name columns
    try:
        sales_cols = [r['name'] for r in db.execute("PRAGMA table_info(sales)").fetchall()]
        if 'product_id' not in sales_cols:
            db.execute("ALTER TABLE sales ADD COLUMN product_id INTEGER")
        if 'qty' not in sales_cols:
            db.execute("ALTER TABLE sales ADD COLUMN qty INTEGER DEFAULT 1")
        if 'buyer_name' not in sales_cols:
            db.execute("ALTER TABLE sales ADD COLUMN buyer_name TEXT")
    except Exception:
        pass

    # create demo admin if not exist
    try:
        cur = db.execute("SELECT * FROM users WHERE username = ?", ('admin',))
        if cur.fetchone() is None:
            db.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    ('admin', 'samventuresblocksinterlocks@gmail.com', generate_password_hash('Sam1991@'), 'admin'))
        db.execute("UPDATE users SET email = ? WHERE username = ?", ('samventuresblocksinterlocks@gmail.com', 'admin'))
    except Exception:
        pass
    db.commit()

    # ensure breakages table exists
    try:
        db.execute('''
            CREATE TABLE IF NOT EXISTS breakages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                reason TEXT,
                reported_by TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
    except Exception:
        pass
    
    # ensure ledger table exists
    try:
        db.execute('''
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                qty_in INTEGER DEFAULT 0,
                qty_out INTEGER DEFAULT 0,
                amount REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        ''')
    except Exception:
        pass
    # ensure audit log table exists
    try:
        db.execute('''
            CREATE TABLE IF NOT EXISTS product_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                user TEXT,
                action TEXT,
                field TEXT,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except Exception:
        pass
    # generic audit table for other entities (trips, sales edits, etc.)
    try:
        db.execute('''
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity TEXT,
                entity_id INTEGER,
                user TEXT,
                action TEXT,
                field TEXT,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except Exception:
        pass


# Run migrations before first request so existing DBs are updated when app is started via flask run
@app.before_request
def ensure_migrations():
    try:
        init_db()
    except Exception:
        # swallow errors here; init_db already tries safe PRAGMA checks
        pass

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print("Initialized the database.")


# Inject the active DB backend into templates for a small UI banner.
@app.context_processor
def inject_db_backend():
    """Provide `db_backend` to templates: 'SQLite', 'SQLite (forced)', or 'Postgres'.

    This inspects the same environment flags used by `get_db()` so the banner
    matches the actual runtime choice.
    """
    FORCE_SQLITE = os.environ.get('FORCE_SQLITE')
    if FORCE_SQLITE and str(FORCE_SQLITE).lower() in ('1', 'true', 'yes'):
        return {'db_backend': 'SQLite (forced)'}
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and '<' not in DATABASE_URL and '>' not in DATABASE_URL and DATABASE_URL.strip():
        return {'db_backend': 'Postgres'}
    return {'db_backend': 'SQLite'}

# --- User Model for flask-login ---
class User(UserMixin):
    def __init__(self, id_, username, email, role='customer'):
        self.id = id_
        self.username = username
        self.email = email
        self.role = role or 'customer'


@login_manager.user_loader
def load_user(user_id):
    """Load a user by id. Try users table first, then customers table.

    Returns a User or None.
    """
    try:
        db = get_db()
    except Exception:
        return None

    # try users table
    row = db.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
    if row:
        cols = row.keys()
        username = row['username'] if 'username' in cols and row['username'] else ''
        email = row['email'] if 'email' in cols and row['email'] else ''
        role = row['role'] if 'role' in cols and row['role'] else 'admin'
        return User(row['id'], username, email, role)

    # fallback to customers table (if customers are allowed to login)
    row2 = db.execute("SELECT * FROM customers WHERE id = ?", (int(user_id),)).fetchone()
    if row2:
        cols2 = row2.keys()
        username = row2['name'] if 'name' in cols2 and row2['name'] else ''
        email = row2['email'] if 'email' in cols2 and row2['email'] else ''
        role = row2['role'] if 'role' in cols2 and row2['role'] else 'customer'
        return User(row2['id'], username, email, role)

    return None


# Restrict customers to a small set of pages
@app.before_request
def restrict_customer_routes():
    # endpoints customers are allowed to access
    allowed_for_customer = {'products', 'notes', 'add_order', 'login', 'logout', 'register', 'ping', 'static'}
    try:
        if current_user.is_authenticated and getattr(current_user, 'role', '').lower() == 'customer':
            endpoint = (request.endpoint or '')
            # allow static resources
            if endpoint is None:
                return None
            if endpoint.startswith('static'):
                return None
            if endpoint not in allowed_for_customer:
                # redirect customers to products page if they try to access other pages
                return redirect(url_for('products'))
    except Exception:
        # if current_user isn't available (e.g., before login manager setup), ignore
        pass

# --- Utility decorator for admin-only routes ---
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.lower() != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# --- Routes ---
@app.route('/')
def index():
    # Show welcome page for anonymous users
    if not current_user.is_authenticated:
        return render_template('welcome.html')
    
    # if a customer is logged in, send them to their dashboard
    try:
        if getattr(current_user, 'role', '').lower() == 'customer':
            return redirect(url_for('customer_dashboard'))
    except Exception:
        pass
    
    # Admin dashboard: show quick stats
    db = get_db()
    total_products = db.execute('SELECT COUNT(*) AS c FROM products').fetchone()['c']
    total_orders = db.execute('SELECT COUNT(*) AS c FROM orders').fetchone()['c']
    total_customers = db.execute('SELECT COUNT(*) AS c FROM customers').fetchone()['c']
    return render_template('index.html', total_products=total_products,
                           total_orders=total_orders, total_customers=total_customers)

# Auth: login/register/logout
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        # allow login using username OR email for users, otherwise check customers by email
        row = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()
        if not row:
            row = db.execute("SELECT * FROM customers WHERE email = ?", (username,)).fetchone()
        if row and check_password_hash(row['password'], password):
            # sqlite3.Row doesn't implement dict.get, so access columns safely
            cols = row.keys()
            username_val = row['username'] if 'username' in cols and row['username'] else (row['name'] if 'name' in cols and row['name'] else '')
            email_val = row['email'] if 'email' in cols and row['email'] else ''
            role_val = row['role'] if 'role' in cols and row['role'] else 'customer'
            user = User(row['id'], username_val, email_val, role_val)
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        password = generate_password_hash(request.form['password'])
        db = get_db()
        existing = db.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
        if existing:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        # insert with address column (migration ensures column exists)
        db.execute("INSERT INTO customers (name, email, phone, password, address) VALUES (?, ?, ?, ?, ?)",
                   (name, email, phone, password, address))
        db.commit()
        flash('Registered successfully, please log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

# Products - list for customers
@app.route('/products')
def products():
    db = get_db()
    prods = db.execute("SELECT * FROM products").fetchall()
    return render_template('products.html', products=prods)

# Admin manage products
@app.route('/admin/products', methods=['GET','POST'])
@login_required
@admin_required
def admin_products():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form.get('description','')
        size = request.form.get('size','')
        price = float(request.form.get('price',0))
        qty = int(request.form.get('qty', 0) or 0)
        reorder = int(request.form.get('reorder_level', 0) or 0)
        db.execute("INSERT INTO products (name, description, size, price, qty, reorder_level) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, desc, size, price, qty, reorder))
        db.commit()
        flash('Product added', 'success')
        return redirect(url_for('admin_products'))
    prods = db.execute("SELECT * FROM products").fetchall()
    return render_template('admin/products_manage.html', products=prods)


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    db = get_db()
    # KPIs
    total_products = db.execute("SELECT COUNT(*) as c FROM products").fetchone()['c']
    total_customers = db.execute("SELECT COUNT(*) as c FROM customers").fetchone()['c']
    total_sales = db.execute("SELECT COUNT(*) as c FROM sales").fetchone()['c']
    pending_payments = db.execute("SELECT COUNT(*) as c FROM payments WHERE status = 'Pending'").fetchone()['c']
    
    # Financial KPIs
    total_revenue = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM sales").fetchone()['total']
    total_expenses = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM trips").fetchone()['total']
    pending_payment_amount = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = 'Pending'").fetchone()['total']
    ledger_balance = db.execute("SELECT balance FROM ledger ORDER BY date DESC, id DESC LIMIT 1").fetchone()
    current_balance = ledger_balance['balance'] if ledger_balance else 0
    
    # Sales trend data (last 7 days)
    sales_trend = db.execute("""
        SELECT sale_date, SUM(amount) as total 
        FROM sales 
        WHERE sale_date >= date('now', '-7 days')
        GROUP BY sale_date 
        ORDER BY sale_date
    """).fetchall()
    
    # Top selling products (last 30 days)
    top_products = db.execute("""
        SELECT p.name, SUM(s.qty) as total_qty, SUM(s.amount) as total_amount
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.sale_date >= date('now', '-30 days')
        GROUP BY p.id, p.name
        ORDER BY total_qty DESC
        LIMIT 5
    """).fetchall()
    
    # Recent orders
    recent_orders = db.execute("""
        SELECT o.id, o.order_date, o.status, o.total, c.name as customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.order_date DESC
        LIMIT 5
    """).fetchall()
    
    # low stock products (qty <= reorder_level)
    low_products = db.execute("SELECT id, name, qty, reorder_level FROM products WHERE qty <= reorder_level ORDER BY qty ASC").fetchall()
    # low raw materials
    low_materials = db.execute("SELECT id, name, qty, reorder_level FROM raw_materials WHERE qty <= reorder_level ORDER BY qty ASC").fetchall()
    
    return render_template('admin/dashboard.html', 
                        total_products=total_products, 
                        total_customers=total_customers,
                        total_sales=total_sales, 
                        pending_payments=pending_payments,
                        total_revenue=total_revenue,
                        total_expenses=total_expenses,
                        pending_payment_amount=pending_payment_amount,
                        current_balance=current_balance,
                        sales_trend=sales_trend,
                        top_products=top_products,
                        recent_orders=recent_orders,
                        low_products=low_products, 
                        low_materials=low_materials)


# --- CSV export/import for products
@app.route('/admin/products/export')
@login_required
@admin_required
def admin_products_export():
    db = get_db()
    rows = db.execute('SELECT id, name, size, price, qty, reorder_level, description FROM products').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','name','size','price','qty','reorder_level','description'])
    for r in rows:
        cols = r.keys()
        price = r['price'] if 'price' in cols and r['price'] is not None else 0
        qty = r['qty'] if 'qty' in cols and r['qty'] is not None else 0
        reorder = r['reorder_level'] if 'reorder_level' in cols and r['reorder_level'] is not None else 0
        desc = r['description'] if 'description' in cols and r['description'] is not None else ''
        writer.writerow([r['id'], r['name'], r['size'], price, qty, reorder, desc])
    resp = app.response_class(output.getvalue(), mimetype='text/csv')
    resp.headers.set('Content-Disposition', 'attachment', filename='products.csv')
    return resp


@app.route('/admin/products/import', methods=['GET','POST'])
@login_required
@admin_required
def admin_products_import():
    db = get_db()
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin_products'))
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        changed = 0
        for row in reader:
            # prefer id matching, else try name
            pid = row.get('id')
            try:
                pid = int(pid) if pid else None
            except Exception:
                pid = None
            if pid:
                existing = db.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
            else:
                existing = db.execute('SELECT * FROM products WHERE name = ?', (row.get('name'),)).fetchone()
            if existing:
                updates = {}
                reason = 'import'
                # fields: price, qty, reorder_level
                for fkey in ('price','qty','reorder_level','description','size','name'):
                    if fkey in row and row[fkey] != '' and row[fkey] is not None:
                        val = row[fkey]
                        # cast numeric fields
                        if fkey in ('price',):
                            try:
                                val = float(val)
                            except Exception:
                                continue
                        if fkey in ('qty','reorder_level'):
                            try:
                                val = int(float(val))
                            except Exception:
                                continue
                        updates[fkey] = val
                if updates:
                    # perform update and log audits per changed field
                    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
                    params = list(updates.values()) + [existing['id']]
                    db.execute(f'UPDATE products SET {set_clause} WHERE id = ?', params)
                    user = getattr(current_user, 'username', None) or getattr(current_user, 'email', None) or 'unknown'
                    for k, v in updates.items():
                        # existing is sqlite3.Row — use keys() to access safely
                        ek = existing.keys()
                        oldv = existing[k] if k in ek else None
                        try:
                            db.execute('INSERT INTO product_audit (product_id, user, action, field, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                    (existing['id'], user, 'import_update', k, str(oldv), str(v), reason))
                        except Exception:
                            pass
                    changed += 1
        db.commit()
        flash(f'Import completed, {changed} rows updated', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/products_import.html')


@app.route('/admin/routes')
@login_required
@admin_required
def admin_routes():
    # show all routes for debugging/discovery
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join(sorted(rule.methods - {'HEAD','OPTIONS'}))
        routes.append({'rule': rule.rule, 'endpoint': rule.endpoint, 'methods': methods})
    return render_template('admin/routes.html', routes=routes)


@app.route('/admin/audit')
@login_required
@admin_required
def admin_audit():
    db = get_db()
    # filters: product_id, user, field, date range
    product_id = request.args.get('product_id')
    user = request.args.get('user','').strip()
    field = request.args.get('field','').strip()
    start = request.args.get('start')
    end = request.args.get('end')

    # Fetch product_audit entries
    p_params = []
    p_where = []
    p_sql = 'SELECT pa.id, "products" as entity, pa.product_id as entity_id, pa.user, pa.action, pa.field, pa.old_value, pa.new_value, pa.reason, pa.timestamp, p.name as entity_name FROM product_audit pa LEFT JOIN products p ON pa.product_id = p.id'
    if product_id:
        p_where.append('pa.product_id = ?')
        p_params.append(product_id)
    if user:
        p_where.append('pa.user LIKE ?')
        p_params.append(f'%{user}%')
    if field:
        p_where.append('pa.field = ?')
        p_params.append(field)
    if start:
        p_where.append("date(pa.timestamp) >= date(?)")
        p_params.append(start)
    if end:
        p_where.append("date(pa.timestamp) <= date(?)")
        p_params.append(end)
    if p_where:
        p_sql += ' WHERE ' + ' AND '.join(p_where)

    # Fetch generic audit entries
    a_params = []
    a_where = []
    a_sql = 'SELECT a.id, a.entity, a.entity_id, a.user, a.action, a.field, a.old_value, a.new_value, a.reason, a.timestamp FROM audit a'
    if product_id:
        # if product_id provided, limit to audits for products with that id
        a_where.append("a.entity = 'products' AND a.entity_id = ?")
        a_params.append(product_id)
    if user:
        a_where.append('a.user LIKE ?')
        a_params.append(f'%{user}%')
    if field:
        a_where.append('a.field = ?')
        a_params.append(field)
    if start:
        a_where.append("date(a.timestamp) >= date(?)")
        a_params.append(start)
    if end:
        a_where.append("date(a.timestamp) <= date(?)")
        a_params.append(end)
    if a_where:
        a_sql += ' WHERE ' + ' AND '.join(a_where)

    # execute both queries and combine results in Python, then sort by timestamp desc
    rows_combined = []
    try:
        p_rows = db.execute(p_sql, p_params).fetchall()
        for r in p_rows:
            rows_combined.append({
                'id': r['id'], 'entity': 'products', 'entity_id': r['entity_id'], 'user': r['user'],
                'action': r['action'], 'field': r['field'], 'old_value': r['old_value'], 'new_value': r['new_value'],
                'reason': r['reason'], 'timestamp': r['timestamp'], 'entity_name': r['entity_name']
            })
    except Exception:
        pass
    try:
        a_rows = db.execute(a_sql, a_params).fetchall()
        # try to fetch a human-friendly name for some entities
        for r in a_rows:
            name = None
            try:
                if r['entity'] == 'products':
                    p = db.execute('SELECT name FROM products WHERE id = ?', (r['entity_id'],)).fetchone()
                    name = p['name'] if p else None
                elif r['entity'] == 'trips':
                    t = db.execute('SELECT vehicle_no FROM trips WHERE id = ?', (r['entity_id'],)).fetchone()
                    name = t['vehicle_no'] if t else None
            except Exception:
                name = None
            rows_combined.append({
                'id': r['id'], 'entity': r['entity'], 'entity_id': r['entity_id'], 'user': r['user'],
                'action': r['action'], 'field': r['field'], 'old_value': r['old_value'], 'new_value': r['new_value'],
                'reason': r['reason'], 'timestamp': r['timestamp'], 'entity_name': name
            })
    except Exception:
        pass

    # sort by timestamp desc
    try:
        rows_combined.sort(key=lambda x: x.get('timestamp') or '', reverse=True)
    except Exception:
        pass

    # limit to 500
    rows_combined = rows_combined[:500]

    products = db.execute('SELECT id, name FROM products').fetchall()
    return render_template('admin/audit.html', audits=rows_combined, products=products)


@app.route('/admin/reconciliation', methods=['GET','POST'])
@login_required
@admin_required
def admin_reconciliation():
    db = get_db()
    # default: today
    start = request.values.get('start')
    end = request.values.get('end')
    if not start:
        # default to today
        start = datetime.utcnow().date().isoformat()
    if not end:
        end = start

    # gather per-product totals
    prods = db.execute('SELECT id, name, qty FROM products').fetchall()
    result = []
    for p in prods:
        pid = p['id']
        current_qty = int(p['qty'] or 0)
        sold_row = db.execute("SELECT SUM(qty) as s FROM sales WHERE date(sale_date) BETWEEN date(?) AND date(?) AND product_id = ?", (start, end, pid)).fetchone()
        sold = int(sold_row['s'] or 0)
        broken_row = db.execute("SELECT SUM(qty) as b FROM breakages WHERE date(date) BETWEEN date(?) AND date(?) AND product_id = ?", (start, end, pid)).fetchone()
        broken = int(broken_row['b'] or 0)
        # adjustments from audit for field 'qty' during period: sum(new-old)
        adj_rows = db.execute("SELECT old_value, new_value FROM product_audit WHERE field = 'qty' AND date(timestamp) BETWEEN date(?) AND date(?) AND product_id = ?", (start, end, pid)).fetchall()
        adjustments = 0
        for ar in adj_rows:
            try:
                oldv = int(float(ar['old_value']))
            except Exception:
                oldv = 0
            try:
                newv = int(float(ar['new_value']))
            except Exception:
                newv = 0
            adjustments += (newv - oldv)
        # opening = current + sold + broken - adjustments
        opening = current_qty + sold + broken - adjustments
        closing = opening - sold - broken + adjustments
        result.append({'id': pid, 'name': p['name'], 'opening': opening, 'sold': sold, 'broken': broken, 'adjustments': adjustments, 'closing': closing, 'current': current_qty})

    return render_template('admin/reconciliation.html', result=result, start=start, end=end)

@app.route('/admin/products/delete/<int:pid>', methods=['POST'])
@login_required
@admin_required
def admin_product_delete(pid):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (pid,))
    db.commit()
    flash('Product deleted', 'info')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/adjust/<int:pid>', methods=['POST'])
@login_required
@admin_required
def admin_product_adjust(pid):
    db = get_db()
    try:
        delta = int(request.form.get('delta', 0))
    except Exception:
        delta = 0
    reason = request.form.get('reason','')
    # fetch old qty
    row = db.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
    if not row:
        flash('Product not found', 'warning')
        return redirect(url_for('admin_products'))
    old_qty = int(row['qty'] or 0)
    new_qty = old_qty + delta
    db.execute('UPDATE products SET qty = ? WHERE id = ?', (new_qty, pid))
    # audit
    try:
        user = getattr(current_user, 'username', None) or getattr(current_user, 'email', None) or 'unknown'
        db.execute('INSERT INTO product_audit (product_id, user, action, field, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (pid, user, 'adjust', 'qty', str(old_qty), str(new_qty), reason))
    except Exception:
        pass
    db.commit()
    flash('Stock adjusted', 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/products/edit/<int:pid>', methods=['GET','POST'])
@login_required
@admin_required
def admin_product_edit(pid):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form.get('description','')
        size = request.form.get('size','')
        price = float(request.form.get('price',0))
        qty = int(request.form.get('qty', 0) or 0)
        reorder = int(request.form.get('reorder_level', 0) or 0)
        # fetch old values for audit
        old = db.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
        old_vals = {}
        if old:
            cols = old.keys()
            old_vals = {
                'name': old['name'] if 'name' in cols and old['name'] is not None else '',
                'description': old['description'] if 'description' in cols and old['description'] is not None else '',
                'size': old['size'] if 'size' in cols and old['size'] is not None else '',
                'price': old['price'] if 'price' in cols else 0,
                'qty': old['qty'] if 'qty' in cols else 0,
                'reorder_level': old['reorder_level'] if 'reorder_level' in cols else 0,
            }

        db.execute('UPDATE products SET name = ?, description = ?, size = ?, price = ?, qty = ?, reorder_level = ? WHERE id = ?',
                   (name, desc, size, price, qty, reorder, pid))

        # record audit entries for changed fields
        def _log(field, oldv, newv, reason=''):
            try:
                user = getattr(current_user, 'username', None) or getattr(current_user, 'email', None) or 'unknown'
                db.execute('INSERT INTO product_audit (product_id, user, action, field, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (pid, user, 'update', field, str(oldv), str(newv), reason))
            except Exception:
                pass

        if old:
            if str(old_vals.get('price')) != str(price):
                _log('price', old_vals.get('price'), price, request.form.get('reason',''))
            if int(old_vals.get('qty') or 0) != int(qty):
                _log('qty', old_vals.get('qty'), qty, request.form.get('reason',''))
            if int(old_vals.get('reorder_level') or 0) != int(reorder):
                _log('reorder_level', old_vals.get('reorder_level'), reorder, request.form.get('reason',''))
            if (old_vals.get('name') or '') != (name or ''):
                _log('name', old_vals.get('name'), name, request.form.get('reason',''))
            if (old_vals.get('description') or '') != (desc or ''):
                _log('description', old_vals.get('description'), desc, request.form.get('reason',''))

        db.commit()
        flash('Product updated', 'success')
        return redirect(url_for('admin_products'))
    row = db.execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
    if not row:
        flash('Product not found', 'warning')
        return redirect(url_for('admin_products'))
    return render_template('admin/products_edit.html', product=row)

# Orders: customer places order (simple single-product order for demo)
@app.route('/orders/add', methods=['GET','POST'])
@login_required
def add_order():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    customers = db.execute("SELECT * FROM customers").fetchall()
    if request.method == 'POST':
        customer_id = int(request.form['customer_id'])
        product_id = int(request.form['product_id'])
        qty = int(request.form['qty'])
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        unit_price = product['price']
        # check inventory qty if available
        available = product['qty'] if 'qty' in product.keys() else None
        if available is not None and qty > available:
            flash(f'Requested quantity ({qty}) exceeds available stock ({available}).', 'danger')
            return redirect(url_for('add_order'))
        total = unit_price * qty

        db.execute("INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
                   (customer_id, total, 'Pending'))
        db.commit()
        order_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']
        db.execute("INSERT INTO order_items (order_id, product_id, qty, unit_price) VALUES (?, ?, ?, ?)",
                   (order_id, product_id, qty, unit_price))
        # create payment entry pending
        account_number = request.form.get('account_number', '')
        db.execute("INSERT INTO payments (order_id, amount, status, account_number) VALUES (?, ?, ?, ?)",
                   (order_id, total, 'Pending', account_number))
        # decrement product qty if tracked
        try:
            if 'qty' in product.keys():
                db.execute("UPDATE products SET qty = qty - ? WHERE id = ?", (qty, product_id))
        except Exception:
            pass
        db.commit()
        flash('Order created (Payment Pending).', 'success')
        return redirect(url_for('orders_list'))
    return render_template('orders_add.html', products=products, customers=customers)


# --- Admin: raw materials CRUD ---
@app.route('/admin/raw_materials', methods=['GET','POST'])
@login_required
@admin_required
def admin_raw_materials():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        qty = float(request.form.get('qty', 0))
        reorder = float(request.form.get('reorder_level', 0))
        db.execute("INSERT INTO raw_materials (name, qty, reorder_level) VALUES (?, ?, ?)", (name, qty, reorder))
        db.commit()
        flash('Raw material added', 'success')
        return redirect(url_for('admin_raw_materials'))
    rows = db.execute('SELECT * FROM raw_materials').fetchall()
    return render_template('admin/raw_materials_manage.html', materials=rows)


@app.route('/admin/raw_materials/edit/<int:mid>', methods=['GET','POST'])
@login_required
@admin_required
def admin_raw_materials_edit(mid):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        qty = float(request.form.get('qty', 0))
        reorder = float(request.form.get('reorder_level', 0))
        db.execute('UPDATE raw_materials SET name = ?, qty = ?, reorder_level = ? WHERE id = ?', (name, qty, reorder, mid))
        db.commit()
        flash('Raw material updated', 'success')
        return redirect(url_for('admin_raw_materials'))
    row = db.execute('SELECT * FROM raw_materials WHERE id = ?', (mid,)).fetchone()
    return render_template('admin/raw_materials_edit.html', material=row)


@app.route('/admin/raw_materials/delete/<int:mid>', methods=['POST'])
@login_required
@admin_required
def admin_raw_materials_delete(mid):
    db = get_db()
    db.execute('DELETE FROM raw_materials WHERE id = ?', (mid,))
    db.commit()
    flash('Raw material deleted', 'info')
    return redirect(url_for('admin_raw_materials'))


# --- Admin: sales CRUD ---
@app.route('/admin/sales', methods=['GET','POST'])
@login_required
@admin_required
def admin_sales():
    db = get_db()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        qty = int(request.form['qty'])
        amount = float(request.form['amount'])
        buyer_name = request.form.get('buyer_name','').strip()
        sale_date = request.form.get('sale_date') or datetime.utcnow().date().isoformat()
        db.execute('INSERT INTO sales (sale_date, amount, product_id, qty, buyer_name) VALUES (?, ?, ?, ?, ?)', (sale_date, amount, product_id, qty, buyer_name))
        # decrement product qty
        db.execute('UPDATE products SET qty = qty - ? WHERE id = ?', (qty, product_id))
        db.commit()
        flash('Sale recorded', 'success')
        return redirect(url_for('admin_sales'))
    # simple search and pagination
    q = request.args.get('q','').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    params = []
    sql = 'SELECT s.*, p.name as product_name FROM sales s LEFT JOIN products p ON s.product_id = p.id'
    if q:
        sql += ' WHERE p.name LIKE ?'
        params.append(f'%{q}%')
    sql += ' ORDER BY s.sale_date DESC LIMIT ? OFFSET ?'
    params.extend((per_page, (page-1)*per_page))
    rows = db.execute(sql, params).fetchall()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('admin/sales_manage.html', sales=rows, products=products, q=q, page=page)


@app.route('/admin/sales/edit/<int:sid>', methods=['GET','POST'])
@login_required
@admin_required
def admin_sales_edit(sid):
    db = get_db()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        qty = int(request.form['qty'])
        amount = float(request.form['amount'])
        buyer_name = request.form.get('buyer_name','').strip()
        sale_date = request.form.get('sale_date') or datetime.utcnow().date().isoformat()
        # fetch old sale to adjust inventory
        old = db.execute('SELECT * FROM sales WHERE id = ?', (sid,)).fetchone()
        if old:
            old_qty = old['qty'] or 0
            old_pid = old['product_id']
            # restore old qty then deduct new qty
            if old_pid:
                db.execute('UPDATE products SET qty = qty + ? WHERE id = ?', (old_qty, old_pid))
        db.execute('UPDATE sales SET sale_date = ?, amount = ?, product_id = ?, qty = ?, buyer_name = ? WHERE id = ?', (sale_date, amount, product_id, qty, buyer_name, sid))
        db.execute('UPDATE products SET qty = qty - ? WHERE id = ?', (qty, product_id))
        db.commit()
        flash('Sale updated', 'success')
        return redirect(url_for('admin_sales'))
    row = db.execute('SELECT * FROM sales WHERE id = ?', (sid,)).fetchone()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('admin/sales_edit.html', sale=row, products=products)


@app.route('/admin/sales/delete/<int:sid>', methods=['POST'])
@login_required
@admin_required
def admin_sales_delete(sid):
    db = get_db()
    row = db.execute('SELECT * FROM sales WHERE id = ?', (sid,)).fetchone()
    if row and row['product_id']:
        db.execute('UPDATE products SET qty = qty + ? WHERE id = ?', (row['qty'] or 0, row['product_id']))
    db.execute('DELETE FROM sales WHERE id = ?', (sid,))
    db.commit()
    flash('Sale deleted', 'info')
    return redirect(url_for('admin_sales'))


# --- Admin: breakages CRUD (record damaged/broken blocks)
@app.route('/admin/breakages', methods=['GET','POST'])
@login_required
@admin_required
def admin_breakages():
    db = get_db()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        qty = int(request.form['qty'])
        reason = request.form.get('reason','')
        reported_by = request.form.get('reported_by','')
        date = request.form.get('date') or datetime.utcnow().isoformat()
        db.execute('INSERT INTO breakages (product_id, qty, reason, reported_by, date) VALUES (?, ?, ?, ?, ?)', (product_id, qty, reason, reported_by, date))
        # decrement product stock to account for breakage
        db.execute('UPDATE products SET qty = qty - ? WHERE id = ?', (qty, product_id))
        db.commit()
        flash('Breakage recorded and stock adjusted', 'success')
        return redirect(url_for('admin_breakages'))
    # list breakages
    rows = db.execute('SELECT b.*, p.name as product_name FROM breakages b LEFT JOIN products p ON b.product_id = p.id ORDER BY b.date DESC').fetchall()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template('admin/breakages_manage.html', breakages=rows, products=products)


@app.route('/admin/breakages/delete/<int:bid>', methods=['POST'])
@login_required
@admin_required
def admin_breakages_delete(bid):
    db = get_db()
    row = db.execute('SELECT * FROM breakages WHERE id = ?', (bid,)).fetchone()
    if row:
        # restore stock when deleting a breakage record
        db.execute('UPDATE products SET qty = qty + ? WHERE id = ?', (row['qty'] or 0, row['product_id']))
        db.execute('DELETE FROM breakages WHERE id = ?', (bid,))
        db.commit()
        flash('Breakage entry removed and stock restored', 'info')
    return redirect(url_for('admin_breakages'))


# Admin: customers list
@app.route('/admin/customers')
@login_required
@admin_required
def admin_customers():
    db = get_db()
    # simple search and pagination
    q = request.args.get('q','').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    params = []
    sql = 'SELECT * FROM customers'
    if q:
        sql += ' WHERE name LIKE ? OR email LIKE ?'
        params.extend((f'%{q}%', f'%{q}%'))
    sql += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    params.extend((per_page, (page-1)*per_page))
    rows = db.execute(sql, params).fetchall()
    return render_template('admin/customers_list.html', customers=rows, q=q, page=page)


# Customer-facing: my orders and payments
@app.route('/my/orders')
@login_required
def my_orders():
    db = get_db()
    # if current_user is admin, show all orders; else show only their orders (customers use email to match)
    if getattr(current_user, 'role', '').lower() == 'admin':
        rows = db.execute('SELECT * FROM orders ORDER BY order_date DESC').fetchall()
    else:
        # find customer id by email
        customer = db.execute('SELECT * FROM customers WHERE email = ?', (current_user.email,)).fetchone()
        if not customer:
            flash('No customer record found for your account', 'warning')
            return redirect(url_for('products'))
        rows = db.execute('SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC', (customer['id'],)).fetchall()
    # fetch items per order
    orders = []
    for o in rows:
        items = db.execute('SELECT oi.qty, p.name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?', (o['id'],)).fetchall()
        orders.append({'id': o['id'], 'order_date': o['order_date'], 'total': o['total'], 'status': o['status'], 'items': items})
    return render_template('my_orders.html', orders=orders)


@app.route('/my/payments')
@login_required
def my_payments():
    db = get_db()
    if getattr(current_user, 'role', '').lower() == 'admin':
        rows = db.execute('SELECT * FROM payments ORDER BY date_paid DESC').fetchall()
    else:
        customer = db.execute('SELECT * FROM customers WHERE email = ?', (current_user.email,)).fetchone()
        if not customer:
            flash('No customer record found for your account', 'warning')
            return redirect(url_for('products'))
        rows = db.execute('''
            SELECT p.* FROM payments p
            JOIN orders o ON p.order_id = o.id
            WHERE o.customer_id = ?
            ORDER BY p.date_paid DESC
        ''', (customer['id'],)).fetchall()
    return render_template('my_payments.html', payments=rows)


# Customer dashboard
@app.route('/dashboard')
@login_required
def customer_dashboard():
    db = get_db()
    role = getattr(current_user, 'role', '').lower()
    if role == 'admin':
        # Admin dashboard could be more elaborate; redirect to admin dashboard
        return redirect(url_for('admin_dashboard'))

    # find customer id
    customer = db.execute('SELECT * FROM customers WHERE email = ?', (current_user.email,)).fetchone()
    if not customer:
        flash('Customer record not found', 'warning')
        return redirect(url_for('products'))

    cust_id = customer['id']
    
    # Enhanced customer statistics
    total_products = db.execute('SELECT COUNT(*) as c FROM products').fetchone()['c']
    my_orders = db.execute('SELECT COUNT(*) as c FROM orders WHERE customer_id = ?', (cust_id,)).fetchone()['c']
    my_payments = db.execute("SELECT COUNT(*) as c FROM payments p JOIN orders o ON p.order_id = o.id WHERE o.customer_id = ?", (cust_id,)).fetchone()['c']
    
    # Total spent
    total_spent = db.execute("SELECT COALESCE(SUM(total), 0) as sum FROM orders WHERE customer_id = ?", (cust_id,)).fetchone()['sum']
    
    # Total paid
    total_paid = db.execute("""
        SELECT COALESCE(SUM(p.amount), 0) as sum 
        FROM payments p 
        JOIN orders o ON p.order_id = o.id 
        WHERE o.customer_id = ?
    """, (cust_id,)).fetchone()['sum']
    
    # Outstanding balance
    outstanding = total_spent - total_paid
    
    # Recent orders
    recent_orders = db.execute("""
        SELECT id, order_date, status, total 
        FROM orders 
        WHERE customer_id = ? 
        ORDER BY order_date DESC 
        LIMIT 5
    """, (cust_id,)).fetchall()
    
    # Recent payments
    recent_payments = db.execute("""
        SELECT p.id, p.amount, p.date_paid, p.status, o.id as order_id
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        WHERE o.customer_id = ?
        ORDER BY p.date_paid DESC
        LIMIT 5
    """, (cust_id,)).fetchall()
    
    return render_template('customer_dashboard.html', 
                         total_products=total_products, 
                         my_orders=my_orders, 
                         my_payments=my_payments,
                         total_spent=total_spent,
                         total_paid=total_paid,
                         outstanding=outstanding,
                         recent_orders=recent_orders,
                         recent_payments=recent_payments,
                         customer=customer)

@app.route('/orders')
@login_required
def orders_list():
    db = get_db()
    rows = db.execute(""" 
        SELECT o.id, o.order_date, o.total, o.status, c.name as customer
        FROM orders o LEFT JOIN customers c ON o.customer_id = c.id
        ORDER BY o.order_date DESC
    """).fetchall()
    return render_template('orders_list.html', orders=rows)

# Payments admin view
@app.route('/payments')
@login_required
@admin_required
def payments_list():
    db = get_db()
    rows = db.execute(""" 
        SELECT p.id, p.order_id, p.amount, p.date_paid, p.status, c.name as customer
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        LEFT JOIN customers c ON o.customer_id = c.id
        ORDER BY p.date_paid DESC
    """).fetchall()
    return render_template('payments_list.html', payments=rows)

@app.route('/payments/mark_paid/<int:pid>', methods=['POST'])
@login_required
@admin_required
def mark_paid(pid):
    db = get_db()
    db.execute("UPDATE payments SET status = 'Paid', date_paid = ? WHERE id = ?", (datetime.utcnow().isoformat(), pid))
    db.commit()
    flash('Payment marked as Paid', 'success')
    return redirect(url_for('payments_list'))

# Trips (admin only)
@app.route('/trips', methods=['GET','POST'])
@login_required
@admin_required
def trips():
    db = get_db()
    if request.method == 'POST':
        vehicle_no = request.form['vehicle_no']
        driver_name = request.form.get('driver_name','')
        date = request.form.get('date') or datetime.utcnow().date().isoformat()
        amount = float(request.form.get('amount',0))
        note = request.form.get('note','')
        db.execute("INSERT INTO trips (vehicle_no, driver_name, date, amount, note) VALUES (?, ?, ?, ?, ?)",
                   (vehicle_no, driver_name, date, amount, note))
        db.commit()
        # Try to find the inserted trip id in a DB-agnostic way
        try:
            new_row = db.execute("SELECT id FROM trips WHERE vehicle_no = ? AND date = ? AND amount = ? ORDER BY id DESC LIMIT 1",
                                 (vehicle_no, date, amount)).fetchone()
            new_id = new_row['id'] if new_row else None
        except Exception:
            new_id = None
        # Insert a generic audit entry capturing the creation
        try:
            user = getattr(current_user, 'username', None) or getattr(current_user, 'email', None) or 'unknown'
            summary = f"vehicle_no={vehicle_no};driver_name={driver_name};date={date};amount={amount};note={note}"
            db.execute('INSERT INTO audit (entity, entity_id, user, action, field, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       ('trips', new_id, user, 'create', 'all', '', summary, 'create'))
        except Exception:
            pass
        db.commit()
        flash('Trip recorded', 'success')
        return redirect(url_for('trips'))
    rows = db.execute("SELECT * FROM trips ORDER BY date DESC").fetchall()
    # calculate totals per vehicle for today
    today = datetime.utcnow().date().isoformat()
    totals_today = db.execute("SELECT vehicle_no, SUM(amount) as total FROM trips WHERE date = ? GROUP BY vehicle_no", (today,)).fetchall()
    return render_template('trips.html', trips=rows, totals_today=totals_today)


@app.route('/trips/edit/<int:tid>', methods=['GET','POST'])
@login_required
@admin_required
def trips_edit(tid):
    db = get_db()
    if request.method == 'POST':
        vehicle_no = request.form['vehicle_no']
        driver_name = request.form.get('driver_name','')
        date = request.form.get('date') or datetime.utcnow().date().isoformat()
        try:
            amount = float(request.form.get('amount',0))
        except Exception:
            amount = 0.0
        note = request.form.get('note','')

        # fetch old values for auditing
        old = db.execute('SELECT * FROM trips WHERE id = ?', (tid,)).fetchone()
        if not old:
            flash('Trip not found', 'warning')
            return redirect(url_for('trips'))

        old_vals = {}
        try:
            cols = old.keys()
            old_vals = {
                'vehicle_no': old['vehicle_no'] if 'vehicle_no' in cols else '',
                'driver_name': old['driver_name'] if 'driver_name' in cols else '',
                'date': old['date'] if 'date' in cols else '',
                'amount': old['amount'] if 'amount' in cols else 0,
                'note': old['note'] if 'note' in cols else ''
            }
        except Exception:
            pass

        db.execute('UPDATE trips SET vehicle_no = ?, driver_name = ?, date = ?, amount = ?, note = ? WHERE id = ?',
                (vehicle_no, driver_name, date, amount, note, tid))

        # log audits per-field
        try:
            user = getattr(current_user, 'username', None) or getattr(current_user, 'email', None) or 'unknown'
            def _log(field, oldv, newv, reason=''):
                try:
                    db.execute('INSERT INTO audit (entity, entity_id, user, action, field, old_value, new_value, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                            ('trips', tid, user, 'update', field, str(oldv), str(newv), reason))
                except Exception:
                    pass

            if str(old_vals.get('vehicle_no','')) != str(vehicle_no):
                _log('vehicle_no', old_vals.get('vehicle_no',''), vehicle_no, request.form.get('reason',''))
            if str(old_vals.get('driver_name','')) != str(driver_name):
                _log('driver_name', old_vals.get('driver_name',''), driver_name, request.form.get('reason',''))
            if str(old_vals.get('date','')) != str(date):
                _log('date', old_vals.get('date',''), date, request.form.get('reason',''))
            try:
                if float(old_vals.get('amount') or 0) != float(amount):
                    _log('amount', old_vals.get('amount'), amount, request.form.get('reason',''))
            except Exception:
                pass
            if str(old_vals.get('note','')) != str(note):
                _log('note', old_vals.get('note',''), note, request.form.get('reason',''))
        except Exception:
            pass

        db.commit()
        flash('Trip updated', 'success')
        return redirect(url_for('trips'))

    row = db.execute('SELECT * FROM trips WHERE id = ?', (tid,)).fetchone()
    if not row:
        flash('Trip not found', 'warning')
        return redirect(url_for('trips'))
    return render_template('trips_edit.html', trip=row)

# Notes (accessible to logged-in users)
@app.route('/notes', methods=['GET','POST'])
@login_required
def notes():
    db = get_db()
    if request.method == 'POST':
        content = request.form['content']
        db.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        db.commit()
        flash('Note saved', 'success')
        return redirect(url_for('notes'))
    rows = db.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchall()
    return render_template('notes.html', notes=rows)

# Sales report: daily and monthly
@app.route('/sales')
@login_required
@admin_required
def sales_report():
    db = get_db()
    # Monthly totals
    rows = db.execute(""" 
        SELECT strftime('%Y-%m', sale_date) as month, SUM(amount) as total
        FROM sales
        GROUP BY month
        ORDER BY month
    """).fetchall()
    months = [r['month'] for r in rows]
    totals = [r['total'] for r in rows]
    # Daily totals for last 7 days
    rows_d = db.execute(""" 
        SELECT date(sale_date) as day, SUM(amount) as total
        FROM sales
        WHERE date(sale_date) >= date('now','-6 day')
        GROUP BY day
        ORDER BY day
    """).fetchall()
    days = [r['day'] for r in rows_d]
    day_totals = [r['total'] for r in rows_d]
    return render_template('sales.html', months=months, totals=totals, days=days, day_totals=day_totals)

# Utility route to insert demo sales (for presentation only)
@app.route('/admin/seed_demo_sales')
@login_required
@admin_required
def seed_demo_sales():
    db = get_db()
    demo = [
        ('2025-01-05', 1200),
        ('2025-02-10', 1900),
        ('2025-03-15', 3000),
        ('2025-04-20', 2500),
        ('2025-05-12', 2800),
    ]
    for d, a in demo:
        db.execute("INSERT INTO sales (sale_date, amount) VALUES (?, ?)", (d, a))
    db.commit()
    flash('Demo sales inserted', 'success')
    return redirect(url_for('sales_report'))

# --- Ledger Routes ---
@app.route('/ledger')
@login_required
@admin_required
def ledger():
    db = get_db()
    entries = db.execute('''
        SELECT * FROM ledger 
        ORDER BY date DESC, id DESC
    ''').fetchall()
    return render_template('ledger.html', entries=entries)

@app.route('/ledger/add', methods=['GET', 'POST'])
@login_required
@admin_required
def ledger_add():
    if request.method == 'POST':
        date = request.form['date']
        description = request.form['description']
        qty_in = request.form.get('qty_in', 0) or 0
        qty_out = request.form.get('qty_out', 0) or 0
        amount = request.form.get('amount', 0) or 0
        
        db = get_db()
        
        # Calculate new balance based on previous balance
        last_entry = db.execute('SELECT balance FROM ledger ORDER BY date DESC, id DESC LIMIT 1').fetchone()
        previous_balance = last_entry['balance'] if last_entry else 0
        new_balance = previous_balance + float(amount)
        
        # Insert new entry
        db.execute('''
            INSERT INTO ledger (date, description, qty_in, qty_out, amount, balance, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, description, int(qty_in), int(qty_out), float(amount), new_balance, current_user.username))
        db.commit()
        
        flash('Ledger entry added successfully', 'success')
        return redirect(url_for('ledger'))
    
    return render_template('ledger_add.html')

@app.route('/ledger/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def ledger_edit(id):
    db = get_db()
    entry = db.execute('SELECT * FROM ledger WHERE id = ?', (id,)).fetchone()
    
    if not entry:
        flash('Entry not found', 'danger')
        return redirect(url_for('ledger'))
    
    if request.method == 'POST':
        date = request.form['date']
        description = request.form['description']
        qty_in = request.form.get('qty_in', 0) or 0
        qty_out = request.form.get('qty_out', 0) or 0
        amount = request.form.get('amount', 0) or 0
        
        # Recalculate balance for this entry and all subsequent entries
        # Get previous entry before this one
        prev_entry = db.execute('''
            SELECT balance FROM ledger 
            WHERE date < ? OR (date = ? AND id < ?)
            ORDER BY date DESC, id DESC LIMIT 1
        ''', (date, date, id)).fetchone()
        
        previous_balance = prev_entry['balance'] if prev_entry else 0
        new_balance = previous_balance + float(amount)
        
        # Update the entry
        db.execute('''
            UPDATE ledger 
            SET date = ?, description = ?, qty_in = ?, qty_out = ?, amount = ?, balance = ?
            WHERE id = ?
        ''', (date, description, int(qty_in), int(qty_out), float(amount), new_balance, id))
        
        # Recalculate all subsequent balances
        subsequent = db.execute('''
            SELECT id, amount FROM ledger 
            WHERE date > ? OR (date = ? AND id > ?)
            ORDER BY date ASC, id ASC
        ''', (date, date, id)).fetchall()
        
        current_balance = new_balance
        for row in subsequent:
            current_balance += row['amount']
            db.execute('UPDATE ledger SET balance = ? WHERE id = ?', (current_balance, row['id']))
        
        db.commit()
        flash('Ledger entry updated successfully', 'success')
        return redirect(url_for('ledger'))
    
    return render_template('ledger_edit.html', entry=entry)

@app.route('/ledger/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def ledger_delete(id):
    db = get_db()
    entry = db.execute('SELECT * FROM ledger WHERE id = ?', (id,)).fetchone()
    
    if entry:
        # Delete the entry
        db.execute('DELETE FROM ledger WHERE id = ?', (id,))
        
        # Recalculate all balances after this entry
        entries = db.execute('SELECT id, amount FROM ledger ORDER BY date ASC, id ASC').fetchall()
        balance = 0
        for row in entries:
            balance += row['amount']
            db.execute('UPDATE ledger SET balance = ? WHERE id = ?', (balance, row['id']))
        
        db.commit()
        flash('Ledger entry deleted successfully', 'success')
    else:
        flash('Entry not found', 'danger')
    
    return redirect(url_for('ledger'))

# Health route
@app.route('/ping')
def ping():
    return "pong"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Railway's port
    app.run(host="0.0.0.0", port=port)
