"""
TicketReply — one row per comment left on a ticket.
Any authenticated user who can see the ticket can comment on it.
"""

from datetime import datetime, timezone
from .. import db


class TicketReply(db.Model):
    __tablename__ = "ticket_replies"

    id         = db.Column(db.Integer, primary_key=True)
    ticket_id  = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey("users.id"),   nullable=False)
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    author = db.relationship(
        "User",
        foreign_keys=[author_id],
        backref=db.backref("replies_written", lazy="dynamic"),
    )

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "ticket_id": self.ticket_id,
            "author": {
                "id":       self.author_id,
                "username": self.author.username if self.author else None,
            },
            "body":       self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }