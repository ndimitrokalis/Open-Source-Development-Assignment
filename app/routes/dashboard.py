from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models.user import User, Role
from ..models.ticket import Ticket, TicketType, TicketStatus
from ..models.ticket_reply import TicketReply

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():

    # ── Base query (customers see only their own tickets) ─────────────────────
    if current_user.role == Role.CUSTOMER:
        base_q = Ticket.query.filter_by(customer_id=current_user.id)
    else:
        base_q = Ticket.query

    # ── Ticket stats ──────────────────────────────────────────────────────────
    total_tickets       = base_q.count()
    open_tickets        = base_q.filter_by(status=TicketStatus.TODO).count()
    in_progress_tickets = base_q.filter_by(status=TicketStatus.IN_PROGRESS).count()
    done_tickets        = base_q.filter_by(status=TicketStatus.DONE).count()

    # Technician only
    assigned_tickets = (
        Ticket.query.filter_by(assignee_id=current_user.id)
        .filter(Ticket.status != TicketStatus.DONE)
        .count()
        if current_user.role == Role.TECHNICIAN else 0
    )
    critical_tickets = (
        Ticket.query.filter_by(assignee_id=current_user.id, type=TicketType.CRITICAL)
        .filter(Ticket.status != TicketStatus.DONE)
        .count()
        if current_user.role == Role.TECHNICIAN else 0
    )

    # Manager / admin only
    unassigned_tickets = (
        Ticket.query.filter_by(assignee_id=None)
        .filter(Ticket.status != TicketStatus.DONE)
        .count()
        if Role.has_permission(current_user.role, Role.MANAGER) else 0
    )
    active_technicians = (
        User.query.filter_by(role=Role.TECHNICIAN, active=True).count()
        if Role.has_permission(current_user.role, Role.MANAGER) else 0
    )

    # ── Admin: total users ────────────────────────────────────────────────────
    total_users = User.query.count() if current_user.role == Role.ADMIN else 0

    # ── Category breakdown ────────────────────────────────────────────────────
    service_count  = base_q.filter_by(type=TicketType.SERVICE).count()
    bug_count      = base_q.filter_by(type=TicketType.BUG).count()
    critical_count = base_q.filter_by(type=TicketType.CRITICAL).count()

    service_pct  = round(service_count  / total_tickets * 100) if total_tickets else 0
    bug_pct      = round(bug_count      / total_tickets * 100) if total_tickets else 0
    critical_pct = round(critical_count / total_tickets * 100) if total_tickets else 0

    # ── Recent activity ───────────────────────────────────────────────────────
    recent_replies = (
        TicketReply.query
        .order_by(TicketReply.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = [
        {
            "text": f"{r.author.username} commented on #{r.ticket_id}",
            "time": r.created_at.strftime("%d %b %Y, %H:%M") if r.created_at else "",
        }
        for r in recent_replies
    ]

    # ── Ticket list ───────────────────────────────────────────────────────────
    ticket_list = base_q.order_by(Ticket.created_at.desc()).all()

    # ── Employees (manager / admin only) ──────────────────────────────────────
    if current_user.role in (Role.MANAGER, Role.ADMIN):
        employees = User.query.all()
    else:
        employees = []

    return render_template(
        "dashboard.html",
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        done_tickets=done_tickets,
        assigned_tickets=assigned_tickets,
        critical_tickets=critical_tickets,
        unassigned_tickets=unassigned_tickets,
        active_technicians=active_technicians,
        total_users=total_users,
        service_count=service_count,
        bug_count=bug_count,
        critical_count=critical_count,
        service_pct=service_pct,
        bug_pct=bug_pct,
        critical_pct=critical_pct,
        recent_activity=recent_activity,
        ticket_list=ticket_list,
        employees=employees,
    )