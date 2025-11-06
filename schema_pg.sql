-- Postgres schema equivalent for sam_blocks_inventory
-- Uses SERIAL for auto-increment primary keys and numeric types where appropriate

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'Customer'
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    size TEXT,
    price NUMERIC NOT NULL,
    qty INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS raw_materials (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    qty NUMERIC NOT NULL,
    reorder_level NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS finished_blocks (
    id SERIAL PRIMARY KEY,
    block_type TEXT NOT NULL,
    qty INTEGER NOT NULL,
    date_produced TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT DEFAULT 'Pending',
    total NUMERIC DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    unit_price NUMERIC NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    date_paid TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT DEFAULT 'Pending',
    account_number TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    amount NUMERIC NOT NULL,
    product_id INTEGER,
    qty INTEGER DEFAULT 1,
    buyer_name TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    vehicle_no TEXT NOT NULL,
    driver_name TEXT,
    date DATE NOT NULL,
    amount NUMERIC NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS breakages (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    reason TEXT,
    reported_by TEXT,
    date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS product_audit (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    user TEXT,
    action TEXT,
    field TEXT,
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- optional seed data
INSERT INTO products (id, name, description, size, price, qty) VALUES
(1, 'Standard Block', 'Normal block for general use', '4"', 50, 100) ON CONFLICT DO NOTHING;
INSERT INTO products (id, name, description, size, price, qty) VALUES
(2, '6-inch Block', 'Lightweight partition block', '6"', 450, 50) ON CONFLICT DO NOTHING;
INSERT INTO products (id, name, description, size, price, qty) VALUES
(3, '8-inch Block', 'Load-bearing 8-inch block', '8"', 500, 30) ON CONFLICT DO NOTHING;
INSERT INTO products (id, name, description, size, price, qty) VALUES
(4, '9-inch Block', 'Large block for special projects', '9"', 600, 20) ON CONFLICT DO NOTHING;

-- Ledger and generic audit tables used by admin/ledger features
CREATE TABLE IF NOT EXISTS ledger (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    qty_in INTEGER DEFAULT 0,
    qty_out INTEGER DEFAULT 0,
    amount NUMERIC DEFAULT 0,
    balance NUMERIC DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS generic_audit (
    id SERIAL PRIMARY KEY,
    entity TEXT,
    entity_id INTEGER,
    user TEXT,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);
