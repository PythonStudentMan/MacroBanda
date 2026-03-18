import re

def generar_slug(nombre):
    slug = nombre.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug