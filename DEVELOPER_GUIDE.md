# Developer Guide: Making UI Changes & Debugging
## S.A.M Blocks & Interlocks Inventory System

**Your System:** Windows with Python virtual environment  
**Tech Stack:** Flask + Bootstrap 5 + Custom CSS

---

## 📁 Project Structure

```
sam_blocks_inventory/
├── app.py                      # Main Flask application
├── static/
│   ├── style.css              # YOUR CUSTOM STYLES (edit this!)
│   ├── logo.png               # Logo image
│   └── sam.jpg                # Original logo
├── templates/
│   ├── base.html              # Main layout template
│   ├── index.html             # Home page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── admin/
│       └── dashboard.html
├── database.db                # SQLite database
└── requirements.txt           # Python dependencies
```

---

## 🎨 How to Change UI Colors & Styles

### **Step 1: Find the CSS File**

Open: `c:\Users\HP PRO\Desktop\sam_blocks_inventory\static\style.css`

This is where ALL your custom styles are!

---

### **Step 2: Common Changes**

#### **A. Change Background Color**

Find this section (around line 19):
```css
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f8f5f2;    /* ← CHANGE THIS COLOR */
    min-height: 100vh;
    color: var(--dark-text);
}
```

**Color Examples:**
```css
background: #f8f5f2;        /* Light cream/pink (current) */
background: #ffffff;        /* Pure white */
background: #f0f4f8;        /* Light blue-gray */
background: #fef6e7;        /* Light yellow/cream */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* Gradient */
```

---

#### **B. Change Navbar Color**

Find (around line 29):
```css
.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    /* ↑ Change this for navbar color */
}
```

**Examples:**
```css
background: #343a40 !important;                                    /* Dark gray */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;  /* Green */
background: #2c3e50 !important;                                    /* Dark blue */
```

---

#### **C. Change Button Colors**

Find button sections (around line 150):
```css
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-success {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
```

**To make simple solid colors:**
```css
.btn-primary {
    background: #007bff;  /* Solid blue */
}
```

---

#### **D. Change Card Styles**

Find (around line 70):
```css
.card {
    border: none;
    border-radius: 15px;     /* ← Rounded corners */
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);  /* ← Shadow */
    transition: all 0.3s ease;
    overflow: hidden;
    background: white;       /* ← Card background */
}
```

**Examples:**
```css
border-radius: 5px;          /* Less rounded */
border-radius: 25px;         /* More rounded */
box-shadow: none;            /* No shadow */
background: #f9f9f9;         /* Light gray background */
```

---

### **Step 3: Save and Test**

After editing `style.css`:

1. **Save the file** (Ctrl+S)
2. **Refresh your browser** (Ctrl+F5 or Ctrl+Shift+R for hard refresh)
3. Changes appear immediately!

**If changes don't appear:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Restart Flask server

---

## 🔧 How to Test Changes Locally

### **Start the Server:**

```powershell
# 1. Open PowerShell
# 2. Navigate to project
cd "c:\Users\HP PRO\Desktop\sam_blocks_inventory"

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Run Flask
python app.py
```

**Or shorter version:**
```powershell
cd "c:\Users\HP PRO\Desktop\sam_blocks_inventory"
& ".\.venv\Scripts\python.exe" app.py
```

### **View in Browser:**

Open: `http://127.0.0.1:5000` or `http://localhost:5000`

### **Stop the Server:**

Press `Ctrl+C` in PowerShell

---

## 🚀 How to Deploy Changes to Railway

### **Option A: Using Git Commands (Recommended)**

```powershell
# 1. Check what changed
git status

# 2. Add your changes
git add static/style.css           # Add specific file
# OR
git add .                          # Add all changes

# 3. Commit with a message
git commit -m "Update navbar color to green"

# 4. Push to GitHub (Railway auto-deploys)
git push origin main
```

**Railway automatically:**
- Detects the push
- Rebuilds your app
- Deploys in 1-2 minutes

---

### **Option B: Railway Dashboard**

1. Go to https://railway.app/
2. Click your project
3. Click "Deployments"
4. Click "Deploy Now"

---

## 🐛 Debugging Common Issues

### **Issue 1: Changes Don't Show Up**

**Symptoms:**
- Edited CSS but nothing changed
- Old design still showing

**Solutions:**

