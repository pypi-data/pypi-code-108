from zerohash import resources

OBJECT_CLASSES = {
    resources.Accounts.OBJECT_NAME: resources.Accounts,
    resources.DigitalAssetAddresses.OBJECT_NAME: resources.DigitalAssetAddresses,
    resources.Index.OBJECT_NAME: resources.Index,
    resources.LiquidityRfq.OBJECT_NAME: resources.LiquidityRfq,
    resources.ParticipantCustomerNew.OBJECT_NAME: resources.ParticipantCustomerNew,
    resources.LiquidityExecute.OBJECT_NAME: resources.LiquidityExecute,
    resources.Trades.OBJECT_NAME: resources.Trades,
    resources.TradesBatch.OBJECT_NAME: resources.TradesBatch,
    resources.Transfers.OBJECT_NAME: resources.Transfers,
    resources.Participants.OBJECT_NAME: resources.Participants,
    resources.Time.OBJECT_NAME: resources.Time,
    resources.WithdrawalDigitalAssetAddresses.OBJECT_NAME: resources.WithdrawalDigitalAssetAddresses,
    resources.Withdrawal.OBJECT_NAME: resources.Withdrawal,
    resources.Withdrawals.OBJECT_NAME: resources.Withdrawals,
}
