PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'Customer'
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    size TEXT,
    price REAL NOT NULL,
    qty INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 10
);
CREATE TABLE IF NOT EXISTS raw_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    qty REAL NOT NULL,
    reorder_level REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS finished_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_type TEXT NOT NULL,
    qty INTEGER NOT NULL,
    date_produced TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending',
    total REAL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date_paid TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    qty INTEGER NOT NULL DEFAULT 1,
    sale_date TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_no TEXT NOT NULL,
    driver_name TEXT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    qty_in INTEGER DEFAULT 0,
    qty_out INTEGER DEFAULT 0,
    amount REAL NOT NULL,
    balance REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO products (id, name, description, size, price, qty, reorder_level) VALUES
(1, 'Standard Block', 'Normal block for general use', '4"', 50, 100, 20),
(2, '6-inch Block', 'Lightweight partition block', '6"', 450, 50, 10),
(3, '8-inch Block', 'Load-bearing 8-inch block', '8"', 500, 75, 15),
(4, '9-inch Block', 'Large block for special projects', '9"', 600, 30, 10);
