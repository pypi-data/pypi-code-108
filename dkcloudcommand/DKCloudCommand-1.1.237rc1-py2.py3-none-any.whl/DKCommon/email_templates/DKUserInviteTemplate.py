DK_USER_INVITE_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>DataKitchen - Invite</title>
        <style type="text/css">
            body {
                margin: 0;
                padding: 0;
                background: #e5e5e5 !important;
            }
            h1, p {
                margin: 0;
            }

            table.body {
                width: 100%;
                height: 100%;
                background: #E5E5E5 !important;
            }

            table.body > tbody > tr > td {
                padding: 32px;
            }

            table.content {
                margin-left: auto;
                margin-right: auto;
                border-radius: 4px;
                border-collapse: collapse;

                background-color: #ffffff;
                background-image: url('https://dk-support-external.s3.amazonaws.com/support/dk_logo_horizontal.png');
                background-repeat: no-repeat;
                background-size: 120px 24px;
                background-position: 24px 24px;
            }

            table.content .content-header {
                padding: 24px;
                padding-bottom: 0px;
            }

            table.content .content-body {
                padding: 24px;
                padding-top: 0px;
                padding-bottom: 75px;
            }

            table.content .content-header h1 {
                font-family: 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 20px;
                font-weight: 400;
                line-height: 24px;
                color: rgba(0, 0, 0, .87);
                margin-bottom: 53px;
            }

            .intro {
                font-family: 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 16px;
                font-weight: 400;
                line-height: 18px;
                color: rgba(0, 0, 0, .87);

                margin-left: 70px;
                margin-right: 70px;
                margin-bottom: 10px;
            }

            .purpose {
                font-family: 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 16px;
                font-weight: 400;
                line-height: 18px;
                color: rgba(0, 0, 0, .87);

                margin-left: 70px;
                margin-right: 70px;
                margin-bottom: 48px;
            }

            .message {
                font-family: 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                font-weight: 400;
                line-height: 16px;
                color: rgba(0, 0, 0, .38);

                margin-bottom: 40px;
            }

            td.button-wrapper {
                border-radius: 4px;
                background-color: #06A04A;
            }

            td.button-wrapper .button {
                padding: 10px 12px;

                background: #06A04A;
                border-radius: 4px;
                margin: 0px;
                text-decoration: none;

                display: table;
            }

            a.button span {
                font-family: 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                font-weight: 500;
                line-height: 16px;
                color: #ffffff;

                display: table-cell;
                vertical-align: middle;
                padding-right: 8px;
            }

            a.button img {
                width: 18px;
                display: table-cell;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" class="body">
            <tr>
                <td>
                    <table align="center" cellpadding="0" cellspacing="0" width="800" class="content">
                        <tr align="center">
                            <td class="content-header">
                                <h1>Join DataKitchen</h1>
                            </td>
                        </tr>

                        <tr>
                            <td class="content-body">
                                <table align="center" cellpadding="0" cellspacing="0" border="0" width="75%" class="card">
                                    <tr>
                                        <td>
                                            <p class="intro">Hello!<p>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <p class="purpose">You have been invited to access the {{ primary_company }} account in the DataKitchen DataOps Platform.</p>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="center">
                                            <table border="0" cellspacing="0" cellpadding="0" class="button-table">
                                                <tr>
                                                    <td align="center" class="button-wrapper">
                                                        <a href="{{ public_address }}/#/join?request_id={{ request_id }}" target="_blank" class="button">
                                                            <span>Join Now</span>
                                                            <img src="https://dk-support-external.s3.amazonaws.com/support/arrow-forward.png" alt="Arrow Forward">
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""
