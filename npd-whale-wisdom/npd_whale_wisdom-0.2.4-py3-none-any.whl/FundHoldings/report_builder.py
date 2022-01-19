import pandas as pd
from WhaleWisdom.Common.npd_data import get_ww_tickers
import matplotlib.pyplot as plt
import math
import matplotlib.backends.backend_pdf
import logging

def get_ticker_count(data):

    ticker_data = data.sort_values(["filer_name","stock_ticker","current_mv"], ascending=False).drop_duplicates(subset=["filer_name","stock_ticker"])
    total_tickers = ticker_data["filer_name"].value_counts()
    target_tickers = ticker_data[ticker_data["current_percent_of_portfolio"] > 0.01]["filer_name"].value_counts()
    ticker_counts = {x : {} for x in data["filer_name"].unique()}
    for x in ticker_counts.keys():
        try:
            ticker_counts[x]["total"] = total_tickers[x]
        except:
            ticker_counts[x]["total"] = 0
        try:
            ticker_counts[x]["target"] = target_tickers[x]
        except:
            ticker_counts[x]["target"] = 0
    return ticker_counts



def get_aum(data):

    aum = {x : [] for x in data["filer_name"].unique()}
    for ind, row in data.iterrows():
        aum[row["filer_name"]].append(row["current_mv"] / (row["current_percent_of_portfolio"]))
    return {x : sum(aum[x]) / len(aum[x]) for x in aum.keys()}

def autosize_columns(df, worksheet):

    for idx, col in enumerate(df):
        col_data = df[col]
        max_len = max((col_data.astype(str).map(len).max(), len(str(col_data.name)))) + 1
        max_len = min(max_len, 60)
        worksheet.set_column(idx, idx, max_len)

def create_prospect_report_v1(data, quarter_name, output_path):

    data["current_percent_of_portfolio"] = data["current_percent_of_portfolio"] / 100
    ticker_count = get_ticker_count(data)
    aum = get_aum(data)
    target_list_df = pd.DataFrame(columns=["filer_name","AUM","Ticker_Count"])
    target_list_df["filer_name"] = list(data["filer_name"].unique())
    target_list_df["AUM"] = target_list_df["filer_name"].apply(lambda x: aum[x])
    target_list_df["Ticker_Count"] = target_list_df["filer_name"].apply(lambda x: ticker_count[x]["target"])
    target_list_df = target_list_df[(target_list_df["AUM"] >= 500000000) & (target_list_df["AUM"] < 10000000000) & (target_list_df["Ticker_Count"] >= 2)]
    target_list_df = target_list_df.sort_values("AUM", ascending=False)

    full_details_df = data
    full_details_df["AUM"] = full_details_df["filer_name"].apply(lambda x: aum[x])
    full_details_df["NPD_Ticker"] = "NPD_Ticker"
    full_details_df["stock_holding_morethan1pct"] = full_details_df["current_percent_of_portfolio"].apply(lambda x: "More than 1% of Portfolio" if x > 0.01 else "Other")
    full_details_df["Ticker_Count"] = full_details_df["filer_name"].apply(lambda x: ticker_count[x]["total"])
    full_details_df = full_details_df[["filer_name","stock_name","stock_ticker","security_type","current_mv","current_percent_of_portfolio","source_date","sector","industry","AUM","NPD_Ticker","stock_holding_morethan1pct","Ticker_Count"]]
    
    writer = pd.ExcelWriter("{output_path}ProspectV1_Report_{quarter}.xlsx".format(output_path=output_path, quarter=quarter_name.replace("/","-")), engine="xlsxwriter")
    target_list_df.to_excel(writer, index=False, sheet_name="1_target_list")
    full_details_df.to_excel(writer, index=False, sheet_name="2_full_details")
    workbook = writer.book
    target_list_sheet = writer.sheets["1_target_list"]
    full_details_sheet = writer.sheets["2_full_details"]

    
    dollars_format = workbook.add_format({'num_format': '[$$-409]#,##0'})
    percent_format = workbook.add_format({'num_format': '0.0%'})

    target_list_sheet.set_column("B:B", None, dollars_format)
    full_details_sheet.set_column("E:E", None, dollars_format)
    full_details_sheet.set_column("J:J", None, dollars_format)
    full_details_sheet.set_column("F:F", None, percent_format)
    
    autosize_columns(target_list_df, target_list_sheet)
    autosize_columns(full_details_df, full_details_sheet)
    target_list_sheet.autofilter("A1:C{end}".format(end=target_list_df.shape[0]))
    full_details_sheet.autofilter("A1:M{end}".format(end=full_details_df.shape[0]))
    
    writer.save()
    writer.close()