1. **Hard Refresh Browser:**
   ```
   Windows: Ctrl+F5 or Ctrl+Shift+R
   ```

2. **Clear Browser Cache:**
   ```
   Chrome: Ctrl+Shift+Delete → Clear browsing data
   ```

3. **Check File Saved:**
   - Look for `•` (dot) in VS Code tab = unsaved
   - Press Ctrl+S to save

4. **Restart Flask:**
   ```powershell
   # Stop: Ctrl+C
   # Start again: python app.py
   ```

---

### **Issue 2: Site Looks Broken**

**Symptoms:**
- Layout messed up
- Missing styles
- Weird spacing

**Solutions:**

1. **Check CSS Syntax:**
   ```css
   /* WRONG - missing semicolon */
   body {
       background: #f8f5f2
       color: black;
   }

   /* CORRECT */
   body {
       background: #f8f5f2;  /* ← semicolon! */
       color: black;
   }
   ```

2. **Check VS Code Problems Panel:**
   - Bottom of VS Code
   - Look for red squiggly lines
   - Fix syntax errors

3. **Restore from Git:**
   ```powershell
   git checkout static/style.css  # Undo changes
   ```

---

### **Issue 3: Flask Won't Start**

**Symptoms:**
- Error: "Module not found"
- Error: "Address already in use"

**Solutions:**

1. **Virtual Environment Not Activated:**
   ```powershell
   # Check if activated (should see (.venv) in prompt)
   .\.venv\Scripts\Activate.ps1
   ```

2. **Missing Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Port Already in Use:**
   ```powershell
   # Kill existing Python processes
   taskkill /F /IM python.exe

   # Or use different port
   python app.py --port 5001
   ```

4. **Database Locked:**
   ```powershell
   # Remove lock file
   Remove-Item database.db-wal -ErrorAction SilentlyContinue
   ```

---

### **Issue 4: Railway Deployment Fails**

**Symptoms:**
- Build failed
- App crashes
- 500 error

**Solutions:**

1. **Check Railway Logs:**
   - Go to Railway dashboard
   - Click your service
   - Click "Logs" tab
   - Look for error messages

2. **Check requirements.txt:**
   ```powershell
   # Regenerate requirements
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Update requirements"
   git push
   ```

3. **Check Environment Variables:**
   - Railway dashboard → Variables tab
   - Make sure all needed vars are set

---

## 📝 Making Template (HTML) Changes

### **Where Templates Are:**

```
templates/
├── base.html          # Main layout (navbar, footer)
├── index.html         # Home page
├── products.html      # Products page
└── auth/
    ├── login.html     # Login page
    └── register.html  # Register page
```

### **How to Edit:**

1. **Open template file** (e.g., `templates/index.html`)

2. **Make changes:**
   ```html
   <!-- Add a new section -->
   <div class="card">
       <div class="card-body">
           <h3>New Section</h3>
           <p>Your content here</p>
       </div>
   </div>
   ```

3. **Save** (Ctrl+S)

4. **Refresh browser** - changes show immediately!

---

## 🎨 Quick Reference: Common CSS Properties

```css
/* Colors */
color: #333;                  /* Text color */
background: #fff;             /* Background color */
border-color: #ddd;           /* Border color */

/* Spacing */
margin: 10px;                 /* Outside spacing */
padding: 20px;                /* Inside spacing */
margin-top: 15px;             /* Specific side */

/* Size */
width: 100%;                  /* Full width */
height: 200px;                /* Fixed height */
max-width: 1200px;            /* Maximum width */

/* Text */
font-size: 16px;              /* Text size */
font-weight: bold;            /* Bold text */
text-align: center;           /* Center align */

/* Borders */
border: 1px solid #ddd;       /* Border line */
border-radius: 10px;          /* Rounded corners */

/* Shadows */
box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* Drop shadow */

/* Display */
display: flex;                /* Flexbox layout */
display: none;                /* Hide element */
display: block;               /* Show element */
```

---

## 🔍 Finding What to Change

### **Method 1: Browser DevTools (Easiest!)**

1. **Open site in browser**
2. **Right-click** on element you want to change
3. **Click "Inspect"** (or press F12)
4. **See the styles** on the right side
5. **Try changes live** - edit in DevTools
6. **Copy working code** to your CSS file

