from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    place_id = fields.Many2one(
        'hr.attendance.place',
        'Attendance Place',
    )
    comments = fields.Char()
