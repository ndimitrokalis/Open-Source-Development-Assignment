"""
Ticket management endpoints.


CSS-22  POST   /tickets                      — create a ticket
CSS-24  PUT    /tickets/<id>                 — update ticket fields
CSS-25  POST   /tickets/<id>/assign          — assign to a technician
CSS-26  POST   /tickets/<id>/close           — mark ticket as Done
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import login_required, current_user

from .. import db
from ..models.user import Role
from ..models.ticket import Ticket, TicketType, TicketStatus
from ..models.ticket_reply import TicketReply

tickets_bp = Blueprint("tickets", __name__)

# Helpers 

def _parse_done_by(raw: str | None) -> datetime | None:
    """Parse an ISO date/datetime string to UTC datetime, or return None."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _get_ticket_or_404(ticket_id: int):
    """Return (ticket, None) or (None, error_response)."""
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return None, (jsonify({"error": "Ticket not found."}), 404)
    return ticket, None


# Page routes

@tickets_bp.get("/tickets")
@login_required
def list_tickets():
    if current_user.role == Role.CUSTOMER:
        abort(403)
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template("tickets/tickets.html", tickets=tickets, view="all")


@tickets_bp.get("/tickets/my")
@login_required
def my_tickets():
    # only the current user's tickets, newest first
    tickets = (Ticket.query
               .filter_by(customer_id=current_user.id)
               .order_by(Ticket.created_at.desc())
               .all())
    return render_template("tickets/tickets.html", tickets=tickets, view="my")


# CSS-22  Create ticket   

@tickets_bp.post("/tickets")
@login_required
def create_ticket():
    data = request.get_json(silent=True) or {}

    title       = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip() or None
    ticket_type = (data.get("type") or TicketType.SERVICE).strip()
    priority    = bool(data.get("priority", False))
    done_by_raw = data.get("done_by")
    company_raw = (data.get("company") or "").strip() or None

    if not title:
        return jsonify({"error": "Title is required."}), 400
    if len(title) > 200:
        return jsonify({"error": "Title must be 200 characters or fewer."}), 400
    if not TicketType.is_valid(ticket_type):
        return jsonify({"error": f"Type must be one of: {', '.join(TicketType.ALL)}."}), 400

    done_by = _parse_done_by(done_by_raw)
    if done_by_raw and done_by is None:
        return jsonify({"error": "done_by must be a valid ISO date (YYYY-MM-DD)."}), 400

    customer_id = current_user.id
    if "customer_id" in data:
        if not Role.has_permission(current_user.role, Role.MANAGER):
            return jsonify({"error": "Only managers and admins can open tickets on behalf of others."}), 403
        customer_id = int(data["customer_id"])

    if company_raw:
        company = company_raw
    else:
        from ..models.user import User
        owner = User.query.get(customer_id)
        company = owner.company if owner else None

    ticket = Ticket(
        title=title,
        description=description,
        type=ticket_type,
        priority=priority,
        done_by=done_by,
        company=company,
        customer_id=customer_id,
        status=TicketStatus.TODO,
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify({"message": "Ticket created successfully.", "ticket": ticket.to_dict()}), 201


# CSS-24  Update ticket   

@tickets_bp.put("/tickets/<int:ticket_id>")
@login_required
def update_ticket(ticket_id: int):
    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err

    if current_user.role == Role.CUSTOMER and ticket.customer_id != current_user.id:
        return jsonify({"error": "You do not have permission to edit this ticket."}), 403

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No fields provided to update."}), 400

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return jsonify({"error": "Title cannot be empty."}), 400
        if len(title) > 200:
            return jsonify({"error": "Title must be 200 characters or fewer."}), 400
        ticket.title = title

    if "description" in data:
        ticket.description = (data["description"] or "").strip() or None

    if "type" in data:
        new_type = (data["type"] or "").strip()
        if not TicketType.is_valid(new_type):
            return jsonify({"error": f"Type must be one of: {', '.join(TicketType.ALL)}."}), 400
        ticket.type = new_type

    if "priority" in data:
        ticket.priority = bool(data["priority"])

    if "done_by" in data:
        done_by = _parse_done_by(data["done_by"])
        if data["done_by"] and done_by is None:
            return jsonify({"error": "done_by must be a valid ISO date (YYYY-MM-DD)."}), 400
        ticket.done_by = done_by

    if "company" in data:
        ticket.company = (data["company"] or "").strip() or None

    if "attachments" in data:
        raw = data["attachments"]
        if isinstance(raw, list):
            ticket.attachments = ",".join(f.strip() for f in raw if f.strip()) or None
        else:
            ticket.attachments = str(raw).strip() or None

    if "status" in data:
        if current_user.role == Role.CUSTOMER:
            return jsonify({"error": "Customers cannot change ticket status directly."}), 403
        new_status = (data["status"] or "").strip()
        if not TicketStatus.is_valid(new_status):
            return jsonify({"error": f"Status must be one of: {', '.join(TicketStatus.ALL)}."}), 400
        ticket.status = new_status

    db.session.commit()
    return jsonify({"message": "Ticket updated successfully.", "ticket": ticket.to_dict()}), 200


# CSS-25 Assign ticket 

@tickets_bp.post("/tickets/<int:ticket_id>/assign")
@login_required
def assign_ticket(ticket_id: int):
    if not Role.has_permission(current_user.role, Role.MANAGER):
        return jsonify({"error": "Only managers and admins can assign tickets."}), 403

    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err

    data = request.get_json(silent=True) or {}
    if "assignee_id" not in data:
        return jsonify({"error": "assignee_id is required (use null to unassign)."}), 400

    raw_assignee_id = data["assignee_id"]

    if raw_assignee_id is None:
        ticket.assignee_id = None
        if ticket.status == TicketStatus.IN_PROGRESS:
            ticket.status = TicketStatus.TODO
    else:
        from ..models.user import User
        assignee = User.query.get(int(raw_assignee_id))
        if assignee is None:
            return jsonify({"error": "Assignee user not found."}), 404
        if assignee.role != Role.TECHNICIAN:
            return jsonify({"error": "Tickets can only be assigned to technicians."}), 400
        if not assignee.is_active:
            return jsonify({"error": "Cannot assign to a disabled account."}), 400

        ticket.assignee_id = assignee.id
        if ticket.status == TicketStatus.TODO:
            ticket.status = TicketStatus.IN_PROGRESS

    db.session.commit()
    return jsonify({
        "message": "Ticket assigned successfully." if raw_assignee_id else "Ticket unassigned.",
        "ticket":  ticket.to_dict(),
    }), 200


# CSS-26 Close ticket 

@tickets_bp.post("/tickets/<int:ticket_id>/close")
@login_required
def close_ticket(ticket_id: int):
    if current_user.role == Role.CUSTOMER:
        return jsonify({"error": "Customers cannot close tickets."}), 403

    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err

    if current_user.role == Role.TECHNICIAN and ticket.assignee_id != current_user.id:
        return jsonify({"error": "You can only close tickets that are assigned to you."}), 403

    if ticket.status == TicketStatus.DONE:
        return jsonify({"message": "Ticket is already closed.", "ticket": ticket.to_dict()}), 200

    ticket.status    = TicketStatus.DONE
    ticket.closed_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"message": "Ticket closed successfully.", "ticket": ticket.to_dict()}), 200


