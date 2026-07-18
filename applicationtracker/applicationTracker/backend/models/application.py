from extensions import db
from datetime import datetime, timezone

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    date_applied = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    screenshot_path = db.Column(db.String(255), nullable=True)
    cover_letter_path = db.Column(db.String(255), nullable=True)
    page_content = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'status': self.status,
            'date_applied': self.date_applied.isoformat() if self.date_applied else None,
            'notes': self.notes,
            'url': self.url,
            'screenshot_path': self.screenshot_path,
            'cover_letter_path': self.cover_letter_path,
            'page_content': self.page_content
        }