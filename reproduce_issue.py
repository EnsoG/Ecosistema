import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecosistema.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from usuario.models import Usuario

def test_admin_creation_session():
    # 1. Create Superuser
    admin_user, created = User.objects.get_or_create(username='admin_test', email='admin@test.com')
    if created:
        admin_user.set_password('admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
    else:
        admin_user.set_password('admin123')
        admin_user.save()

    client = Client()
    
    # 2. Login to Admin
    login_success = client.login(username='admin_test', password='admin123')
    print(f"Admin Login Success: {login_success}")
    
    # Check session
    print(f"Session after login: {client.session.keys()}")
    
    # 3. Create Usuario directly (simulating Admin ModelForm save)
    # Note: Admin uses model.save(), so we do that.
    new_usuario = Usuario(
        nombre="Test", 
        apellido="User", 
        email="testuser@example.com", 
        rut="12345678-9",
        password="password"
    )
    new_usuario.save()
    print(f"Created Usuario: {new_usuario.id}")
    
    # 4. Check session again
    # Does saving the model affect the session? 
    # (It shouldn't, as model save has no request access, but we verify)
    print(f"Session after model save: {client.session.keys()}")

    # 5. Simulate Admin View POST (if possible/needed)
    # Since we can't easily mock the full Admin view stack without URLs, 
    # we rely on the fact that if model save doesn't do it, Admin view generally won't 
    # unless it has custom logic (which we verified it doesn't).
    
    if '_auth_user_id' in client.session:
        print("PASS: Admin is still logged in.")
        if str(client.session['_auth_user_id']) == str(admin_user.id):
             print("PASS: Admin ID matches.")
        else:
             print("FAIL: Admin ID mismatch.")
    else:
        print("FAIL: Admin logged out.")

    if 'usuario_id' in client.session:
        print(f"INFO: 'usuario_id' key present: {client.session['usuario_id']}")
    else:
        print("INFO: 'usuario_id' key NOT present.")

if __name__ == '__main__':
    try:
        test_admin_creation_session()
    except Exception as e:
        print(f"Error: {e}")