#  Comments   

@tickets_bp.get("/tickets/<int:ticket_id>/comments")
@login_required
def get_comments(ticket_id: int):
    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err
    if current_user.role == Role.CUSTOMER and ticket.customer_id != current_user.id:
        return jsonify({"error": "You do not have permission to view this ticket."}), 403

    return jsonify({"ticket_id": ticket_id, "comments": [r.to_dict() for r in ticket.replies]}), 200


@tickets_bp.post("/tickets/<int:ticket_id>/comments")
@login_required
def add_comment(ticket_id: int):
    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err
    if current_user.role == Role.CUSTOMER and ticket.customer_id != current_user.id:
        return jsonify({"error": "You do not have permission to comment on this ticket."}), 403

    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()

    if not body:
        return jsonify({"error": "Comment body cannot be empty."}), 400
    if len(body) > 5000:
        return jsonify({"error": "Comment must be 5000 characters or fewer."}), 400

    reply = TicketReply(ticket_id=ticket_id, author_id=current_user.id, body=body)
    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Comment added.", "comment": reply.to_dict()}), 201


@tickets_bp.delete("/tickets/<int:ticket_id>/comments/<int:comment_id>")
@login_required
def delete_comment(ticket_id: int, comment_id: int):
    ticket, err = _get_ticket_or_404(ticket_id)
    if err:
        return err

    reply = TicketReply.query.filter_by(id=comment_id, ticket_id=ticket_id).first()
    if reply is None:
        return jsonify({"error": "Comment not found."}), 404

    if reply.author_id != current_user.id and not Role.has_permission(current_user.role, Role.MANAGER):
        return jsonify({"error": "You do not have permission to delete this comment."}), 403

    db.session.delete(reply)
    db.session.commit()
    return jsonify({"message": "Comment deleted."}), 200