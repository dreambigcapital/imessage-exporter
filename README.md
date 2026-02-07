# iMessage Exporter

Export your iMessage conversations to beautiful HTML files with all attachments preserved.

## ✨ Features
- 📱 Exports all iMessage conversations (supports 10,000+ messages per chat)
- 👤 Automatically matches phone numbers to contact names
- 🖼️ Embeds images and videos inline in HTML
- 📎 Copies all attachments to organized folders
- 🎨 Beautiful, easy-to-read HTML format with iMessage-style bubbles
- ⚡ Handles large contact lists (1000+ contacts)
- 🔒 100% private - all processing happens locally on your Mac

## 📋 Requirements
- macOS 10.14 or higher
- Python 3.6+ (pre-installed on macOS)
- Terminal access

## 🚀 Quick Start

### 1. Download
Download the `imessage_archive.py` file to your Mac.

### 2. Grant Permissions (One-Time Setup)

**Required for the script to access your messages and contacts:**

#### Step A: Full Disk Access
1. Open **System Settings** (or System Preferences)
2. Go to **Privacy & Security** → **Full Disk Access**
3. Click the **🔒** lock icon and authenticate
4. Click the **+** button
5. Navigate to `/Applications/Utilities/` and select **Terminal**
6. Enable the checkbox next to Terminal

#### Step B: Contacts Access
1. Still in **System Settings**
2. Go to **Privacy & Security** → **Contacts**
3. Click the **+** button
4. Add **Terminal** again
5. Enable the checkbox

#### Step C: Restart Terminal
Close Terminal completely and reopen it for permissions to take effect.

### 3. Run the Exporter

Open Terminal and run:
```bash
cd ~/Downloads  # Or wherever you saved the file
python3 imessage_archive.py
```

### 4. Follow the Prompts
1. Press Enter when ready (after granting permissions)
2. Wait for contacts to load (1-3 minutes for large lists)
3. Press Enter for default location or type a custom path
4. Wait for export to complete (1-5 minutes depending on message count)

## 📁 Output Structure

```
iMessage_Export/
├── Mom/
│   ├── Mom_chat.html          ← Open this in your browser
│   └── attachments/
│       ├── IMG_1234.jpg
│       └── VID_5678.mp4
├── Dad/
│   ├── Dad_chat.html
│   └── attachments/
└── John Smith/
    ├── John Smith_chat.html
    └── attachments/
```

Each contact gets their own folder with:
- HTML file with all messages (styled like iMessage)
- Attachments folder with all photos, videos, and files

## 🎯 What Gets Exported

✅ Text messages  
✅ iMessages  
✅ Photos (embedded inline)  
✅ Videos (playable in browser)  
✅ Attachments (PDFs, docs, etc.)  
✅ Timestamps  
✅ Group chats  
✅ Reactions and effects (as text)  

## 🔧 Troubleshooting

### "Permission denied" when accessing chat.db
**Solution:** 
- Make sure you granted **Full Disk Access** to Terminal
- Restart Terminal after granting
- Try running the script again

### Contacts showing as phone numbers
**Possible causes:**
1. Chunk timeout (script will continue and load remaining contacts)
2. Contact not in your Contacts app
3. Phone number format mismatch

**What happens:**
- Script loads contacts in chunks of 50
- If a chunk times out (90 seconds), it skips and continues
- You'll typically get 70-90% contact match rate
- Remaining chats use phone numbers as folder names

### Messages appear as gibberish or blank
**This is rare (<1% of messages)**
- Usually affects very old messages with special formatting
- Most messages will extract perfectly
- The script tries multiple decoding methods

### Script is slow
**Expected behavior:**
- Contact loading: 1-3 minutes for 1000+ contacts
- Export: 1-5 minutes for 50,000+ messages
- Progress is shown in real-time

## 📊 Performance

Tested with:
- ✅ 579 conversations
- ✅ 76,000+ messages
- ✅ 12,000+ attachments
- ✅ 1,125 contacts
- ⏱️ Total time: ~5 minutes

## 🔒 Privacy & Security

- **No internet connection required** - everything runs locally
- **No data is uploaded** anywhere
- **Open source** - all code is in one readable Python file
- **No tracking or analytics**
- You can review every line of code yourself

## 💾 Storage Requirements

Estimate: ~1-2 GB per 10,000 messages (including attachments)

The exported files are copies, so your original messages remain untouched.

## 🆘 Support

**Common Issues:**

1. **"Command not found: python3"**
   - macOS 10.14+ has Python 3 pre-installed
   - Try: `python3 --version` to verify

2. **Script hangs at "Loading contacts"**
   - This is normal - wait 2-5 minutes
   - Large contact lists take time to process

3. **Some contacts didn't match**
   - Check that contacts have phone numbers saved
   - Script shows match statistics at the end

## 📦 Distribution

Feel free to share this tool! It's free to use and modify.

**Ways to share:**
- Direct file sharing (email, cloud storage)
- GitHub repository
- Personal website

## 🎓 Technical Details

**For developers:**
- Pure Python 3, no external dependencies
- Uses sqlite3 to read Messages database
- AppleScript for contact name resolution
- Binary plist parsing for modern message format
- Graceful error handling and chunk-based processing

## ⚖️ License

Free to use, modify, and distribute. No warranty provided.

Use at your own risk. This tool reads from Apple's Messages database but makes no modifications.

---

**Version 1.0.0** - February 2026

**Author:** Created with love for the iMessage community

**Questions?** Review the code - it's well-commented and easy to understand!
