from flask import render_template, flash, redirect, url_for, request
from utils.decorators import admin_required
from utils.users import get_users_overview, get_all_users, get_user_count, deactivate_user, activate_user, get_users_paginated

def init_user_routes(app):
    @app.route("/users-management")
    @admin_required
    def users_management():
        page = request.args.get("page", default=1, type=int)
        per_page = 10

        users, total_pages = get_users_paginated(page=page, per_page=per_page)
        total_users = get_user_count()
        users_overview = get_users_overview()
        
        return render_template('pages/users_management.html', 
                            user_count=total_users, 
                            users=users, 
                            users_overview=users_overview,
                            page=page,
                            total_pages=total_pages,
                            per_page=per_page)


    @app.route("/deactivate-user/<int:user_id>", methods=['POST'])
    @admin_required
    def deactivate_user_route(user_id):
        if deactivate_user(user_id):
            flash("User deactivated successfully.", "success")
        else:
            flash("Cannot deactivate super admin!", "error")
        return redirect(url_for('users_management'))
    
    @app.route("/activate-user/<int:user_id>", methods=['POST'])
    @admin_required
    def activate_user_route(user_id):
        if activate_user(user_id):
            flash("User activated successfully.", "success")
        else:
            flash("Cannot activate super admin!", "error")
        return redirect(url_for('users_management'))