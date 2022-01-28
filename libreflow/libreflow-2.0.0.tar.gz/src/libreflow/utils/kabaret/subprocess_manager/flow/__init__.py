from kabaret.subprocess_manager.flow import RunAction as KabaretSMRunAction


class RunAction(KabaretSMRunAction):

    @classmethod
    def get_result(
            cls, close=None, refresh=None,
            goto=None, goto_target=None, goto_target_type=None, 
            next_action=None, runner_id=None
    ):
        ret = super(RunAction, cls).get_result(
            close=close, refresh=refresh,
            goto=goto, goto_target=goto_target, goto_target_type=goto_target_type,
            next_action=next_action
        )
        ret.update(dict(runner_id=runner_id))

        return ret

    def run(self, button):
        name, tags = self.runner_name_and_tags()
        rid = self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            tags=tags,
            version=self.get_version(button),
            label=self.get_run_label(),
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
        )
        return self.get_result(runner_id=rid)
