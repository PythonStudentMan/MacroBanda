import pytest

@pytest.mark.skipif(True, reason='Ajusta la ruta /admin/only si la app usa otra ruta para endpoints admin.')
def test_admin_endpoint_requires_admin(client, seed_data):
    usuarios = seed_data['usuarios']
    client.post('/auth/login', data={'email': getattr(usuarios['u1'], 'email'), 'password': 'pass1'}, headers={'Host': 't1.localhost'})
    resp = client.get('/admin/only', headers={'Host': 't1.localhost'})
    assert resp.status_code(401, 403)
    client.post('/auth/login', data={'email': getattr(usuarios['admin'], 'email'), 'password': 'adminpass'}, headers={'Host': 't1.localhost'})
    resp2 = client.get('/admin/only', headers={'Host': 't1.localhost'})
    assert resp2.status_code == 200