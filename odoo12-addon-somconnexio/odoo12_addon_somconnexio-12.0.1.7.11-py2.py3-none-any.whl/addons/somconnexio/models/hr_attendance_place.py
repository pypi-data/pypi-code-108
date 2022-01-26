from odoo import models, fields


class HrAttendancePlace(models.Model):
    _name = 'hr.attendance.place'
    name = fields.Char('Name', translate=True)
    code = fields.Char('Code', required=True)
