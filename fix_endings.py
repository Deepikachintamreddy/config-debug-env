import os
for r,d,fs in os.walk("server"):
    if "__pycache__" in r: continue
    for fn in fs:
        if not fn.endswith(".py"): continue
        p = os.path.join(r,fn)
        fh = open(p,"rb")
        data = fh.read()
        fh.close()
        fh = open(p,"wb")
        fh.write(data.replace(b"\r\n",b"\n"))
        fh.close()
        print(p, len(data))
