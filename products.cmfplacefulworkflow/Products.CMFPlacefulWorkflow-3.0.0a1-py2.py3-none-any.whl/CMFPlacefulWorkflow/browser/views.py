# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlacefulWorkflow import CMFPlacefulWorkflowMessageFactory as _
from Products.Five import BrowserView


class PlacefulWorkflowConfiguration(BrowserView):
    """Manage placeful wf for a item or container
    """

    def __call__(self):
        context = self.context
        request = self.request

        policy_in = request.form.get('policy_in', None)
        policy_below = request.form.get('policy_below', None)

        # Form submission will either have update_security as a key
        # meaning user wants to do it OR no key at all. If this script
        # is called directly, we use the parameter
        update_security = request.form.get('update_security', None)

        if 'add_wp_for_type' in request.form:
            context.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig(request)
            context.plone_utils.addPortalMessage(_(u'Workflow policy configuration added.'))
            return request.response.redirect('placeful_workflow_configuration')

        # This script is used for both the save and cancel button
        cancel = False
        submit = request.form.get('submit', None)
        if not submit:
            return self.index()

        if submit is not None and submit == 'Cancel':
            cancel = True
            message = _(u'Configuration changes cancelled.')


        if not cancel:
            tool = getToolByName(context, 'portal_placeful_workflow')
            config = tool.getWorkflowPolicyConfig(context)
            if not config:
                message = _(u'No config in this folder.')
            else:
                if not tool.isValidPolicyName(policy_in) and not policy_in == '':
                    raise AttributeError("%s is not a valid policy id" % policy_in)

                if not tool.isValidPolicyName(policy_below) and not policy_below == '':
                    raise AttributeError("%s is not a valid policy id" % policy_below)

                config.setPolicyIn(policy_in, update_security)
                config.setPolicyBelow(policy_below, update_security)

                message = _('Changed policies.')

        context.plone_utils.addPortalMessage(message)
        return request.response.redirect('placeful_workflow_configuration')


class WorkflowPoliciesForm(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request

        policy_ids = request.get('policy_ids', [])
        policy_id = request.get('policy_id', None)
        delete = request.get('delete', None)
        add = request.get('add', None)
        policy_duplicate_id = request.get('policy_duplicate_id', 'empty')

        pwtool = getToolByName(context, 'portal_placeful_workflow')
        plone_utils = getToolByName(context, 'plone_utils')

        if delete and policy_ids:
            for policy_id in policy_ids:
                if policy_id in pwtool.objectIds():
                    pwtool.manage_delObjects([policy_id, ])
            plone_utils.addPortalMessage(_(u'Deleted Local Workflow Policy.'), 'info')
            return request.response.redirect('@@prefs_workflow_localpolicies_form')

        elif add:
            if policy_id:
                pwtool.manage_addWorkflowPolicy(id=policy_id, duplicate_id=policy_duplicate_id)
                plone_utils.addPortalMessage(_(u'Local Workflow Policy added.'), 'info')
                return request.response.redirect('@@prefs_workflow_policy_mapping?wfpid=' + policy_id)

            else:
                plone_utils.addPortalMessage(_(u'The policy Id is required.'), 'error')
                return request.response.redirect('@@prefs_workflow_localpolicies_form')

        return self.index()

class WorkflowPolicyMapping(BrowserView):
    """
    """

    def __call__(self):
        # First check that we have a policy id and that it exists.
        # If we don't, return to the overview form.
        request = self.request
        context = self.context
        plone_utils = getToolByName(context, 'plone_utils')
        wfpid = request.get('wfpid', None)
        policy = None
        if wfpid:
            tool = getToolByName(context, 'portal_placeful_workflow')
            policy = tool.getWorkflowPolicyById(wfpid)
        if policy is None:
            portal_url = getToolByName(context, 'portal_url')()
            plone_utils.addPortalMessage(_(u'No Policy selected.'), 'error')
            return request.response.redirect(portal_url + '/@@prefs_workflow_localpolicies_form')

        if not request.get('submit', None):
            return self.index()

        title = request.get('title', None)
        description = request.get('description', None)
        default_workflow_id = request.get('default_workflow_id', None)
        wf = request.get('wf', None)

        if title:
            plone_utils.addPortalMessage(title)
            policy.setTitle(title)
        else:
            plone_utils.addPortalMessage(_(u'Title is required.'), 'error')
            return request.response.redirect('@@prefs_workflow_policy_mapping?wfpid=%s' % wfpid)

        policy.setDescription(description)
        policy.setDefaultChain(
            default_chain=(default_workflow_id, ),
            REQUEST=request)

        # for filtering special option values
        CHAIN_MAP = {'acquisition': None, '': ()}

        for pt, wflow in list(wf.items()):
            if wflow in CHAIN_MAP:
                chain = CHAIN_MAP[wflow]
            else:
                chain = (wflow, )
            policy.setChain(portal_type=pt, chain=chain, REQUEST=request)

        wf_tool = getToolByName(context, 'portal_workflow')
        wf_tool.updateRoleMappings()

        plone_utils.addPortalMessage(_(u'Changes to criteria saved.'))
        return request.response.redirect('@@prefs_workflow_policy_mapping?wfpid=%s' % wfpid)
