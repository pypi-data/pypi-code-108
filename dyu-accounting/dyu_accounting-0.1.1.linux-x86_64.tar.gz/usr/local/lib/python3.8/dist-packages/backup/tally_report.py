import sys
import datetime
import re
from beancount import loader
from beancount.core import amount
from beancount.core.number import D
from beancount.core import data
from beancount.parser import printer
#__plugins__ = ['report_gst']
# Python Script for GST Reporting. Reports data for GSTR 1 and GSTR 3
# Input GST(GST Paid during a purchase.) is an Asset
# Output GST(GST Collected during a Sale) is an Liability.
# For GST1 Report all GST collected during Sales.
# For GSR3 Report all GST paid during Purchase.


def update_account(bean, category, field, posting, report):
    if re.search(bean, posting.account):
        print(f"amount={posting.units}")
        report[category][field] = amount.add(
            report[category][field], posting.units)


def report_gst(entries, options_map, report_fy):
    errors = []
    # print("entries=%s\n Options=%s\n \n" % (repr(entries), repr(options_map)))
    print("GST Plugin Invoked")
    # asset_re = re.compile(r'Assets.*GST')
    # liability_re = re.compile(r'Liability.*GST')
    report = {
        'directExpenses': {'customDuty': amount.Amount(D(0), 'INR')},
        'indirectIncome': {'exchangeGain': amount.Amount(D(0), 'INR')},
        'indirectExpenses': {
            'auditFee': amount.Amount(D(0), 'INR'),
            'deferredTax': amount.Amount(D(0), 'INR'),
            'depreciation': amount.Amount(D(0), 'INR'),
            'electricalItems': amount.Amount(D(0), 'INR'),
            'foodAllowances': amount.Amount(D(0), 'INR'),
            'fuelAllowances': amount.Amount(D(0), 'INR'),
            'generalExpenses': amount.Amount(D(0), 'INR'),
            'internetExpenses': amount.Amount(D(0), 'INR'),
            'officeMaintainance': amount.Amount(D(0), 'INR'),
            'professionalServices': amount.Amount(D(0), 'INR'),
            'registrationFees': amount.Amount(D(0), 'INR'),
            'repairAndMaintainance': amount.Amount(D(0), 'INR'),
            'salaryAndWages': amount.Amount(D(0), 'INR'),
            'telephoneExpenses': amount.Amount(D(0), 'INR'),
            'travelingExpenses': amount.Amount(D(0), 'INR'),
            'feesAndFine': amount.Amount(D(0), 'INR'),
        },
        'directIncome': {
            'consulting': amount.Amount(D(0), 'INR'),
            'otherIncome': amount.Amount(D(0), 'INR')
        }
    }
    today = datetime.date.today()
    cur_quarter = (today.month-1)//3
    print(cur_quarter)
    for entry in entries:
        if isinstance(entry, data.Transaction):
            entry_year = entry.date.year
            entry_quarter = (entry.date.month-1)//3
            # entry_quarter = 'q4' if entry_quarter == 0 else 'q' + str(entry_quarter)
            fy = str(entry_year-1) if entry_quarter == 4 else str(entry_year)
            print(f'date={entry.date} fy={int(fy)}: entry_year={entry_year}: entry_quarter={entry_quarter}')
            if (int(fy) == int(report_fy)) & (len(entry.postings) > 0):
                print("================================================")
                for posting in entry.postings:
                    update_account("Expenses:INR:Food", 'indirectExpenses',
                                   'foodAllowances', posting, report)
                    # update_account("Expenses:INR:Fuel", 'indirectExpenses',
                    #                'fuelAllowances', posting, report)
                    # update_account("Expenses:INR:Internet", 'indirectExpenses',
                    #                'internetExpenses', posting, report)
                    # update_account("Expenses:INR:Phone", 'indirectExpenses',
                    #                'telephoneExpenses', posting, report)

    print(f"report={repr(report)}")
    # print(" FY  Quarter Account                  GST1    GST3")
    # blank = ' '
    # for fy in gst:
    #     for q in gst[fy]:
    #         for account in gst[fy][q]['asset']:
    #             print(
    #                 f" {fy:5} {q:3} {account:10} {gst[fy][q]['asset'][account]} {blank:10}")
    #         for account in gst[fy][q]['liability']:
    #             print(
    #                 f" {fy:5} {q:3} {account:10} {blank:10} {gst[fy][q]['liability'][account]} ")
#    print(f'GSTR3: {repr(asset)}')

    return entries, errors


if __name__ == "__main__":

    entries, errors, options = loader.load_file(
        'ledger.beancounter', log_errors=sys.stderr)
    print(repr(errors))
    report_gst(entries, options, int(sys.argv[1]))
    # depreciation(entries, options)
