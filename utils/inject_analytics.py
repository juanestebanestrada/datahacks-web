import os
import re

analytics_code = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-K1C0H54WYE"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-K1C0H54WYE');
  </script>"""

directory = "website"
html_files = []

# Only target the static files directly in the website/ directory
for f in os.listdir(directory):
    if f.endswith(".html"):
        html_files.append(os.path.join(directory, f))

print(f"Injecting Google Analytics into {len(html_files)} static files...")

modified_count = 0

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if already has G-K1C0H54WYE
        if "G-K1C0H54WYE" in content:
            print(f"  [Skipped] {filepath} already has the tag.")
            continue
        
        # Locate the <head> tag (case-insensitive, optional spaces)
        head_match = re.search(r'<head\s*[^>]*>', content, re.IGNORECASE)
        if head_match:
            insert_pos = head_match.end()
            new_content = content[:insert_pos] + "\n" + analytics_code + content[insert_pos:]
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"  [Injected] {filepath}")
            modified_count += 1
        else:
            print(f"  [Warning] <head> tag not found in {filepath}")
    except Exception as e:
        print(f"  [Error] Failed to process {filepath}: {e}")

print(f"Completed. Modified {modified_count} files.")
