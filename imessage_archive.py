#!/usr/bin/env python3
"""
iMessage Exporter - Production Ready
Exports chats with proper contact names and message text
"""

import os
import sqlite3
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import re

print("🛑 Closing Messages and Contacts apps...")
for proc in ['Messages', 'Contacts', 'imagent', 'contactsd']:
    subprocess.run(['killall', proc], stderr=subprocess.DEVNULL)
print("✓ Done\n")

# Get output directory
print("📁 Where to save chats?")
output = input("(Press Enter for ~/Desktop/iMessage_Export): ").strip()
if not output:
    output = "~/Desktop/iMessage_Export"
output_dir = Path(os.path.expanduser(output))
output_dir.mkdir(parents=True, exist_ok=True)

# Load contacts - faster method using chunks
print("\n📇 Loading contacts...")
contact_map = {}

try:
    # Get count first
    count_script = 'tell application "Contacts" to count people'
    result = subprocess.run(['osascript', '-e', count_script], capture_output=True, text=True, timeout=10)
    total_contacts = int(result.stdout.strip()) if result.returncode == 0 else 0
    
    if total_contacts == 0:
        print("   No contacts found\n")
    else:
        print(f"   Found {total_contacts} contacts, loading in chunks...")
        print("   (This may take 2-5 minutes for large contact lists)\n")
        
        # Load in chunks of 50 (smaller = faster)
        chunk_size = 50
        loaded = 0
        
        for start in range(1, total_contacts + 1, chunk_size):
            end = min(start + chunk_size - 1, total_contacts)
            
            chunk_script = f'''
tell application "Contacts"
    set output to ""
    repeat with i from {start} to {end}
        try
            set p to person i
            set pName to name of p
            if (count of phones of p) > 0 then
                set output to output & pName & "|" & (value of item 1 of phones of p) & linefeed
            end if
        end try
    end repeat
    return output
end tell
'''
            
            try:
                result = subprocess.run(['osascript', '-e', chunk_script], capture_output=True, text=True, timeout=90)
                
                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if '|' not in line:
                            continue
                        parts = line.split('|', 1)
                        if len(parts) == 2:
                            name, phone = parts[0].strip(), parts[1].strip()
                            if name and phone:
                                digits = re.sub(r'\D', '', phone)
                                if len(digits) >= 10:
                                    # Store ALL variations
                                    contact_map[digits] = name
                                    contact_map[digits[-10:]] = name
                                    if len(digits) == 10:
                                        contact_map['1' + digits] = name
                                    if len(digits) == 11 and digits[0] == '1':
                                        contact_map[digits[1:]] = name
                                    loaded += 1
            
            except subprocess.TimeoutExpired:
                print(f"\n   ⚠️  Chunk {start}-{end} timed out, skipping...")
            except Exception as e:
                print(f"\n   ⚠️  Chunk {start}-{end} failed: {e}")
            
            print(f"   Progress: {end}/{total_contacts} ({int(end/total_contacts*100)}%) - loaded {loaded} contacts...", end='\r')
        
        print(f"\n✓ Loaded {loaded} contacts ({len(contact_map)} variations)")
        
        # Show samples
        if contact_map:
            print("\nSample mappings:")
            for phone, name in list(contact_map.items())[:5]:
                print(f"  {phone} → {name}")
        print()

except Exception as e:
    print(f"⚠️  Could not load contacts: {e}")
    print("   Will use phone numbers\n")

# Helper functions
def get_name(phone_or_email):
    if not phone_or_email:
        return "Unknown"
    
    if '@' in phone_or_email:
        return phone_or_email
    
    # Strip ALL non-digits including the + sign
    digits = re.sub(r'\D', '', phone_or_email)
    
    if not digits:
        return phone_or_email
    
    # Try MANY variations
    variations = [
        digits,                                          # Full: 16824380581
        digits[-10:],                                    # Last 10: 6824380581
        digits[-11:] if len(digits) >= 11 else None,   # Last 11: 16824380581
        '1' + digits if len(digits) == 10 else None,   # Add 1: 16824380581
        digits[1:] if len(digits) == 11 and digits[0] == '1' else None,  # Remove 1: 6824380581
        digits[2:] if len(digits) == 12 and digits[0] == '1' else None,  # Remove country+1
    ]
    
    # Try each variation
    for var in variations:
        if var and var in contact_map:
            return contact_map[var]
    
    # If still not found, return the original
    return phone_or_email

