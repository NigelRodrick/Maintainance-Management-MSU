from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required
from ..services.report_service import report_service
import os

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route("/")
@login_required
def reports():
    try:
        report_list = report_service.get_report_list()
        return render_template("reports.html", reports=report_list)
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template("reports.html", reports=[])

@reports_bp.route("/generate", methods=["POST"])
@login_required
def generate_report():
    try:
        filename = report_service.generate_comprehensive_report()
        flash(f'Report generated successfully: {filename}', 'success')
        return redirect(url_for('reports.reports'))
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('reports.reports'))

@reports_bp.route("/download/<filename>")
@login_required
def download_report(filename):
    try:
        reports_dir = current_app.config['REPORTS_DIR']
        filepath = os.path.join(reports_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            flash('Report not found', 'error')
            return redirect(url_for('reports.reports'))
    except Exception as e:
        flash(f'Error downloading report: {str(e)}', 'error')
        return redirect(url_for('reports.reports'))

@reports_bp.route("/analytics")
@login_required
def report_analytics():
    try:
        # Generate job statistics report
        job_report = report_service.generate_job_report()
        
        return render_template("report_analytics.html", 
                             job_report=job_report)
    except Exception as e:
        flash(f'Error loading report analytics: {str(e)}', 'error')
        return render_template("report_analytics.html", job_report=None)
