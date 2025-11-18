# How to Label Your Block Images
## Quick Guide to Creating Training Data

Since Roboflow isn't working, use one of these FREE alternatives:

---

## Option 1: LabelImg (RECOMMENDED ⭐)

### Why LabelImg?
- ✅ Completely FREE and open source
- ✅ Works offline (no internet needed)
- ✅ Designed for YOLO format
- ✅ Simple interface - just draw boxes!
- ✅ Keyboard shortcuts = very fast

### Installation (Windows):

**Method A: Using pip (Easiest)**
```powershell
# In PowerShell
cd "c:\Users\HP PRO\Desktop\sam_blocks_inventory"
& ".\.venv\Scripts\python.exe" -m pip install labelImg

# Run it
& ".\.venv\Scripts\labelImg.exe"
```

**Method B: Download executable**
1. Go to: https://github.com/HumanSignal/labelImg/releases
2. Download: `windows_v1.8.6.zip`
3. Extract and run `labelImg.exe`

---

### How to Use LabelImg:

#### Step 1: Open LabelImg
- Run the program
- Click **"Open Dir"** → Select `c:\Users\HP PRO\Desktop\sam_blocks_inventory\block_dataset\images`
- Click **"Change Save Dir"** → Select `c:\Users\HP PRO\Desktop\sam_blocks_inventory\block_dataset\labels`

#### Step 2: Set YOLO Format
- Click **"View"** menu → Check **"Auto Save mode"** (saves automatically)
- In the left panel, make sure format shows: **"YOLO"**
- If not, click the format button to switch

#### Step 3: Create classes.txt
- LabelImg needs a `classes.txt` file
- Create it manually:
  ```powershell
  "block" | Out-File -FilePath "c:\Users\HP PRO\Desktop\sam_blocks_inventory\block_dataset\classes.txt" -Encoding utf8
  ```
- Or in LabelImg, when you draw first box, type "block" as class name

#### Step 4: Label Images
1. **Draw box:** Press `W` or click "Create RectBox"
2. **Drag** around a hollow block (include full block)
3. **Type class:** Enter "block" (or select from list)
4. **Repeat** for ALL blocks in the image
5. **Next image:** Press `D` or click "Next Image"
6. **Previous:** Press `A`

#### Keyboard Shortcuts:
- `W` = Draw new box
- `D` = Next image
- `A` = Previous image
- `Del` = Delete selected box
- `Ctrl+S` = Save (but auto-save is on!)
- `Ctrl+D` = Duplicate box

---

## Option 2: CVAT (Web-based, Free)

### Why CVAT?
- ✅ Professional tool (used by companies)
- ✅ Can run locally or use cloud version
- ✅ Team collaboration features
- ✅ Automatic interpolation between frames (for videos)

### Quick Start:
1. Go to: https://app.cvat.ai/
2. Sign up (free account)
3. Create new task
4. Upload your images
5. Label: "block"
6. Draw boxes
7. Export → YOLO 1.1 format

**Pros:** Professional, feature-rich
**Cons:** Requires internet, learning curve

---

## Option 3: Label Studio (Open Source)

### Installation:
```powershell
pip install label-studio
label-studio start
```

Opens in browser at http://localhost:8080

**Pros:** Modern UI, many export formats
**Cons:** More complex setup

---

## Option 4: Makesense.ai (Web-based, No Signup)

### Quick Start:
1. Go to: https://www.makesense.ai/
2. Click "Get Started"
3. Drop your images
4. Select "Object Detection"
5. Add label: "block"
6. Draw boxes
7. Export → YOLO format

**Pros:** No installation, no signup, simple
**Cons:** All processing in browser (slower with many images)

---

## 📝 Labeling Best Practices

### What to Label:
✅ **DO label:**
- Hollow concrete blocks (interlocks)
- Complete blocks (not broken/partial)
- Blocks at any angle
- Stacked blocks (label each one separately)

❌ **DON'T label:**
- Bricks
- Walls
- Parts of blocks cut off by image edge
- Severely damaged/unrecognizable blocks

### How to Draw Good Boxes:

```
GOOD ✅                    BAD ❌
┌─────────────┐           ┌──────┐
│             │           │  Too │
│   BLOCK     │    vs     │ Small│
│             │           └──────┘
└─────────────┘
(Tight fit)              (Missing edges)

GOOD ✅                    BAD ❌
┌─────────────┐           ┌────────────────┐
│   BLOCK     │    vs     │  BLOCK + BG    │
└─────────────┘           │  Extra space   │
(Just block)              └────────────────┘
                          (Too much background)
```

