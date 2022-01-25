mr_template = """

<tbody>
    <tr>
        <td>
            <table border="0" cellpadding="0" cellspacing="0"
                style="border-collapse: collapse; width:100%; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
                <tbody>
                    <tr height="34"
                        style="height:34.0pt;vertical-align: middle; text-align: center;padding: 10px; background-color: #f3f9f1; border: none; font-size: 20px; font-weight: bold; border-bottom: 1px solid #e5e5e5;">
                        <td style="color: #333; ">$title</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: none;">
                            <fieldset style="border: 1px solid #e5e5e5">
                                <legend style="color: #114f8e;font-size: 16pt;">一、读书：$book</legend>
                                <div style="padding:5px;">
                                    <p
                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                        $book_content
                                    </p>
                                </div>
                            </fieldset>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0px 10px 10px 10px; border: none;">
                            <fieldset style="border: 1px solid #e5e5e5">
                                <legend style="color: #114f8e;font-size: 16pt;">二、月度工作</legend>
                                <div style="padding:5px;">

                                    <table border="0" cellspacing="0" cellpadding="0"
                                        style="border-collapse:collapse;border:none; width:100%">
                                        <tbody>
                                            <!--表头-->
                                            <tr style="font-weight: bold;">
                                                <td width="44"
                                                    style="width:33.3pt;border:solid windowtext 1.0pt;background:#C2D69B;text-align: center;padding: 10px;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">维度
                                                        </span>
                                                    </p>
                                                </td>
                                                <td width="220" colspan="2"
                                                    style="width:214.7pt;border:solid windowtext 1.0pt;border-left:none;background:#C2D69B;text-align: center;padding: 10px;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">要求</span>
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border:solid windowtext 1.0pt;border-left:none;background:#C2D69B;text-align: center;padding: 10px;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">月度进度与结果</span>
                                                    </p>
                                                </td>
                                            </tr>
                                            <!--整体目标-->
                                            <tr>
                                                <td width="44" rowspan="2"
                                                    style="width:33.3pt;border:solid windowtext 1.0pt;border-top:none;text-align: center;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">目标</span>
                                                    </p>
                                                </td>
                                                <td width="420" colspan="2"
                                                    style="width:314.7pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">清楚公司整体目标</span>
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$main_target</span>
                                                </td>
                                            </tr>
                                            <!--拆解目标-->
                                            <tr>
                                                <td width="420" colspan="2"
                                                    style="width:314.7pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family: 宋体; ">根据公司</span>
                                                        <span
                                                            style="font-family: 宋体; color: red; ">目标清楚职责范围内分解团队技术方向和目标</span>
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$team_target</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="44" rowspan="6"
                                                    style="width:33.3pt;border:solid windowtext 1.0pt;border-top:none;text-align: center;padding: 10px;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">职责</span>
                                                    </p>
                                                </td>
                                                <td width="48" rowspan="2"
                                                    style="width:35.8pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;text-align: center;padding: 10px;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">技术</span>
                                                    </p>
                                                </td>
                                                <td width="372"
                                                    style="width:278.9pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family: 宋体; color: red; ">公司系统构整体技术架设计</span>
                                                        <span
                                                            style="font-family: 宋体; ">，新技术预言和可行性分析。<br>技术方案的评估、分解、输出。</span>
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$technology</span>
                                                </td>
                                            </tr>
                                            <tr style="height:12.75pt">
                                                <td width="372"
                                                    style="width:278.9pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;height:12.75pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        专利输出（上半年 3个，下半年 3个）
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;height:12.75pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$patent</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="48" rowspan="4"
                                                    style="width:35.8pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;text-align: center;padding: 10px">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family:宋体;">事
                                                        </span>
                                                    </p>
                                                </td>
                                                <td width="372"
                                                    style="width:278.9pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        组织阶段技术评审对交付代码质量负责
                                                    </p>
                                                </td>
                                                <td width="472"
                                                    style="width:353.65pt;border-top:none;border-left:none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$review</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        技术问题和难题的协助和推进
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$technology_issues</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        运维相关的技术或者资源问题进行辅导
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$maintainance</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        规范软件开发流程，执行制度流程上职责负责的内容
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$duties</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="44" rowspan="2"
                                                    style="width:33.3pt;border:solid windowtext 1.0pt;border-top:none;text-align: center;padding: 10px">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        结果
                                                    </p>
                                                </td>
                                                <td width="48" rowspan="2" style="width:35.8pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            text-align: center;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        事
                                                    </p>
                                                </td>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span
                                                            style="font-family: 宋体; color: red; background-image: initial; background-position: initial; background-size: initial; 
                                                            background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;">无严重质量问题为前提：
                                                            <br></span>团队项目完成率（&gt;=85%)，=20%
                                                        <br>团队项目完成率（75%&lt;X&lt;85%)，=15%
                                                        <br>团队项目完成率（60%&lt;X&lt;75%)，=10%
                                                        <br>团队项目完成率（&lt;60%)，或者出现严重质量问题=0%
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        见团队实际项目情况
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        根据项目要求完成编码输出工作
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$programming_work</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="44" rowspan="2"
                                                    style="width:33.3pt;border:solid windowtext 1.0pt;border-top:none;text-align: center;">
                                                    <p
                                                        style="margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        学习
                                                    </p>
                                                </td>
                                                <td width="48"
                                                    style="width:35.8pt;border-top:none;border-left:none;border-bottom:
                                            solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="text-align: justify; margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span lang="EN-US" style="font-family:宋体;">
                                                            <o:p>&nbsp;</o:p>
                                                        </span>
                                                    </p>
                                                </td>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family: 宋体; ">
                                                            读书学到的应用，应用到日常工作和生活中。
                                                            <br>1.</span>月度总结报告呈现。（6%）
                                                        <br>2.月度总结会议中呈现。（2%）
                                                        <br>3.项目例会中呈现。（2%）
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$reading_share</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="48"
                                                    style="width:35.8pt;border-top:none;border-left:none;border-bottom:
                                            solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="text-align: justify; margin: 0px 0cm; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span lang="EN-US" style="font-family:宋体;">
                                                            <o:p>&nbsp;</o:p>
                                                        </span>
                                                    </p>
                                                </td>
                                                <td width="372" style="width:278.9pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <p
                                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                                        <span style="font-family: 宋体; ">指导和影响团队学习。</span>
                                                        <br>1.推荐团队成员优秀
                                                        <span style="font-family: 宋体; color: red; ">书籍</span>
                                                        <span style="font-family: 宋体; ">。（2%）</span>

                                                        <br>2.给予团队
                                                        <span style="font-family: 宋体; color: red; ">培训</span>
                                                        <span style="font-family: 宋体; ">。（5%）</span>

                                                        <br>3.给予团队工作
                                                        <span style="font-family: 宋体; color: red; ">指导</span>
                                                        <span style="font-family: 宋体; ">。（3%）</span>
                                                    </p>
                                                </td>
                                                <td width="472" style="width:353.65pt;border-top:none;border-left:none;
                                            border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
                                            padding:0cm 5.4pt 0cm 5.4pt">
                                                    <span style="font-family: 宋体; font-size: 10.5pt;">$direction</span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </fieldset>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: none;">
                            <fieldset style="border: 1px solid #e5e5e5">
                                <legend style="color: #114f8e;font-size: 16pt;">三、学习</legend>
                                <div style="padding:5px;">
                                    <p
                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                        $study
                                    </p>
                                </div>
                            </fieldset>
                        </td>
                    </tr>
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

mstudy_template = """

