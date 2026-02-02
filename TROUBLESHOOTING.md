# APK Purifier - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### Issue 1: "Failed to recompile APK"

**Symptoms:**
- Error message: "Failed to recompile APK"
- Processing fails at recompilation step
- No output APK generated

**Possible Causes:**
1. **Complex APK structure** - Heavily obfuscated or complex APKs
2. **Resource conflicts** - Invalid or conflicting resources
3. **AAPT errors** - Android Asset Packaging Tool issues
4. **Memory limitations** - Insufficient system memory
5. **Corrupted decompilation** - Issues during decompilation step

**Solutions:**

#### Solution 1: Use Debug Tool
```bash
python debug_apk.py path/to/your/app.apk
```
This will help identify exactly where the process fails.

#### Solution 2: Check System Resources
- Ensure you have at least 4GB RAM available
- Close other memory-intensive applications
- Check available disk space (need ~3x APK size free)

#### Solution 3: Try Different APK
- Test with a simpler APK first
- Avoid heavily obfuscated apps
- Try APKs from trusted sources

#### Solution 4: Manual APKTool Testing
```bash
# Test APKTool directly
cd tools
java -jar apktool.jar d path/to/app.apk -o test_output
java -jar apktool.jar b test_output -o test_rebuilt.apk
```

#### Solution 5: Update Java
- Ensure Java 8 or higher is installed
- Try with different Java versions if available
- Check Java memory settings

### Issue 2: Logging Not Showing in GUI

**Symptoms:**
- Logs tab remains empty
- No progress information displayed
- Silent failures

**Solutions:**

#### Solution 1: Check Log Files
Logs are saved to: `~/.apk_purifier/logs/apk_purifier.log`

#### Solution 2: Enable Verbose Logging
```python
# In main.py, change logging level
setup_logging(logging.DEBUG)
```

#### Solution 3: Use CLI for Detailed Output
```bash
python src/cli.py purify app.apk --verbose
```

### Issue 3: APK Signing Failures

**Symptoms:**
- "Failed to sign APK" error
- Unsigned APK generated
- Installation fails on Android

**Solutions:**

#### Solution 1: Check uber-apk-signer
```bash
cd tools
java -jar uber-apk-signer.jar --version
```

#### Solution 2: Use Debug Keystore
- Let APK Purifier use default debug keystore
- Don't specify custom keystore unless necessary

#### Solution 3: Manual Signing
```bash
cd tools
java -jar uber-apk-signer.jar --apks path/to/unsigned.apk --debug
```

### Issue 4: "Invalid APK file" Error

**Symptoms:**
- APK file rejected during validation
- Cannot add APK to processing list

**Solutions:**

#### Solution 1: Verify APK Integrity
```bash
# Check if APK is valid ZIP file
unzip -t app.apk
```

#### Solution 2: Re-download APK
- Download APK again from original source
- Verify file wasn't corrupted during download

#### Solution 3: Check File Extension
- Ensure file has .apk extension
- Rename if necessary: `mv app.zip app.apk`

### Issue 5: Java Not Found

**Symptoms:**
- "Java not found" error
- Installation test fails
- Tools don't work

**Solutions:**

#### Solution 1: Install Java
**Windows:**
```bash
# Download from https://openjdk.org/
# Or use chocolatey
choco install openjdk
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install openjdk-11-jdk

# CentOS/RHEL
sudo dnf install java-11-openjdk-devel
```

#### Solution 2: Set JAVA_HOME
**Windows:**
```cmd
set JAVA_HOME=C:\Program Files\Java\jdk-11
set PATH=%JAVA_HOME%\bin;%PATH%
```

