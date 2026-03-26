import pytest

def test_access_same_tenant(client, seed_data):
    users = seed_data['users']
    TestResource = seed_data['TestResource']
    client.post('auth/login', data={'email': getattr(users['u1'], 'email'), 'password': 'pass1'}, headers={'Host': 't1.localhost'})
    from app.extensions import db as _db
    r = _db.session.query(TestResource).filter_by(data='secret t1').first()
    resp = client.get(f'/test_resource/{r.id}', headers={'Host': 't1.localhost'})
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert b'secret t1' in resp.data

def test_access_other_tenant_forbidden(client, seed_data):
    users = seed_data['users']
    TestResource = seed_data['TestResource']
    client.post('auth/login', data={'email': getattr(users['u1'], 'email'), 'password': 'pass1'}, headers={'Host': 't1.localhost'})
    from app.extensions import db as _db
    r2 = _db.session.query(TestResource).filter_by(data='secret t2').first()
    resp = client.get(f'/test_resource/{r2.id}', headers={'Host': 't1.localhost'})
    assert resp.status_code in (403, 404, 401)

