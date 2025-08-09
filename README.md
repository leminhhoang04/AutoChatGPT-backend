# Getting started

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Create `config.ini` based on `config-sample.ini`

3. Login account and then press 'enter' in the terminal to get cookies
```bash
python get_cookies.py
```

4. Run FastAPI server
```bash
fastapi run main.py
```
Note: If you do not want to run in **headless mode** (for debugging purposes), set `headless = False` in `config.ini`.

# Find Chrome version

## Windows

```bash
Get-ChildItem -Path "C:\Program Files*\" -Filter chrome.exe -Recurse -ErrorAction SilentlyContinue
(Get-Item "C:\path\to\chrome.exe").VersionInfo.ProductVersion
```

## Debian/Ubuntu (Linux)

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
google-chrome --version
```