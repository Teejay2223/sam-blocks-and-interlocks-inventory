import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
db = sqlite3.connect('database.db')
db.row_factory = sqlite3.Row

# Check if admin exists
cur = db.execute('SELECT * FROM users WHERE username = ?', ('admin',))
admin = cur.fetchone()

if admin:
    print(f"Admin user exists:")
    print(f"  Username: {admin['username']}")
    print(f"  Email: {admin['email']}")
    print(f"  Role: {admin['role']}")
    print("\nUpdating password to 'Sam1991@'...")
    
    # Update admin password and email
    new_password = generate_password_hash('Sam1991@')
    db.execute('UPDATE users SET password = ?, email = ? WHERE username = ?', 
               (new_password, 'samventuresblocksinterlocks@gmail.com', 'admin'))
    db.commit()
    print("✅ Admin password updated successfully!")
else:
    print("Admin user does not exist. Creating new admin...")
    new_password = generate_password_hash('Sam1991@')
    db.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
               ('admin', 'samventuresblocksinterlocks@gmail.com', new_password, 'admin'))
    db.commit()
    print("✅ Admin user created successfully!")

print("\n📧 Email: samventuresblocksinterlocks@gmail.com")
print("🔑 Password: Sam1991@")
print("👤 Username: admin")

db.close()