def clean(text):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', str(text)).strip()

def extract_text(attributed_body):
    """Extract plain text from attributed body binary data"""
    if not attributed_body:
        return None
    
    try:
        # Try plistlib first (proper way)
        import plistlib
        try:
            plist = plistlib.loads(attributed_body)
            
            # Method 1: Check for NSString directly
            if isinstance(plist, dict):
                if 'NSString' in plist:
                    return plist['NSString']
                
                # Method 2: Check $objects array
                if '$objects' in plist:
                    for obj in plist['$objects']:
                        if isinstance(obj, str) and len(obj) > 0:
                            # Skip metadata strings
                            if obj not in ['$null', 'NSAttributedString', 'NSMutableAttributedString', 
                                          'NSString', 'NSMutableString', 'NSObject', '__kIMMessagePartAttributeName']:
                                return obj
        except:
            pass
        
        # Fallback: Manual extraction from binary
        decoded = attributed_body.decode('latin-1', errors='ignore')
        
        # Pattern 1: Text after \x84\x01+ marker (most common)
        match = re.search(r'\x84\x01\+F(.+?)(?:\x86|\x84)', decoded, re.DOTALL)
        if match:
            text = match.group(1)
            # Clean up any embedded null bytes or control characters
            text = ''.join(c if 32 <= ord(c) < 127 or c in '\n\r\t' else '' for c in text)
            if len(text.strip()) > 0:
                return text.strip()
        
        # Pattern 2: Look for readable text chunks
        # Find all sequences of printable characters
        text_chunks = re.findall(r'[\x20-\x7E\n\r\t]{3,}', decoded)
        
        # Filter out metadata/junk
        valid_chunks = []
        junk_keywords = ['NSMutableAttributedString', 'NSAttributedString', 'NSObject', 
                        'NSString', 'NSDictionary', 'NSNumber', 'NSValue', 'streamtyped',
                        '__kIMMessagePartAttributeName', 'NSMutableString']
        
        for chunk in text_chunks:
            # Skip if it's mostly junk
            if any(junk in chunk for junk in junk_keywords):
                continue
            # Skip if it's too short
            if len(chunk.strip()) < 3:
                continue
            # Skip if it's mostly non-alphanumeric
            alnum_count = sum(c.isalnum() or c.isspace() for c in chunk)
            if alnum_count / len(chunk) < 0.7:
                continue
            
            valid_chunks.append(chunk.strip())
        
        # Return the longest valid chunk
        if valid_chunks:
            return max(valid_chunks, key=len)
    
    except Exception as e:
        pass
    
    return None

# Connect to Messages database
db_path = Path.home() / "Library/Messages/chat.db"
if not db_path.exists():
    print("❌ Messages database not found!")
    exit(1)

print("📱 Reading Messages database...")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cursor = conn.cursor()

# Get all chats
cursor.execute("""
    SELECT 
        c.chat_identifier,
        c.display_name,
        COUNT(m.ROWID) as msg_count
    FROM chat c
    LEFT JOIN chat_message_join cmj ON c.ROWID = cmj.chat_id
    LEFT JOIN message m ON cmj.message_id = m.ROWID
    GROUP BY c.ROWID
    HAVING msg_count > 0
    ORDER BY msg_count DESC
""")

chats = cursor.fetchall()
print(f"✓ Found {len(chats)} conversations\n")

# Export each chat
stats = {'chats': 0, 'messages': 0, 'attachments': 0, 'matched': 0}