**Example:**
```
1. Right-click on navbar
2. Click "Inspect"
3. See: .navbar { background: #667eea; }
4. Change to: background: red; (test live)
5. Copy to style.css when you like it
```

---

### **Method 2: Search in VS Code**

1. Press `Ctrl+Shift+F` (Find in Files)
2. Type what you're looking for:
   - "navbar" → Find navbar styles
   - "btn-primary" → Find primary button
   - "background" → Find all backgrounds
3. Edit the file that appears

---

### **Method 3: Class Names**

Look at HTML, find class names:
```html
<button class="btn btn-primary">Click Me</button>
                  └─ Look for .btn-primary in CSS
```

Then search CSS for `.btn-primary`

---

## 📚 Resources for Learning

### **Colors:**
- https://coolors.co/ - Generate color palettes
- https://htmlcolorcodes.com/ - Pick colors
- https://uigradients.com/ - Gradient generator

### **CSS:**
- https://www.w3schools.com/css/ - Learn CSS basics
- https://css-tricks.com/ - CSS tips and tricks

### **Bootstrap:**
- https://getbootstrap.com/docs/5.3/ - Bootstrap documentation
- Your site uses Bootstrap 5.3 components

---

## ⚡ Quick Fixes Cheat Sheet

```powershell
# Restart Flask server
cd "c:\Users\HP PRO\Desktop\sam_blocks_inventory"
python app.py

# Deploy to Railway
git add .
git commit -m "Update UI"
git push origin main

# Undo last change
git checkout style.css

# See what changed
git diff style.css

# Reset to last working version
git reset --hard HEAD

# Update dependencies
pip install -r requirements.txt

# Check for errors
python -m py_compile app.py
```

---

## 🎯 Your Workflow

### **Making a Simple Color Change:**

1. **Edit `static/style.css`**
2. **Save** (Ctrl+S)
3. **Refresh browser** (Ctrl+F5)
4. **If good, deploy:**
   ```powershell
   git add static/style.css
   git commit -m "Change background color"
   git push origin main
   ```
5. **Wait 1-2 min** for Railway to deploy
6. **Check live site!**

---

### **Testing a Big Change:**

1. **Create a backup:**
   ```powershell
   Copy-Item static/style.css static/style.backup.css
   ```

2. **Make changes**

3. **Test locally** (python app.py)

4. **If broken, restore:**
   ```powershell
   Copy-Item static/style.backup.css static/style.css
   ```

5. **If good, deploy to Railway**

---

## 🆘 When You're Stuck

1. **Check VS Code Problems panel** (bottom) for syntax errors

2. **Check browser Console** (F12 → Console tab) for JavaScript errors

3. **Check Railway Logs** for deployment errors

4. **Check Flask terminal** for Python errors

5. **Google the error message** - usually someone had same issue!

6. **Ask for help** - save error message and what you were trying to do

---

## ✅ Best Practices

1. **Always test locally first** before pushing to Railway

2. **Make small changes** - easier to debug

3. **Commit often** with clear messages
   ```
   Good: "Change navbar to green gradient"
   Bad: "update stuff"
   ```

4. **Keep backups** of working versions

5. **Use browser DevTools** to test before editing files

6. **Comment your code:**
   ```css
   /* Main background - changed to cream 2025-11-18 */
   body {
       background: #f8f5f2;
   }
   ```

---

## 🎓 You Now Know How To:

✅ Edit CSS colors and styles  
✅ Test changes locally  
✅ Deploy to Railway  
✅ Debug common issues  
✅ Use browser DevTools  
✅ Find what to change  
✅ Undo mistakes  
✅ Make backups  

**You're now independent!** 🎉

---

## 📞 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  QUICK COMMANDS                         │
├─────────────────────────────────────────┤
│ Start Server:                           │
│   python app.py                         │
│                                         │
│ Deploy:                                 │
│   git add .                             │
│   git commit -m "message"               │
│   git push origin main                  │
│                                         │
│ Undo Changes:                           │
│   git checkout style.css                │
│                                         │
│ Hard Refresh Browser:                   │
│   Ctrl+F5                               │
│                                         │
│ Open DevTools:                          │
│   F12 or Right-click → Inspect          │
└─────────────────────────────────────────┘
```

Save this guide and you can fix/change anything yourself! 💪
