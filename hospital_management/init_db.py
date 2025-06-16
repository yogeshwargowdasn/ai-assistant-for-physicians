from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    print(" Tables created successfully!")

    # Check if default admin already exists
    if not User.query.filter_by(username='admin123').first():
        admin_user = User(
            username='admin123',
            password=generate_password_hash('adminpass', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(" Default admin user created! (username: admin123, password: adminpass)")
    else:
        print(" Default admin user already exists.")