### Tips for Speed:
1. **Start with easy images** - clear, well-lit, few blocks
2. **Use keyboard shortcuts** - 10x faster than mouse
3. **Label in batches** - 5-10 images, take break, repeat
4. **Consistency matters** - same labeling style for all images
5. **Quality > Quantity** - 30 perfect labels > 100 sloppy ones

---

## 🎯 Recommended Workflow

### For Your 89 Images:

**Day 1: Label 20-30 images** (1-2 hours)
- Use LabelImg
- Start with clearest images
- Get comfortable with tool

**Day 2: Label another 20-30** (1-2 hours)
- Total: 40-60 labeled images
- Good enough for training!

**Day 3: Train model** (30 mins)
- Upload to Google Drive
- Run Colab notebook
- See initial results

**Day 4: Label remaining images + improve** (1-2 hours)
- Based on what model gets wrong
- Focus on difficult cases
- Re-train for better accuracy

---

## 📊 How Many Images Do You Need?

| Images | Expected Accuracy | Use Case |
|--------|------------------|----------|
| 30-50  | 50-60% mAP | Proof of concept |
| 50-100 | 60-75% mAP | Working prototype |
| 100-200| 75-85% mAP | Production ready |
| 200+   | 85-95% mAP | Commercial grade |

**Your situation:** 89 images available
**Recommendation:** Label at least 50 for decent results

---

## 🚀 Quick Start (LabelImg)

Run these commands to get started in 2 minutes:

```powershell
# 1. Install LabelImg
cd "c:\Users\HP PRO\Desktop\sam_blocks_inventory"
& ".\.venv\Scripts\python.exe" -m pip install labelImg

# 2. Create classes file
"block" | Out-File -FilePath "block_dataset\classes.txt" -Encoding utf8

# 3. Launch LabelImg
& ".\.venv\Scripts\labelImg.exe" "block_dataset\images" "" "block_dataset\classes.txt"
```

This opens LabelImg with your images ready to label!

---

## 🎓 For Your Defense

**"How did you create training data?"**

> "I manually labeled 50+ images using LabelImg, an open-source annotation tool. For each image, I drew bounding boxes around every hollow block, ensuring tight fit around block edges. Labels were exported in YOLO format (normalized coordinates). This supervised learning approach ensures the model learns exactly what we define as 'blocks', not assumptions from pre-existing datasets."

**"Why manual labeling instead of automated tools?"**

> "Manual labeling ensures accuracy and domain specificity. Automated tools often mislabel or include wrong objects. Since our blocks have unique characteristics (hollow, specific dimensions), manual labeling allows me to define exactly what constitutes a 'block' for our inventory system. Quality of training data directly impacts model performance - garbage in, garbage out."

**"How long did labeling take?"**

> "Approximately 3-4 hours for 50 images, averaging 4-5 minutes per image. Each image contained 1-5 blocks requiring individual bounding boxes. Using keyboard shortcuts (W for box, D for next) significantly improved speed. This upfront time investment ensures reliable automated detection, saving hundreds of hours in manual counting over the system's lifetime."

---

## 📸 After Labeling

Once you have 30+ labeled images:

1. **Upload to Google Drive:**
   ```powershell
   # Compress the updated dataset
   Compress-Archive -Path "block_dataset" -DestinationPath "block_dataset_labeled.zip" -Force
   ```
   Then upload `block_dataset_labeled.zip` to Google Drive

2. **Update Colab notebook:**
   - Extract the new zip
   - Run cells 5-8 to train
   - Model should now detect blocks correctly!

3. **Check results:**
   - mAP50 should be 0.5+ with 30-50 good labels
   - If still low, label 10-20 more images

---

## 🛠️ Troubleshooting

**LabelImg won't install?**
```powershell
# Try with pip upgrade
python -m pip install --upgrade pip
pip install labelImg
```

**Can't find labelImg.exe?**
```powershell
# Find where it installed
python -c "import labelImg; print(labelImg.__file__)"

# Or run directly with Python
python -m labelImg
```

**YOLO format not saving correctly?**
- Make sure `classes.txt` exists in the images folder
- Check that format says "YOLO" in LabelImg (not "PascalVOC")
- Label files should be `.txt` with same name as image

**Boxes don't appear?**
- Press `W` to create box
- Make sure you're in "Create RectBox" mode
- Check that you have classes defined

---

## 📚 Resources

- LabelImg GitHub: https://github.com/HumanSignal/labelImg
- YOLO Format Explained: https://docs.ultralytics.com/datasets/detect/
- Video Tutorial: Search "LabelImg tutorial" on YouTube

---

**Ready to label?** Start with LabelImg - it's the fastest and easiest! 🚀

Good luck! Label 30 images today and you can train tomorrow! 💪
