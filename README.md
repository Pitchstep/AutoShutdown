# AutoShutdown v1.00
 ### Now works on macOS!
 
This program simply shuts off your computer at your desired time.

## macOS Installation & Important Fix for "Damaged" Error

**If macOS says “AutoShutdown is damaged and can’t be opened. You should move it to the Trash”: this is normal for unsigned apps downloaded from the internet. The app is NOT damaged!**

To fix this:
1. Download and double-click the .zip to extract `AutoShutdown.app`
2. Move the .app to your **Applications** folder (optional but recommended)
3. Open **Terminal** (Cmd + Space → type "Terminal" → Enter)
4. Copy-paste this command and press Enter:

`xattr -cr /Applications/AutoShutdown.app`

- Or drag the .app from Finder into Terminal after typing `xattr -cr ` (with a space) — it auto-fills the path
5. Now double-click the app again.
6. If you see "AutoShutdown can't be opened because Apple cannot check it for malicious software" → click **OK**, then go to **System Settings → Privacy & Security** → scroll down → click **Open Anyway** (may ask for password).

Done! The app should launch normally after this.

(Test mode is on by default — flip the switch when ready for real shutdowns. macOS will prompt for your password during actual shutdown — that's expected.)

Apple Gatekeeper quarantines downloaded unsigned apps for security. This is a free/open-source tool, so no $99/year Apple signing (yet).

*Made in Python*