for i, (chat_id, display_name, msg_count) in enumerate(chats, 1):
    # Get contact name
    contact = display_name or get_name(chat_id)
    if contact != chat_id:
        stats['matched'] += 1
    
    contact = clean(contact) or "Unknown"
    
    print(f"[{i}/{len(chats)}] {contact[:40]} ({msg_count} msgs)...", end='\r')
    
    # Create folders
    chat_dir = output_dir / contact
    chat_dir.mkdir(parents=True, exist_ok=True)
    att_dir = chat_dir / "attachments"
    att_dir.mkdir(parents=True, exist_ok=True)
    
    # Get messages
    cursor.execute("""
        SELECT 
            m.ROWID,
            m.text,
            m.attributedBody,
            m.date,
            m.is_from_me,
            m.cache_has_attachments
        FROM message m
        JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
        JOIN chat c ON cmj.chat_id = c.ROWID
        WHERE c.chat_identifier = ?
        ORDER BY m.date ASC
    """, (chat_id,))
    
    messages = cursor.fetchall()
    stats['messages'] += len(messages)
    
    # Create HTML
    html_file = chat_dir / f"{contact}_chat.html"
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{contact}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .message {{ margin: 10px 0; padding: 10px 15px; border-radius: 18px; max-width: 70%; clear: both; word-wrap: break-word; }}
        .from-me {{ background: #007AFF; color: white; float: right; }}
        .from-them {{ background: #E5E5EA; color: black; float: left; }}
        .timestamp {{ font-size: 11px; color: #999; margin: 5px 10px; clear: both; }}
        .attachment {{ max-width: 300px; border-radius: 10px; margin: 5px 0; }}
        h1 {{ text-align: center; }}
        .clear {{ clear: both; }}
    </style>
</head>
<body>
    <h1>{contact}</h1>
""")
        
        for msg_id, text, attributed_body, date, is_from_me, has_att in messages:
            # Convert timestamp
            if date:
                dt = datetime(2001, 1, 1) + timedelta(seconds=date/1000000000)
                timestamp = dt.strftime("%b %d, %Y at %I:%M %p")
            else:
                timestamp = "Unknown"
            
            sender = "You" if is_from_me else contact
            css_class = "from-me" if is_from_me else "from-them"
            
            f.write(f'<div class="timestamp">{sender} - {timestamp}</div>\n')
            f.write(f'<div class="message {css_class}">\n')
            
            # Extract message text
            message_text = text or extract_text(attributed_body)
            
            if message_text:
                safe_text = str(message_text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                f.write(f'<p>{safe_text}</p>\n')
            
            # Attachments
            if has_att:
                cursor.execute("""
                    SELECT a.filename, a.mime_type
                    FROM message_attachment_join maj
                    JOIN attachment a ON maj.attachment_id = a.ROWID
                    WHERE maj.message_id = ?
                """, (msg_id,))
                
                for att_filename, mime_type in cursor.fetchall():
                    if att_filename:
                        att_path = Path(att_filename.replace('~', str(Path.home())))
                        
                        if att_path.exists():
                            dest_name = att_path.name
                            dest = att_dir / dest_name
                            
                            counter = 1
                            while dest.exists():
                                dest = att_dir / f"{att_path.stem}_{counter}{att_path.suffix}"
                                counter += 1
                            
                            try:
                                shutil.copy2(att_path, dest)
                                rel_path = f"attachments/{dest.name}"
                                
                                if mime_type and 'image' in mime_type:
                                    f.write(f'<img src="{rel_path}" class="attachment"><br>\n')
                                elif mime_type and 'video' in mime_type:
                                    f.write(f'<video src="{rel_path}" class="attachment" controls></video><br>\n')
                                else:
                                    f.write(f'<a href="{rel_path}">📎 {dest.name}</a><br>\n')
                                
                                stats['attachments'] += 1
                            except:
                                pass
            
            f.write('</div>\n<div class="clear"></div>\n')
        
        f.write('</body></html>')
    
    stats['chats'] += 1

conn.close()

print(f"\n\n✅ DONE!")
print(f"   Exported: {stats['chats']} chats")
print(f"   Matched contacts: {stats['matched']}/{stats['chats']}")
print(f"   Messages: {stats['messages']:,}")
print(f"   Attachments: {stats['attachments']:,}")

# Show some unmatched numbers for debugging
if stats['matched'] < stats['chats']:
    print(f"\n📊 Analysis of unmatched numbers:")
    unmatched = []
    for chat_id, display_name, msg_count in chats:
        if not display_name:
            contact = get_name(chat_id)
            if contact == chat_id and '@' not in chat_id:  # Still a phone number
                digits = re.sub(r'\D', '', chat_id)
                unmatched.append(digits)
    
    if unmatched[:5]:
        print(f"   First 5 unmatched: {unmatched[:5]}")
        print(f"   Trying to find these in contact_map...")
        for num in unmatched[:5]:
            variations = [num, num[-10:], '1' + num if len(num) == 10 else None,
                         num[1:] if len(num) == 11 else None]
            print(f"   {num}: trying {[v for v in variations if v]} → ", end='')
            found = False
            for v in variations:
                if v and v in contact_map:
                    print(f"FOUND as '{v}' → {contact_map[v]}")
                    found = True
                    break
            if not found:
                print("NOT FOUND")

print(f"\n📁 Saved to: {output_dir}\n")
