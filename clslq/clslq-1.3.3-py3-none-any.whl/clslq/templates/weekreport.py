wr_template = """

<tbody>
  <tr>
    <td>
      <table align="center" border="0" cellpadding="0" cellspacing="0" 
        style="border-collapse: collapse; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
        <tbody>
          <tr height="34" style="height:34.0pt;vertical-align: middle; text-align: center;padding: 10px; background-color: #f3f9f1; border: none; font-size: 20px; font-weight: bold; border-bottom: 1px solid #e5e5e5;">
            <td style="color: #333; ">$title</td>
          </tr>
          <tr>
            <td style="padding: 10px; border: none;">
              <fieldset style="border: 1px solid #e5e5e5">
                <legend style="color: #114f8e">本周工作情况</legend>
                <div style="padding:5px;">
                  <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; color: #3d3b4f; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
                    <tbody>
                      <tr height="19" style="height:14.0pt;background-color:rgb(253, 233, 217)">
                        <td height="19" width="107"
                          style="border: 0.5pt solid #cfcfcf; width: 107pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          分类</td>
                        <td height="19" width="284"
                          style="border: 0.5pt solid #cfcfcf; width: 284pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          事项</td>
                        <td height="19" width="84"
                          style="border: 0.5pt solid #cfcfcf; width: 84pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          进度</td>
                        <td height="19" width="279"
                          style="border: 0.5pt solid #cfcfcf; width: 279pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          遇到问题</td>
                        <td height="19" width="381"
                          style="border: 0.5pt solid #cfcfcf; width: 381pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          解决办法</td>
                      </tr>

                      $table

                    </tbody>
                  </table>
                </div>
              </fieldset>
            </td>
          </tr>
          <tr>
            <td style="padding:0px 10px 10px 10px; border: none;">
              <fieldset style="border: 1px solid #e5e5e5">
                <legend style="color: #114f8e">下周工作计划</legend>
                <div style="padding:5px;">
                  <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse; color: #3d3b4f; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
                    <tbody>

                      <tr height="19" style="height:14.0pt;background-color:rgb(253, 233, 217)">
                        <td height="19" width="107"
                          style="border: 0.5pt solid #cfcfcf; width: 107pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          分类</td>
                        <td height="19" width="284"
                          style="border: 0.5pt solid #cfcfcf; width: 284pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          事项</td>
                        <td height="19" width="84"
                          style="border: 0.5pt solid #cfcfcf; width: 84pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          进度</td>
                        <td height="19" width="279"
                          style="border: 0.5pt solid #cfcfcf; width: 279pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          面临问题</td>
                        <td height="19" width="381"
                          style="border: 0.5pt solid #cfcfcf; width: 381pt; height: 14pt; padding-top: 1px; padding-right: 1px; padding-left: 1px; font-size: 11pt; font-family: 宋体; vertical-align: middle; text-align: center;">
                          解决办法</td>
                      </tr>

                      $plan

                    </tbody>
                  </table>
                </div>
              </fieldset>
            </td>
          </tr>
          <tr height="24" style="height:24.0pt;">
            <td style="padding: 10px; background-color: #FFF0D5">
              <span style="font-size: 16px; color: #F1A325">●</span>&nbsp;
              <span>
                <span style="border-bottom: 1px rgb(204, 204, 204); position: relative;">自省、总结、复盘</span>
              </span>
            </td>
          </tr>

          $summarize

        </tbody>
      </table>
    </td>
  </tr>
</tbody>
<!--Footer-->
<div>
    <p
        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif; line-height: 23.8px; widows: 1; text-align: justify; background-color: rgb(225, 245, 255);">
        <b style="font-size: 10.5pt;">&nbsp;</span></b>
    </p>
    <p
        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif; line-height: 23.8px; widows: 1; text-align: justify; background-color: rgb(225, 245, 255);">
        <b style="font-size: 10.5pt;">
            <span lang="EN-US"
                style="font-family: Times New Roman, serif; color: rgb(0, 147, 221);">&nbsp;&nbsp;&nbsp;&nbsp;Best
                regards</span>
        </b>
    </p>
    <p
        style="margin: 0px 0cm; font-family: Microsoft YaHei UI, Tahoma; line-height: 23.8px; widows: 1; text-align: justify; background-color: rgb(225, 245, 255);">
        <b style="font-size: 10.5pt;">
            <span lang="EN-US" style="font-size: 12pt;">
                <font face="黑体">&nbsp;&nbsp;&nbsp;&nbsp;$user</font>
                <font face="Calibri, sans-serif">&nbsp;</font>
            </span>
        </b>
        <b style="font-family: Calibri, sans-serif;">
            <span lang="EN-US" style="font-size: 14pt; font-family: 黑体;">&nbsp;</span>
            <span lang="EN-US" style="font-family: 黑体; font-size: 12px;">$department</span>
        </b>
    </p>
    <p
        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif; line-height: 23.8px; widows: 1; text-align: justify; background-color: rgb(225, 245, 255);">
        <b style="font-size: 10.5pt;">&nbsp;</span></b>
    </p>
</div>

"""