def create_prospect_report_v2(data, quarter_name, output_path):

    data["current_percent_of_portfolio"] = data["current_percent_of_portfolio"] / 100
    aum = get_aum(data)
    target_list_df = pd.DataFrame(columns=["filer_name","AUM","Filtered Ticker Count", "Filtered Ticker List"])
    target_list_df["filer_name"] = list(data["filer_name"].unique())
    target_list_df["AUM"] = target_list_df["filer_name"].apply(lambda x: aum[x])
    target_list_df = target_list_df[(target_list_df["AUM"] >= 500000000) & (target_list_df["AUM"] < 10000000000)]
    target_list_df = target_list_df.sort_values("AUM", ascending=False)

    full_details_df = data
    full_details_df["AUM"] = full_details_df["filer_name"].apply(lambda x: aum[x])
    full_details_df["NPD_Ticker"] = "NPD_Ticker"
    full_details_df["stock_holding_morethan1pct"] = full_details_df["current_percent_of_portfolio"].apply(lambda x: "More than 1% of Portfolio" if x > 0.01 else "Other")
    full_details_df = full_details_df[["filer_name","stock_name","stock_ticker","security_type","current_mv","current_percent_of_portfolio","source_date","sector","industry","AUM","NPD_Ticker","stock_holding_morethan1pct"]]
    
    writer = pd.ExcelWriter("{output_path}ProspectV2_Report_{quarter}.xlsx".format(output_path=output_path, quarter=quarter_name.replace("/","-")), engine="xlsxwriter")
    target_list_df.to_excel(writer, index=False, sheet_name="1_target_list")
    full_details_df.to_excel(writer, index=False, sheet_name="2_full_details")
    workbook = writer.book
    target_list_sheet = writer.sheets["1_target_list"]
    full_details_sheet = writer.sheets["2_full_details"]

    #add hidden rows
    #full_details_sheet.write("O1", "=SUBTOTAL(109, N1)")
    for i in range(len(full_details_df)):
        m_cell = "M" + str(i+2)
        n_cell = "N" + str(i+2)
        full_details_sheet.write(m_cell, 1)
        full_details_sheet.write_formula(n_cell, "=SUBTOTAL(109, {m_cell})".format(m_cell=m_cell))

    #add dynamic ticker count
    target_list_sheet.write("C1", "Filtered Ticker Count")
    target_list_sheet.write("D1", "Filtered Tickers")
    for i in range(len(target_list_df)):
        a_cell = "A" + str(i+2)
        c_cell = "C" + str(i+2)
        d_cell = "D" + str(i+2)
        target_list_sheet.write_formula(c_cell, '''=IF(LEN(TRIM({d_cell}))=0,0,(LEN(TRIM({d_cell}))-LEN(SUBSTITUTE({d_cell},", ","")))/2+1)'''.format(d_cell=d_cell))
        target_list_sheet.write_formula(d_cell, '''=TEXTJOIN(", ", TRUE, UNIQUE(FILTER('2_full_details'!C:C, ('2_full_details'!A:A={a_cell})*('2_full_details'!N:N=1)*('2_full_details'!L:L="More than 1% of Portfolio"),"")))'''.format(a_cell=a_cell))
    
    dollars_format = workbook.add_format({'num_format': '[$$-409]#,##0'})
    percent_format = workbook.add_format({'num_format': '0.0%'})

    target_list_sheet.set_column("B:B", None, dollars_format)
    full_details_sheet.set_column("E:E", None, dollars_format)
    full_details_sheet.set_column("J:J", None, dollars_format)
    full_details_sheet.set_column("F:F", None, percent_format)
    full_details_sheet.set_column("M:M", None, None, {'hidden': True})
    full_details_sheet.set_column("N:N", None, None, {'hidden': True})
    
    autosize_columns(target_list_df, target_list_sheet)
    autosize_columns(full_details_df, full_details_sheet)

    target_list_sheet.autofilter("B1:C{end}".format(end=target_list_df.shape[0]))
    full_details_sheet.autofilter("A1:L{end}".format(end=full_details_df.shape[0]))
    
    writer.save()
    writer.close()

