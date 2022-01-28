#
# jomiel
#
# Copyright
#  2019-2021 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from jomiel.cache import opts
from jomiel.log import lg
from jomiel_kore.app import exit_error
from jomiel_kore.sig import GracefulExit
from zmq import Context
from zmq import DEALER
from zmq import proxy
from zmq import ROUTER
from zmq import ZMQError


def init():
    """Initiates the broker."""

    def say(text, msgtype):
        """Write a event to the logger."""
        logger = getattr(lg(), msgtype)
        logger("subsystem/broker: %s", text)

    def log(text):
        """Write a "debug" event to the logger."""
        say(text, "debug")

    def log_error(text):
        """Write an "error" event to the logger."""
        say(text, "error")

    def bind_endpoint(device, endpoint, setup_curve=False):
        """Bind the device to the endpoint."""
        sck = ctx.socket(device)
        auth = None
        if opts.curve_enable and setup_curve:
            log("setup curve support")
            from jomiel.curve import setup

            auth = setup(sck)  # Must come before bind.
        try:
            sck.bind(endpoint)
        except ZMQError as error:
            log_error(f"{error}: {endpoint}")
            exit_error()
        return (sck, auth)

    def bind_router():
        """Bind the router device for talking to the clients."""
        router_endpoint = opts.broker_router_endpoint
        (router, auth) = bind_endpoint(
            ROUTER,
            router_endpoint,
            setup_curve=True,
        )
        log("bind router at <%s>" % router_endpoint)
        return (router, auth)

    def bind_dealer():
        """Bind the dealer device for talking to the workers."""
        dealer_endpoint = opts.broker_dealer_endpoint
        (dealer, _) = bind_endpoint(DEALER, dealer_endpoint)
        log("bind dealer at <%s>" % dealer_endpoint)
        return dealer

    def main_loop():
        """The main loop; sits and awaits for new connections."""

        def start_workers():
            """Creates the worker threads and initiates them."""

            from jomiel.subsys.broker.worker import worker_new
            from threading import Thread

            for worker_id in range(opts.broker_worker_threads):
                worker_thread = Thread(
                    target=worker_new,
                    args=(worker_id + 1,),
                )
                worker_thread.start()

            log("%d thread(s) active" % opts.broker_worker_threads)

        start_workers()

        try:
            proxy(router, dealer)
        except KeyboardInterrupt:
            log("<sigint> signal interrupt")
        except ZMQError as error:
            log_error(error)
        finally:
            dealer.close()
            router.close()
            if auth:
                auth.stop()
            ctx.term()

        log("shutdown")

    ctx = Context.instance()

    (router, auth) = bind_router()
    dealer = bind_dealer()

    with GracefulExit(log):
        main_loop()


# vim: set ts=4 sw=4 tw=72 expandtab:
