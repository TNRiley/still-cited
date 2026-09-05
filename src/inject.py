payload=open("payload.json", encoding="utf-8").read()
head=open("t.head.html", encoding="utf-8").read()
body=open("t.body.html", encoding="utf-8").read()
js1 =open("t.js1.html", encoding="utf-8").read().replace("__PAYLOAD__", payload)
js2 =open("t.js2.html", encoding="utf-8").read()
out=head+"\n"+body+"\n"+js1+"\n"+js2+"\n"
dst="/Users/trevor/Development/Claude Quick Projects/nightly/builds/2026-09-05-still-cited/index.html"
import os; os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst,"w", encoding="utf-8").write(out)
print("wrote", dst, f"{len(out)/1e6:.2f} MB")
