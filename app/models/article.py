"""
Article model
CSS-35 (create), CSS-36 (update), CSS-37 (view/list), CSS-38 (search).
"""

from datetime import datetime, timezone
from .. import db


class ArticleType:
    MANUAL          = "Manual"
    TUTORIAL        = "Tutorial"
    TROUBLESHOOTING = "Troubleshooting"
    FAQ             = "FAQ"
    SECURITY        = "Security"

    ALL = [MANUAL, TUTORIAL, TROUBLESHOOTING, FAQ, SECURITY]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.ALL


class Article(db.Model):
    __tablename__ = "articles"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text,        nullable=False)
    type        = db.Column(db.String(30),  nullable=False, default=ArticleType.FAQ)
    attachments = db.Column(db.Text,        nullable=True)

    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))

    author = db.relationship(
        "User",
        foreign_keys=[author_id],
        backref=db.backref("articles_created", lazy="dynamic"),
    )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "title":       self.title,
            "content":     self.content,
            "type":        self.type,
            "attachments": self.attachments.split(",") if self.attachments else [],
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "author": {
                "id":       self.author_id,
                "username": self.author.username if self.author else None,
            },
        }
