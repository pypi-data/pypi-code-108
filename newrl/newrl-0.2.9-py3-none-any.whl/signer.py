import base64
import ecdsa
import json


def sign_transaction(wallet_data, transaction_data):
    pvtkeybytes = None
    pubkeybytes = None

    address = wallet_data['address']
    pvtkeybytes = base64.b64decode(wallet_data['private'])
    pubkeybytes = base64.b64decode(wallet_data['public'])
    if not pvtkeybytes:
        print("No private key found for the address")
        return False

    # if not addresschecker(transaction_data, address):
    #     return False

    msg = json.dumps(transaction_data['transaction']).encode()
    sk = ecdsa.SigningKey.from_string(pvtkeybytes, curve=ecdsa.SECP256k1)
    msgsignbytes = sk.sign(msg)
    msgsign = base64.b64encode(msgsignbytes).decode('utf-8')
    signatures = transaction_data['signatures'] if 'signatures' in transaction_data else [
    ]
    signatures.append({'wallet_address': address, 'msgsign': msgsign})
    # print("signed msg signature is:", signtransbytes,
    #       " and address is ", address)
    # signtrans = base64.b64encode(signtransbytes).decode('utf-8')

    # transaction_all = {'transaction': transaction_data,
    #                        'signatures': signatures}


#	print("storing this in encoded form is:",signtrans)
    # if signtrans:
    #     transaction_file = tm.dumptransaction()
    #     print("Successfully signed the transaction and updated its signatures data.")
    #     sign_status = tm.verifysign(signtrans, pubkeybytes, address)
    #     print("Status of signing: ", sign_status)
    #     with open(transaction_file) as f:
    #         return json.load(f)
    #     # return FileResponse(transfile, filename="signed_transferfile.json")
    #     # return sign_status
    # else:
    #     print("Signing failed. No change made to transaction's signature data")
    #     return None

    return transaction_data


def addresschecker(transaction, address):
    #	trans=trandata['transaction']
    #	signatures = trandata['signatures']
    validadds = getvalidadds(transaction)
    print(validadds)
    for add in validadds:
        if add == address:
            print("The address ", address,
                  " is authorised to sign this transaction.")
            return True
        # did not find the address in the validadds
    print("The address ", address, " is not authorised to sign this transaction.")
    return False

# use the below one to get all authorized addresses that can sign a transaction


def getvalidadds(transaction):
    trans = transaction
    ttype = trans['type']
    validadds = []
    if ttype == 1:  # wallet creation, custodian needs to sign
        validadds.append(trans['specific_data']['custodian_wallet'])
    if ttype == 2:  # token creation, custodian needs to sign
        validadds.append(trans['specific_data']['custodian'])
    if ttype == 4:  # two way transfer; both senders need to sign
        validadds.append(trans['specific_data']['wallet1'])
        validadds.append(trans['specific_data']['wallet2'])
    if ttype == 5:  # one way transfer; only sender1 is needed to sign
        validadds.append(trans['specific_data']['wallet1'])
    return validadds
