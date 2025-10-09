procsim/
├─ manage.py
├─ procsim/
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
└─ sim/
   ├─ __init__.py
   ├─ scheduler.py          # ← your file (unchanged)
   ├─ forms.py
   ├─ views.py
   ├─ urls.py
   ├─ utils.py              # SVG/ASCII helpers
   ├─ templates/
   │  └─ sim/
   │     ├─ base.html
   │     └─ index.html
   └─ static/               # (optional if you add custom CSS/JS later)
