from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models.user import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():

    # ── Ticket stats ──────────────────────────────────────────────────────────
    # TODO: replace with real queries once Ticket model is implemented
    total_tickets      = 0
    open_tickets       = 0
    in_progress_tickets = 0
    done_tickets       = 0
    assigned_tickets   = 0   # technician only
    critical_tickets   = 0   # technician only
    unassigned_tickets = 0   # manager/admin only
    active_technicians = 0   # manager/admin only

    # ── Admin: total users ────────────────────────────────────────────────────
    total_users = User.query.count() if current_user.role == "admin" else 0

    # ── Category breakdown ────────────────────────────────────────────────────
    # TODO: replace with real queries once Ticket + Category models are implemented
    service_count = 0
    bug_count     = 0
    critical_count = 0
    service_pct   = 0
    bug_pct       = 0
    critical_pct  = 0

    # ── Recent activity ───────────────────────────────────────────────────────
    # TODO: replace with real activity feed once tickets/replies are implemented
    recent_activity = []

    # ── Ticket list ───────────────────────────────────────────────────────────
    # TODO: replace with real queries once Ticket model is implemented
    ticket_list = []

    # ── Employees (manager / admin only) ──────────────────────────────────────
    # TODO: extend once employee-specific fields are added to User model
    if current_user.role in ("manager", "admin"):
        employees = User.query.filter(User.role == "technician").all()
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