import pytest

def _login(client, email, password, as_json=False, host=None):
    headers = {}
    if host:
        headers['Host'] = host
    if as_json:
        return client.post('/auth/login', json={'email': email, 'password': password}, headers=headers, follow_redirects=True)
    return client.post('/auth/login', data={'email': email, 'password': password}, headers=headers, follow_redirects=True)

def test_login_success(client, seed_data):
    u1 = seed_data['users']['u1']
    resp = _login(client, getattr(u1, 'email'), 'pass1', host='t1.localhost')
    assert resp.status_code in (200, 302)
    assert b'logout' in resp.data.lower() or b'token' in resp.data or b'bienvenido' in resp.data.lower()

def test_login_fail(client):
    resp = _login(client, 'noone@test', 'bad')
    assert resp.status_code in (401, 400, 200)
    assert b'invalid' in resp.data.lower() or b'cred' in resp.data.lower() or resp.status_code != 200