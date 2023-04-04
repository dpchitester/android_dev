import js2py

with open("blog.js","r") as fh:
    txt = fh.read()

pyth = js2py.eval_js6(txt)

with open("blog.py", "w") as fh:
    fh.write(txt)
    
