from .common import BaseClient, traderrpc, auctioneerrpc
from .errors import handle_rpc_errors


class PoolClient(BaseClient):
    @handle_rpc_errors
    def auction_fee(self):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.AuctionFeeRequest()
        response = self._trader_stub.AuctionFee(request)
        return response

    @handle_rpc_errors
    def batch_snapshots(self, start_batch_id, num_batches_back):
        """Get list of previously filled batches"""
        request = auctioneerrpc.BatchSnapshotsRequest(
            start_batch_id=start_batch_id,
            num_batches_back=num_batches_back
        )
        response = self._trader_stub.BatchSnapshots(request)
        return response

    @handle_rpc_errors
    def bump_account_fee(self, trader_key, fee_rate_sat_per_kw):
        """Bump onchain fee for opening an account"""
        request = traderrpc.BumpAccountFeeRequest(
            trader_key=trader_key,
            fee_rate_sat_per_kw=fee_rate_sat_per_kw
        )
        response = self._trader_stub.BumpAccountFee(request)
        return response

    @handle_rpc_errors
    def cancel_order(self, order_nonce):
        """Cancel an order"""
        request = traderrpc.CancelOrderRequest(
            order_nonce=order_nonce
        )
        response = self._trader_stub.CancelOrder(request)
        return response

    @handle_rpc_errors
    def cancel_sidecar(self, sidecar_id):
        """Cancel a sidecar ticket currently in-flight"""
        request = traderrpc.CancelSidecarRequest(sidecar_id=sidecar_id)
        response = self._trader_stub.CancelSidecar(request)
        return response

    @handle_rpc_errors
    def close_account(self, trader_key, **kwargs):
        """Close the given account and withdraw funds onchain"""
        request = traderrpc.CloseAccountRequest(
            trader_key=trader_key,
            **kwargs
        )
        response = self._trader_stub.CloseAccount(request)
        return response

    @handle_rpc_errors
    def decode_sidecar_ticket(self, ticket):
        """Decode a sidecar ticket into a useable form"""
        request = traderrpc.SidecarTicket(ticket=ticket)
        response = self._trader_stub.DecodeSidecarTicket(request)
        return response

    @handle_rpc_errors
    def deposit_account(self, trader_key, amount_sat, fee_rate_sat_per_kw):
        """Deposit coins into collaborative pool multisig"""
        request = traderrpc.DepositAccountRequest(
            trader_key=trader_key,
            amount_sat=amount_sat,
            fee_rate_sat_per_kw=fee_rate_sat_per_kw
        )
        response = self._trader_stub.DepositAccount(request)
        return response

    # step 4/4
    @handle_rpc_errors
    def expect_sidecar_channel(self, ticket):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.ExpectSidecarChannelRequest(
            ticket=ticket
        )
        response = self._trader_stub.ExpectSidecarChannel(request)
        return response

    @handle_rpc_errors
    def get_info(self):
        """Get info about the pool daemon"""
        request = traderrpc.GetInfoRequest()
        response = self._trader_stub.GetInfo(request)
        return response

    @handle_rpc_errors
    def get_lsat_tokens(self):
        """List available LSAT tokens"""
        request = traderrpc.TokensRequest()
        response = self._trader_stub.GetLsatTokens(request)
        return response

    @handle_rpc_errors
    def init_account(self, **kwargs):
        """Create a new pool account"""
        request = traderrpc.InitAccountRequest(**kwargs)
        response = self._trader_stub.InitAccount(request)
        return response

    @handle_rpc_errors
    def lease_durations(self):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.LeaseDurationRequest()
        response = self._trader_stub.LeaseDurations(request)
        return response

    @handle_rpc_errors
    def leases(self, batch_ids, accounts):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.LeasesRequest(
            batch_ids=batch_ids,
            accounts=accounts
        )
        response = self._trader_stub.Leases(request)
        return response

    @handle_rpc_errors
    def list_accounts(self, active_only=False):
        """List trader accounts"""
        request = traderrpc.ListAccountsRequest(
            active_only=active_only
        )
        response = self._trader_stub.ListAccounts(request)
        return response

    @handle_rpc_errors
    def list_orders(self, verbose=False, active_only=True):
        """
        List info about orders
        cli: pool orders list
        """
        request = traderrpc.ListOrdersRequest(
            verbose=verbose,
            active_only=active_only
        )
        response = self._trader_stub.ListOrders(request)
        return response

    @handle_rpc_errors
    def list_sidecars(self, sidecar_id=None):
        """List the sidecar tickets currently in-flight"""
        request = traderrpc.ListSidecarsRequest(sidecar_id=sidecar_id)
        response = self._trader_stub.ListSidecars(request)
        return response

    @handle_rpc_errors
    def next_batch_info(self):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.NextBatchInfoRequest()
        response = self._trader_stub.NextBatchInfo(request)
        return response

    @handle_rpc_errors
    def node_ratings(self, node_pubkeys=[]):
        """Get node ratings given a list of pubkeys"""
        node_pubkeys = [bytes.fromhex(x) for x in node_pubkeys]
        request = traderrpc.NodeRatingRequest(node_pubkeys=node_pubkeys)
        response = self._trader_stub.NodeRatings(request)
        return response

    # step 1/4
    @handle_rpc_errors
    def offer_sidecar(self, bid, auto_negotiate):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.OfferSidecarRequest(
            auto_negotiate=auto_negotiate,
            bid=bid,
        )
        response = self._trader_stub.OfferSidecar(request)
        return response

    @handle_rpc_errors
    def quote_account(self, account_value, conf_target):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.QuoteAccountRequest(
            account_value=account_value, conf_target=conf_target
        )
        response = self._trader_stub.QuoteAccount(request)
        return response

    @handle_rpc_errors
    def quote_order(
        self,
        amt,
        rate_fixed,
        lease_duration_blocks,
        max_batch_fee_rate_sat_per_kw,
        min_units_match,
    ):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.QuoteOrderRequest(
            amt=amt,
            rate_fixed=rate_fixed,
            lease_duration_blocks=lease_duration_blocks,
            max_batch_fee_rate_sat_per_kw=max_batch_fee_rate_sat_per_kw,
            min_units_match=min_units_match,
        )
        response = self._trader_stub.QuoteOrder(request)
        return response

    @handle_rpc_errors
    def recover_accounts(self):
        """Recover trader accounts that mightve been lost if there was DB corruption based on the backing node pubkey"""
        request = traderrpc.RecoverAccountsRequest()
        response = self._trader_stub.RecoverAccounts(request)
        return response

    # step 2/4
    @handle_rpc_errors
    def register_sidecar(self, ticket, auto_negotiate):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.RegisterSidecarRequest(
            ticket=ticket,
            auto_negotiate=auto_negotiate,
        )
        response = self._trader_stub.RegisterSidecar(request)
        return response

    @handle_rpc_errors
    def renew_account(self, account_key, absolute_expiry, relative_expiry, fee_rate_sat_per_kw):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.RenewAccountRequest(
            account_key=account_key,
            absolute_expiry=absolute_expiry,
            relative_expiry=relative_expiry,
            fee_rate_sat_per_kw=fee_rate_sat_per_kw
        )
        response = self._trader_stub.RenewAccount(request)
        txid = response.account.latest_txid
        txid = bytearray(txid)
        txid.reverse()
        print(f"Latest TXID: {txid.hex()}")
        return response

    @handle_rpc_errors
    def stop_daemon(self):
        """Gracefully stop the pool daemon"""
        request = traderrpc.StopDaemonRequest()
        response = self._trader_stub.StopDaemon(request)
        return response

    @handle_rpc_errors
    def submit_order(self, **kwargs):
        """Unlock encrypted wallet at lnd startup"""
        # TODO: either bid or ask must be filled but not both
        request = traderrpc.SubmitOrderRequest(**kwargs)
        response = self._trader_stub.SubmitOrder(request)
        return response

    @handle_rpc_errors
    def withdraw_account(self, trader_key, outputs, fee_rate_sat_per_kw):
        """Unlock encrypted wallet at lnd startup"""
        request = traderrpc.WithdrawAccountRequest(
            trader_key=trader_key,
            outputs=outputs,
            fee_rate_sat_per_kw=fee_rate_sat_per_kw
        )
        response = self._trader_stub.WithdrawAccount(request)
        return response