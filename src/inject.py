import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
payload=open(os.path.join(HERE,"payload.json"), encoding="utf-8").read()
head=open(os.path.join(HERE,"t.head.html"), encoding="utf-8").read()
body=open(os.path.join(HERE,"t.body.html"), encoding="utf-8").read()
js1 =open(os.path.join(HERE,"t.js1.html"), encoding="utf-8").read().replace("__PAYLOAD__", payload)
js2 =open(os.path.join(HERE,"t.js2.html"), encoding="utf-8").read()
out=head+"\n"+body+"\n"+js1+"\n"+js2+"\n"
dst = os.path.join(HERE, "..", "index.html")
open(dst,"w", encoding="utf-8").write(out)
out = dst

root = HERE
while root != os.path.dirname(root) and not os.path.isdir(os.path.join(root, "projects")):
    root = os.path.dirname(root)
tools = os.path.join(root, "catalog", "tools")
subprocess.run([sys.executable, os.path.join(tools, "wrap_for_pages.py"), out])
subprocess.run([sys.executable, os.path.join(tools, "add_catalog_link.py"), out])
print("wrote", os.path.normpath(out), f"{os.path.getsize(out):,} bytes")
