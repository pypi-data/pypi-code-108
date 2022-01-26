# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo.addons.vh.models.vh_utils import VhUtils


class VhInvoicingOrder(models.Model):
  _name = 'vh.invoicing.order'
  _inherit = ['vh.model.sequence.mixin']
  _prefix = "ORDER"

  name= fields.Char(_("Name"))

  account_journal_mids = fields.Many2many('account.journal', 
    'vh_invoicing_order_account_journal', 'invoicing_order_id',
    'account_journal_id', string=_("Account journals"))
  contact_group_id = fields.Many2one('vh.invoicing.contact.group')
  order_item_ids = fields.One2many('vh.invoicing.order.item','order_id',string="Order Items")
  payment_order_id = fields.Many2one('account.payment.order',string=_("Payment order"))
  status = fields.Selection(selection=[
    ('new',_("New")),
    ('invoices_collected',_("Invoices collected")),
    # ('consumptions_applied',_("Consumptions applied")),
    ('invoices_validated',_("Invoices validated")),
    ('invoices_sent',_("Invoices sent")),
    ('completed',_("Completed"))
  ], default='new', string=_("Status"))
  total_invoiced = fields.Float(string=_("Total invoiced"),compute="_get_total_invoiced",store=False)
  invoice_ids = fields.One2many('account.invoice',string=_("Invoices"),compute="_get_invoice_ids",store=False)

  @api.depends('invoice_ids')
  def _get_total_invoiced(self):
    for record in self:
      total = 0
      for invoice in record.invoice_ids:
        total += invoice.amount_total
      record.total_invoiced = total

  @api.depends('order_item_ids')
  def _get_invoice_ids(self):
    for record in self:
      total = 0
      for order_item in record.order_item_ids:
        for invoice in order_item.invoice_ids:
          record.invoice_ids = [(4,invoice.id)]

  # name defined after starting workflow
  @api.constrains('status')
  def _set_name(self):
    for record in self:
      if not record.external_id_sequence_id and record.status != 'new':
        record._set_external_sequence()
        record.name = record.external_id_sequence_id._next()
      elif record.status == 'new':
        record.name = record.id

  def _change_status(self,new_status):
    self.write({'status' : new_status})

  # WORKFLOW ACTIONS
  def collect_invoices_workflow_action(self):
    for record in self:
      record._validate_collect_invoices_pre()
      # iterate trough journals
      for journal in record.account_journal_mids:
        journal_draft_invoices = self.env['account.invoice'].search([('journal_id','=',journal.id),('state','=','draft')])
        if journal_draft_invoices.exists():
          # iterate trogh draft invoices in journal
          for invoice in journal_draft_invoices:
            # check invoice on the contact list
            if invoice.partner_id.id in record.contact_group_id.partner_mids.mapped('id'):
              query_data = [
                ('partner_id','=',invoice.partner_id.id),
                ('order_id','=',record.id)
              ]
              creation_data = {
                'name': '',
                'partner_id' : invoice.partner_id.id,
                'order_id': record.id
              }
              # get/create order item for the invoice
              order_item = VhUtils.get_create_existing_model(
                record.env['vh.invoicing.order.item'],
                query_data,
                creation_data
              )
              # relate invoice to order_item
              invoice.write({
                'order_item_id': order_item.id
              })
      record._validate_collect_invoices_post()
      record._change_status('invoices_collected')

  def validate_invoices_workflow_action(self):
    for record in self:
      record._validate_validate_invoices_pre()
      for invoice in record.invoice_ids:
      # iterate trough invoices and validate them
        invoice.action_invoice_open()
      record._change_status('invoices_validated')

  def send_invoices_workflow_action(self):
    for record in self:
      company = record.env.user.company_id
      mail_template = company.order_item_mail_template_id
      email_context = {'send_from_code': True}
      if mail_template:
        # iterate trough order items
        for order_item in record.order_item_ids:
          # iterate trough invoices in order_items
          for invoice in order_item.invoice_ids:
            # render invoice pdf
            pdf = self.env.ref('account.account_invoices').sudo().render_qweb_pdf([invoice.id])[0]
            # create invoice attachemnt
            invoice_attachment = self.env['ir.attachment'].create({
              'name': invoice.number + ".pdf",
              'type': 'binary',
              'res_id': invoice.id,
              'res_model': 'account.invoice',
              'datas': base64.b64encode(pdf),
              'mimetype': 'application/x-pdf',
              'datas_fname': invoice.number + ".pdf"
            })
            # add attachment to mail template
            mail_template.attachment_ids = [(4,invoice_attachment.id)]
          # send email
          mail_template.with_context(email_context).send_mail(order_item.id,force_send=True)
          # remove all attachments on template
          for attachment in mail_template.attachment_ids:
            mail_template.attachment_ids = [(3, attachment.id)]
      record._change_status('invoices_sent')

  def create_payment_order_workflow_action(self):
    for record in self:
      record._validate_create_payment_order_pre()
      # create payment order
      record.invoice_ids.create_account_payment_line()
      payment_order = record.env['account.payment.order'].search([('state','=','draft')],order='id desc')
      # attach it to invoicing_order
      if payment_order.exists():
        record.write({'payment_order_id': payment_order.id})
      record._validate_create_payment_order_post()
      record._change_status('completed')

  # WORKFLOW ACTIONS VALIDATION
  def _validate_collect_invoices_pre(self):
    if not self.account_journal_mids:
      raise exceptions.ValidationError(_("Error. At least one journal must be defined"))
  def _validate_collect_invoices_post(self):
    if not self.order_item_ids:
      raise exceptions.ValidationError(_("Error. No invoices found"))

  def _validate_validate_invoices_pre(self):
    for invoice in self.invoice_ids:
      if invoice.state != 'draft':
        raise exceptions.ValidationError(_("Error. Exists an invoice not in draft: ")+invoice.number)
    for order_item in self.order_item_ids:
      if not order_item.invoice_ids:
        raise exceptions.ValidationError(_("Error. Exists an item without invoices: ")+order_item.name)

  def _validate_create_payment_order_pre(self):
    payment_order = self.env['account.payment.order'].search([('state','=','draft')],order='id desc')
    if payment_order.exists():
      raise exceptions.ValidationError(_("Error. Exists already a payment order in draft: ")+payment_order.name)
  def _validate_create_payment_order_post(self):
    if not self.payment_order_id:
      raise exceptions.ValidationError(_("Error. There was a problem creating the payment order."))