**Linux:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
export PATH=$JAVA_HOME/bin:$PATH
```

### Issue 6: Permission Denied Errors

**Symptoms:**
- Cannot write to output directory
- Permission denied when creating files
- Access denied errors

**Solutions:**

#### Solution 1: Run as Administrator (Windows)
- Right-click on command prompt
- Select "Run as administrator"
- Run APK Purifier from elevated prompt

#### Solution 2: Check Directory Permissions (Linux)
```bash
# Make sure you have write permissions
chmod 755 /path/to/output/directory
```

#### Solution 3: Change Output Location
- Use a directory you have write access to
- Avoid system directories
- Use your home directory or desktop

### Issue 7: Out of Memory Errors

**Symptoms:**
- Java heap space errors
- Application crashes during processing
- System becomes unresponsive

**Solutions:**

#### Solution 1: Increase Java Memory
```bash
# Set Java memory options
export JAVA_OPTS="-Xmx4g -Xms1g"
```

#### Solution 2: Process Smaller APKs
- Try with APKs under 50MB first
- Process one APK at a time
- Close other applications

#### Solution 3: Use 64-bit Java
- Ensure you're using 64-bit Java
- 32-bit Java has memory limitations

## 🛠 Advanced Troubleshooting

### Enable Debug Mode

1. **GUI Debug Mode:**
```python
# In src/main.py, modify setup_logging call
setup_logging(logging.DEBUG)
```

2. **CLI Debug Mode:**
```bash
python src/cli.py purify app.apk --verbose
```

### Check System Requirements

**Minimum Requirements:**
- Python 3.8+
- Java 8+
- 4GB RAM
- 2GB free disk space

**Recommended:**
- Python 3.9+
- Java 11+
- 8GB RAM
- 5GB free disk space

### Log Analysis

**Log Locations:**
- GUI logs: `~/.apk_purifier/logs/apk_purifier.log`
- Temporary files: `~/.apk_purifier/temp/`
- Backups: `~/.apk_purifier/backups/`

**Common Log Patterns:**
```
ERROR - APKTool decompilation failed: aapt error
→ AAPT resource compilation issue

ERROR - Failed to recompile APK: duplicate entry
→ Resource duplication problem

ERROR - Java heap space
→ Memory issue, increase Java heap size
```

### Performance Optimization

1. **Increase Java Memory:**
```bash
export JAVA_OPTS="-Xmx8g -Xms2g"
```

2. **Use SSD Storage:**
- Process files on SSD for better performance
- Avoid network drives

3. **Close Other Applications:**
- Free up system memory
- Reduce CPU usage

## 🆘 Getting Help

### Before Reporting Issues

1. **Run Installation Test:**
```bash
python test_installation.py
```

2. **Test with Debug Tool:**
```bash
python debug_apk.py problematic_app.apk
```

3. **Check Logs:**
- Review log files for error details
- Include relevant log excerpts in reports

### Reporting Bugs

**Include the following information:**
- Operating system and version
- Python version (`python --version`)
- Java version (`java -version`)
- APK file size and source
- Complete error message
- Log file excerpts
- Steps to reproduce

**Contact Information:**
- **GitHub Issues:** https://github.com/bidhata/APK-Purifier/issues
- **Email:** me@krishnendu.com
- **Website:** https://krishnendu.com

### Community Support

- Check existing GitHub issues
- Search troubleshooting guide
- Ask questions in discussions
- Contribute solutions back to community

## 📋 Quick Checklist

**Before Processing APKs:**
- [ ] Java 8+ installed and in PATH
- [ ] Python 3.8+ with all dependencies
- [ ] APKTool and uber-apk-signer downloaded
- [ ] Sufficient disk space (3x APK size)
- [ ] Valid APK file (not corrupted)
- [ ] Write permissions to output directory

**If Processing Fails:**
- [ ] Check logs for error details
- [ ] Run debug tool on problematic APK
- [ ] Try with simpler APK first
- [ ] Verify system requirements
- [ ] Check available memory and disk space
- [ ] Test APKTool manually

**For Best Results:**
- [ ] Use APKs under 100MB when possible
- [ ] Process one APK at a time initially
- [ ] Keep original APKs as backup
- [ ] Test on simple APKs first
- [ ] Monitor system resources during processing