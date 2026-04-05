"""
Ticket model 
CSS-22 (create), CSS-24 (update), CSS-25 (assign), CSS-26 (close).
"""
 
from datetime import datetime, timezone
from .. import db
 
 
class TicketType:
    SERVICE  = "Service"
    BUG      = "Bug"
    CRITICAL = "Critical"
 
    ALL = [SERVICE, BUG, CRITICAL]
 
    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.ALL
 
 
class TicketStatus:
    TODO        = "Todo"
    IN_PROGRESS = "In Progress"
    DONE        = "Done"
 
    ALL = [TODO, IN_PROGRESS, DONE]
 
    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.ALL
 
 
class Ticket(db.Model):
    __tablename__ = "tickets"
 
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        nullable=True)
    type        = db.Column(db.String(20),  nullable=False, default=TicketType.SERVICE)
    status      = db.Column(db.String(20),  nullable=False, default=TicketStatus.TODO)
 
    # True = High priority, False = Normal
    priority    = db.Column(db.Boolean, nullable=False, default=False)
 
    # Who opened the ticket
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
 
    # Which technician is handling it 
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
 
    created_at  = db.Column(db.DateTime, nullable=False,
                            default=lambda: datetime.now(timezone.utc))
 
    # Due date — set when creating/updating; 
    done_by     = db.Column(db.DateTime, nullable=True)
 
    # Filled in when status transitions to Done (CSS-26)
    closed_at   = db.Column(db.DateTime, nullable=True)
 
    
    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        backref=db.backref("tickets_created", lazy="dynamic"),
    )
    assignee = db.relationship(
        "User",
        foreign_keys=[assignee_id],
        backref=db.backref("tickets_assigned", lazy="dynamic"),
    )
 

    @property
    def customer_name(self) -> str:
        return self.customer.username if self.customer else "—"
 
    def is_open(self) -> bool:
        return self.status == TicketStatus.TODO
 
    def is_in_progress(self) -> bool:
        return self.status == TicketStatus.IN_PROGRESS
 
    def is_closed(self) -> bool:
        return self.status == TicketStatus.DONE
 
    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "title":       self.title,
            "description": self.description,
            "type":        self.type,
            "status":      self.status,
            "priority":    self.priority,
            "customer": {
                "id":       self.customer_id,
                "username": self.customer.username if self.customer else None,
            },
            "assignee": {
                "id":       self.assignee_id,
                "username": self.assignee.username if self.assignee else None,
            } if self.assignee_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "done_by":    self.done_by.isoformat()    if self.done_by    else None,
            "closed_at":  self.closed_at.isoformat()  if self.closed_at  else None,
        }
 