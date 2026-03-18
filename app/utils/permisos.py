def es_superadmin(membresia):
    return membresia.rol == 'superadmin'

def es_admin(membresia):
    return membresia.rol == 'admin'