def create_client_report(data, npd_tickers, npd_clients, quarter_name, output_path, create_charts):

    #create summary holdings tab
    data["NPD_Ticker"] = data["stock_ticker"].apply(lambda x: "NPD_ticker" if x in list(npd_tickers["stock_ticker"].unique()) else "Other_Ticker")
    data["current_percent_of_portfolio"] = data["current_percent_of_portfolio"] / 100
    ticker_type_df = data.groupby(["filer_name","NPD_Ticker"])["current_percent_of_portfolio"].sum().reset_index().rename(columns={"current_percent_of_portfolio":"Ticker_type_total"})
    npd_df = ticker_type_df[ticker_type_df["NPD_Ticker"] == "NPD_ticker"].sort_values("Ticker_type_total", ascending=False)
    ticker_type_df_sorted = []
    for ind, row in npd_df.iterrows():
        filer_rows = ticker_type_df[ticker_type_df["filer_name"] == row["filer_name"]].sort_values("NPD_Ticker")
        ticker_type_df_sorted.append(filer_rows)
    ticker_type_df_sorted = pd.concat(ticker_type_df_sorted)
    ticker_type_df_sorted = ticker_type_df_sorted.reset_index(drop=True)
    ticker_type_df_sorted = ticker_type_df_sorted[["filer_name","NPD_Ticker","Ticker_type_total"]]
    
    #create client account tab
    #clients input is already the necessary data

    #create data tab
    
    data["avg_price"] = data["avg_price"].apply(lambda x: "NA" if pd.isnull(x) else x)
    data["position_change_type"] = data["position_change_type"].apply(lambda x: "NA" if pd.isnull(x) else x)
    aum = get_aum(data)
    data["AUM"] = data["filer_name"].apply(lambda x: aum[x])
    data = data.reset_index(drop=True)
    ww_tickers = get_ww_tickers()
    data = data.merge(ww_tickers[["stock_ticker","stock_name","sector","industry"]], on=["stock_ticker"])
    #data = data.merge(npd_tickers[["stock_ticker","stock_name","sector","industry"]], on=["stock_ticker"])
    data = data[["filer_name","stock_name","stock_ticker","security_type","shares_change","position_change_type","avg_price","current_mv","current_percent_of_portfolio","source_date","sector","industry","AUM","NPD_Ticker"]]

    writer = pd.ExcelWriter("{output_path}Client_Report_{quarter}.xlsx".format(output_path=output_path, quarter=quarter_name.replace("/","-")), engine="xlsxwriter")
    ticker_type_df_sorted.to_excel(writer, index=False, sheet_name="summary_ticker_type")
    pd.DataFrame().to_excel(writer, index=False, sheet_name="Holdings_Chart_Current_Qtr")
    npd_clients.to_excel(writer, index=False, sheet_name="Clients_by_AccountManager")
    data.to_excel(writer, index=False, sheet_name="Data")

    workbook = writer.book
    ticker_type_sheet = writer.sheets["summary_ticker_type"]
    clients_sheet = writer.sheets["Clients_by_AccountManager"]
    data_sheet = writer.sheets["Data"]
    dollars_format = workbook.add_format({'num_format': '[$$-409]#,##0'})
    percent_format = workbook.add_format({'num_format': '0.0%'})

    ticker_type_sheet.set_column("C:C", None, percent_format)
    data_sheet.set_column("H:H", None, dollars_format)
    data_sheet.set_column("I:I", None, percent_format)
    data_sheet.set_column("M:M", None, dollars_format)
    autosize_columns(ticker_type_df_sorted, ticker_type_sheet)
    autosize_columns(npd_clients, clients_sheet)
    autosize_columns(data, data_sheet)
    
    ticker_type_sheet.autofilter("A1:C{end}".format(end=ticker_type_df_sorted.shape[0]))
    ticker_type_sheet.filter_column("B", "NPD_Ticker == NPD_ticker")
    for ind, row in ticker_type_df_sorted.iterrows():
        if row["NPD_Ticker"] != "NPD_ticker":
            ticker_type_sheet.set_row(ind+1, options={"hidden":True})
        
    clients_sheet.autofilter("A1:G{end}".format(end=npd_clients.shape[0]))

    data_sheet.autofilter("A1:N{end}".format(end=data.shape[0]))
    data_sheet.filter_column("N", "NPD_Ticker == NPD_ticker")
    for ind, row in data.iterrows():
        if row["NPD_Ticker"] != "NPD_ticker":
            data_sheet.set_row(ind+1, options={"hidden":True})

    writer.save()

    if create_charts:
        chart_data = data[(data["NPD_Ticker"] == "NPD_ticker") & (data["current_percent_of_portfolio"] > 0.001) & (data["security_type"] == "SH")].copy()
        chart_data["current_percent_of_portfolio"] = chart_data["current_percent_of_portfolio"] * 100
        chart_data = chart_data.merge(npd_clients[["filer_name","Account_Manager"]], on=["filer_name"])
        for group in chart_data["Account_Manager"].unique():
            pdf = matplotlib.backends.backend_pdf.PdfPages("{output_path}{group}_client_group_{quarter}.pdf".format(output_path=output_path, group=group, quarter=quarter_name.replace("/","-")))
            group_data = chart_data[chart_data["Account_Manager"] == group]
            filers = list(group_data["filer_name"].unique())
            filer_quads = [filers[x:x+4] for x in range(0, len(filers), 4)]
            for quad in filer_quads:
                figure, axis = plt.subplots(2, 2)
                figure.suptitle("{group} Client Group 13F holdings for quarter ending {quarter}\n(% of portfolio)".format(group=group, quarter=quarter_name))
                for ind, fund in enumerate(quad):
                    fund_data = group_data[group_data["filer_name"] == fund]
                    fund_data = fund_data.sort_values("current_percent_of_portfolio")
                    this_row = {0:0,1:0,2:1,3:1}[ind]
                    this_col = {0:0,1:1,2:0,3:1}[ind]
                    axis[this_row, this_col].barh(fund_data["stock_ticker"], fund_data["current_percent_of_portfolio"])
                    fund_name = "Enterprise" if fund == "NA" else fund
                    axis[this_row, this_col].set_title(fund_name, fontsize=9)
                plt.figtext(0.5, 0.01, "Source: WhaleWisdom.com", ha="center", fontsize=8)
                if len(quad) < 4:
                    axis.flat[-1].set_visible(False)
                if len(quad) < 3:
                    axis.flat[-2].set_visible(False)
                if len(quad) < 2:
                    axis.flat[-3].set_visible(False)
                plt.tight_layout()
                pdf.savefig(figure)
            pdf.close()
            