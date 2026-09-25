# -*- coding: utf-8 -*-
import re, sys
def norm(t):
    t = t.replace("´ı", "í").replace("`ı", "ì")
    for a, b in (("´a","á"),("´e","é"),("´o","ó"),("´u","ú"),("´A","Á"),("´E","É"),("´I","Í"),("´O","Ó"),("´U","Ú"),("˜n","ñ"),("˜N","Ñ"),("¨u","ü"),("ﬁ","fi"),("ﬂ","fl")):
        t = t.replace(a, b)
    return t
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    f, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    lines = open(f, encoding="utf-8", errors="replace").read().split("\n")[a-1:b]
    print(re.sub(r"\n\s*\n+", "\n", norm("\n".join(lines))))
