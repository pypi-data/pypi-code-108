"""
Supervisor processes
====================

This module provides high-level tools for managing long-running
processes using `supervisord`_.

.. _supervisord: http://supervisord.org/

"""
import os

from burlap.constants import *
from burlap import ServiceSatchel
from burlap.decorators import task


class SupervisorSatchel(ServiceSatchel):

    name = 'supervisor'

    post_deploy_command = 'restart_all'

    @property
    def packager_system_packages(self):
        return {
            UBUNTU: ['supervisor'],
        }

    def set_defaults(self):

        self.env.manage_configs = True
        self.env.config_template = 'supervisor/supervisor_daemon.template2.config'
        self.env.config_path = '/etc/supervisor/supervisord.conf'
        self.env.conf_dir = '/etc/supervisor/conf.d'
        self.env.daemon_bin_path_template = '{pip_virtualenv_dir}/bin/supervisord'
        self.env.daemon_path = '/etc/init.d/supervisord'
        self.env.bin_path_template = '{pip_virtualenv_dir}/bin'
        self.env.daemon_pid = '/var/run/supervisord.pid'
        self.env.log_path = "/var/log/supervisord.log"
        self.env.supervisorctl_path_template = '{pip_virtualenv_dir}/bin/supervisorctl'
        self.env.kill_pattern = ''
        self.env.services_rendered = ''

        # If true, then all configuration files not explicitly managed by use will be deleted.
        self.env.purge_all_confs = True

        self.env.services = []

        # Functions that, when called, should return a supervisor service text ready to be appended to supervisord.conf.
        # It will be called once for each site.
        self.genv._supervisor_create_service_callbacks = []

        # Most of these service commands are overridden by satchel tasks.
        # http://supervisord.org/running.html
        # http://www.onurguzel.com/supervisord-restarting-and-reloading/
        # "unix:///var/run/supervisor.sock no such file" generally indicates that the Supervisor service is not running.
        self.env.service_commands = {
            START: { # Start Supervisor service. Processes should come up automatically.
                FEDORA: 'systemctl start supervisord.service',
                UBUNTU: 'service supervisor start',
            },
            STOP: { # Stop Supervisor service. Not guaranteed to stop all processes, as stop_all() does.
                FEDORA: 'systemctl stop supervisor.service',
                UBUNTU: 'service supervisor stop',
            },
            DISABLE: {
                FEDORA: 'systemctl disable httpd.service',
                UBUNTU: 'chkconfig supervisor off',
            },
            ENABLE: {
                FEDORA: 'systemctl enable httpd.service',
                UBUNTU: 'chkconfig supervisor on',
            },
            RESTART: { # Restart Supervisor service. Not guaranteed to restart all processes, as restart_all() does.
                FEDORA: 'systemctl restart supervisord.service',
                UBUNTU: 'service supervisor restart; sleep 5',
            },
            STATUS: { # Get status of Supervisor service. Use status_all() for a better view of process status.
                FEDORA: 'systemctl --no-pager status supervisord.service',
                (UBUNTU, '14.04'): 'service supervisor status',
                (UBUNTU, '16.04'): 'systemctl --no-pager status supervisor',
                UBUNTU: 'systemctl --no-pager status supervisor',
            },
        }

    def render_paths(self):
        r = self.local_renderer
        r.env.daemon_bin_path = r.format(r.env.daemon_bin_path_template)
        r.env.bin_path = r.format(r.env.bin_path_template)
        r.env.supervisorctl_path = r.format(r.env.supervisorctl_path_template)

    def register_callback(self, f):
        self.genv._supervisor_create_service_callbacks.append(f)

    @task
    def start_all(self):
        """
        Start service and all processes.
        """
        r = self.local_renderer
        self.start()
        r.sudo('supervisorctl start all')

    @task
    def stop_all(self):
        """
        Stop all processes, but don't stop service.
        """
        r = self.local_renderer
        r.sudo('supervisorctl stop all')

    @task
    def restart_all(self):
        """
        Restart all processes, but don't restart service.
        """
        r = self.local_renderer
        r.sudo('supervisorctl restart all')

    @task
    def status_all(self):
        """
        Get status of all processes.
        """
        r = self.local_renderer
        r.sudo('supervisorctl status')

    @task
    def restart(self):
        """
        Stop all processes, reread config, and reload supervisord.
        """
        self.stop_all()
        self.reload()

    @task
    def reload(self):
        """
        Reread config and reload supervisord, but don't restart service.

        May take several minutes if processes have not yet been stopped.
        restart() is usually faster, as it uses stop_all() to stop processes.
        """
        r = self.local_renderer
        r.sudo('supervisorctl reread')
        r.sudo('supervisorctl reload')

    @task
    def update(self):
        """
        Restart applications whose configurations have changed (does not restart service).
        """
        r = self.local_renderer
        r.sudo('supervisorctl update')

    def record_manifest(self):
        """
        Called after a deployment to record any data necessary to detect changes for a future deployment.
        """
        data = super().record_manifest()

        # Celery deploys itself through supervisor, so monitor its changes too in Apache site configs.
        for site_name, site_data in self.genv.sites.items():
            if self.verbose:
                print(site_name, site_data)
            data['celery_has_worker_%s' % site_name] = site_data.get('celery_has_worker', False)

        data['configured'] = True

        # Generate services list.
        self.write_configs(upload=0)

        return data

    @task
    def write_configs(self, site=None, upload=1):

        site = site or ALL
        verbose = self.verbose

        self.render_paths()

        supervisor_services = []

        # TODO: check available_sites_by_host and remove dead?
        for _site, site_data in self.iter_sites(site=site, renderer=self.render_paths):
            if verbose:
                print('write_configs.site:', _site)
            for cb in self.genv._supervisor_create_service_callbacks:
                ret = cb(site=_site)
                if isinstance(ret, str):
                    supervisor_services.append(ret)
                elif isinstance(ret, tuple):
                    assert len(ret) == 2
                    conf_name, conf_content = ret
                    if verbose:
                        print('conf_name:', conf_name)
                        print('conf_content:', conf_content)
                    remote_fn = os.path.join(self.env.conf_dir, conf_name)
                    if int(upload):
                        local_fn = self.write_to_file(conf_content)
                        self.put(local_path=local_fn, remote_path=remote_fn, use_sudo=True)

        self.env.services_rendered = '\n'.join(supervisor_services)

        if int(upload):
            fn = self.render_to_file(self.env.config_template)
            self.put(local_path=fn, remote_path=self.env.config_path, use_sudo=True)

    def deploy_services(self, site=None, restart=1):
        """
        Collect the configurations for all registered services and write the appropriate supervisord.conf file.
        """

        verbose = self.verbose

        r = self.local_renderer
        if not r.env.manage_configs:
            return

        self.render_paths()

        supervisor_services = []

        if r.env.purge_all_confs:
            r.sudo('rm -Rf /etc/supervisor/conf.d/*')

        # TODO: check available_sites_by_host and remove dead?
        self.write_configs(site=site)
        for _site, site_data in self.iter_sites(site=site, renderer=self.render_paths):
            if verbose:
                print('deploy_services.site:', _site)

            for cb in self.genv._supervisor_create_service_callbacks:
                if self.verbose:
                    print('cb:', cb)
                ret = cb(site=_site)
                if self.verbose:
                    print('ret:', ret)
                if isinstance(ret, str):
                    supervisor_services.append(ret)
                elif isinstance(ret, tuple):
                    assert len(ret) == 2
                    conf_name, conf_content = ret
                    if self.dryrun:
                        print('supervisor conf filename:', conf_name)
                        print(conf_content)
                    self.write_to_file(conf_content)

        self.env.services_rendered = '\n'.join(supervisor_services)

        fn = self.render_to_file(self.env.config_template)
        r.put(local_path=fn, remote_path=self.env.config_path, use_sudo=True)

        if int(restart):
            self.start()
            self.update()

    @task(precursors=['packager', 'user', 'rabbitmq'])
    def configure(self, **kwargs):
        kwargs.setdefault('site', ALL)

        self.deploy_services(**kwargs)

supervisor = SupervisorSatchel()
