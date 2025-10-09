after everything: 
enable the templatetags package:
sim/
 └─ templatetags/
    ├─ __init__.py
    └─ form_extras.py
At the top of index.html, add:
{% load form_extras %}
