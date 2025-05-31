#!/usr/bin/env python3
import os
import re
import subprocess
from bs4 import BeautifulSoup

# --- CONFIG ---
PORTFOLIO_DIR = r"C:\Users\alroo\OneDrive\Desktop\portfolio"
HTML_FILE     = "index.html"
SCRIPT_FILE   = "script.js"

# Helper to run a command and capture exit code
def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

# 1) cd into your repo
os.chdir(PORTFOLIO_DIR)

# 2) Patch index.html
with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

hours_tag = soup.find(id="study-hours-value")
current = int(hours_tag.text)
new_hours = current + 2
hours_tag.string = str(new_hours)

new_pct = f"{new_hours/10000*100:.2f}%"
soup.find(id="study-hours-percentage").string = new_pct

bar = soup.find(id="study-skill-bar-level")
styles = dict(item.split(":",1) for item in bar["style"].rstrip(";").split(";"))
styles["width"] = new_pct
bar["style"] = "; ".join(f"{k.strip()}: {v.strip()}" for k,v in styles.items()) + ";"

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

# 3) Patch script.js fallback template
js = open(SCRIPT_FILE, "r", encoding="utf-8").read()

js = re.sub(
    r'(<span class="percentage" style="margin-left: 12px;">)[\d.]+% ',
    lambda m: m.group(1) + new_pct + " ",
    js
)
js = re.sub(
    r'(<div class="study-count">)\d+ / 10,000',
    lambda m: m.group(1) + f"{new_hours} / 10,000",
    js
)
js = re.sub(
    r'(style="width: )[\d.]+%;',
    lambda m: m.group(1) + new_pct + ";",
    js
)

with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
    f.write(js)

# 4) Git: add, then commit only if there are staged changes
run(["git", "add", "."])
# git diff-index returns 1 if there are staged changes vs HEAD
if run(["git", "diff-index", "--quiet", "HEAD"]) != 0:
    run(["git", "commit", "-m", "adding hours"])
    run(["git", "push"])
else:
    print("No changes to commit.")