<tbody>
    <tr>
        <td>
            <table border="0" cellpadding="0" cellspacing="0"
                style="border-collapse: collapse; width:100%; background-color: #fff; border: 1px solid #cfcfcf; box-shadow: 0 0px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; font-size:13px;">
                <tbody>
                    <tr height="34"
                        style="height:34.0pt;vertical-align: middle; text-align: center;padding: 10px; background-color: #f3f9f1; border: none; font-size: 20px; font-weight: bold; border-bottom: 1px solid #e5e5e5;">
                        <td style="color: #333; ">$title</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: none;">
                            <fieldset style="border: 1px solid #e5e5e5">
                                <legend style="color: #114f8e;font-size: 16pt;">一、读书：$book</legend>
                                <div style="padding:5px;">
                                    <p
                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                        $book_content
                                    </p>
                                </div>
                            </fieldset>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: none;">
                            <fieldset style="border: 1px solid #e5e5e5">
                                <legend style="color: #114f8e;font-size: 16pt;">二、学习</legend>
                                <div style="padding:5px;">
                                    <p
                                        style="margin: 0px 0cm; text-align: justify; font-size: 10.5pt; font-family: Calibri, sans-serif;">
                                        $study
                                    </p>
                                </div>
                            </fieldset>
                        </td>
                    </tr>
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