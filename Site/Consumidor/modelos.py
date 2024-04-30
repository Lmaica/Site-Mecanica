from Site import db, app
from datetime import datetime, timezone


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requisitor = db.Column(db.String, unique=False)
    token = db.Column(db.Integer, nullable=False)
    data= db.Column(
        db.DateTime, default=datetime.now(timezone.utc).astimezone(), nullable=False
    )


with app.app_context():
    db.create_all()
