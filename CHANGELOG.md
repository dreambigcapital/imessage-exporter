# Changelog

All notable changes to iMessage Exporter will be documented in this file.

## [1.0.0] - 2026-02-07

### Features
- Initial release
- Export all iMessage conversations to HTML
- Automatic contact name resolution (matches phone numbers to contact names)
- Embedded images and videos in HTML output
- Organized folder structure (one folder per contact)
- Support for large contact lists (1000+)
- Chunk-based loading with timeout handling
- Binary plist message decoding
- Attachment copying and organization
- Progress indicators for long operations
- Beautiful iMessage-style HTML formatting

### Technical Details
- Pure Python 3 implementation
- No external dependencies required
- AppleScript integration for contact access
- SQLite database reading for messages
- Graceful error handling
- Production-ready code

### Known Limitations
- Requires macOS 10.14 or higher
- Terminal needs Full Disk Access and Contacts permissions
- Some very old messages (<1%) may not decode properly
- Large contact lists (1000+) take 2-5 minutes to load
- Chunk timeouts may cause some contacts to be missed

### Performance
- Successfully tested with:
  - 579 conversations
  - 76,000+ messages
  - 12,000+ attachments
  - 1,125 contacts
  - ~5 minute total export time

---

## Future Improvements (Community Suggestions Welcome)
- [ ] Search functionality in exported HTML
- [ ] Dark mode for HTML output
- [ ] Export date range filtering
- [ ] Group chat participant names
- [ ] Emoji and reaction display improvements
- [ ] PDF export option
- [ ] GUI application wrapper
- [ ] Windows/Linux support (via alternative message sources)
