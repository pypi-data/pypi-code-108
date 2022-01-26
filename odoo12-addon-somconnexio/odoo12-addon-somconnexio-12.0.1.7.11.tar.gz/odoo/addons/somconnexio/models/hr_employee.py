from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    current_place = fields.Many2one(
        'hr.attendance.place',
        string='Current attendance place',
        compute='_compute_attendance_state',
    )

    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id.place_id', 'last_attendance_id')  # noqa
    def _compute_attendance_state(self):
        for employee in self:
            att = employee.last_attendance_id.sudo()
            employee.attendance_state = att and not att.check_out and 'checked_in' or 'checked_out' # noqa
            employee.current_place = att.place_id

    @api.multi
    def attendance_manual(self, next_action, place_code=False, comments_value=False, entered_pin=None): # noqa
        self.ensure_one()
        if not (entered_pin is None) or self.env['res.users'].browse(SUPERUSER_ID).has_group('hr_attendance.group_hr_attendance_use_pin') and (self.user_id and self.user_id.id != self._uid or not self.user_id): # noqa
            if entered_pin != self.pin:
                return {'warning': _('Wrong PIN')}
        return self.attendance_action(next_action, place_code, comments_value)

    @api.multi
    def attendance_action(self, next_action, place_code=False, comments_value=False):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to.
            ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0] # noqa
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False # noqa
        action_message['employee_name'] = self.name
        action_message['barcode'] = self.barcode
        action_message['next_action'] = next_action

        if self.user_id:
            modified_attendance = self.sudo(self.user_id.id).attendance_action_change(place_code, comments_value) # noqa
        else:
            modified_attendance = self.sudo().attendance_action_change(place_code, comments_value) # noqa
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message}

    @api.multi
    def attendance_action_change(self, place_code=False, comments_value=False):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.')) # noqa
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'place_id': self.env['hr.attendance.place'].search(
                    [('code', '=', place_code)]
                ).id,
                'comments': comments_value
            }
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1) # noqa
            if attendance:
                attendance.check_out = action_date
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. ' # noqa
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.name, }) # noqa
            return attendance
