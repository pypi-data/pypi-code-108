def make_html(data, tests):
    # ---- тесты
    test_amount = len(tests)

    # ввод
    data += "<table class=\"xtable\" cellspacing=\"0\" border=\"0\"><tr>"
    for i in range(1, test_amount + 1):
        data += """<td class="xtd">
                    <b>Ввод {0}</b>
                </td>
                """.format(i)
    data += "</tr>"

    data += "<tr>"
    for test in tests:

        data += "<td class=\"xtdcode\">"

        lines = test[0].split('\n')

        is_first = True

        data += "<a class=\"btn__select\">Copy</a>"

        data += "<div class=\"content\">"

        for line in lines:
            if line != "":

                line = line.replace("<br/>", "<br/")
                line = line.replace("<br/", "<br/>")

                if is_first is False:
                    data += "<br>"

                data += line
                is_first = False

        data += "</div>"

        data += "</td>"

    # вывод
    data += "<tr>"
    for i in range(1, test_amount + 1):
        data += """<td class="xtd">
                    <b>Вывод {0}</b>
                </td>
                """.format(i)
    data += "</tr>"

    data += "<tr>"
    for test in tests:

        data += "<td class=\"xtdcode\">"

        lines = test[1].split('\n')

        is_first = True

        for line in lines:
            if line != "":

                if is_first is False:
                    data += "<br/>"

                data += line
                is_first = False

        data += "</td>"

    data += "</tr></table><br/>"

    data += '''
            <style type="text/css">
                    .btn__select {
                        display: inline-block;
                        margin-top: 5px;
                        margin-bottom: 5px;

                        padding: 1px 10px;
                        background-color: #E7E3E7;
                        border: 1px solid #cec9ce;
                        border-radius: 5px;
                        color: #494849;
                        font-size: 10px;
                        font-family: sans-serif;
                        cursor: pointer;
                        transition: all 0.2s ease-in-out;
                    }

                    .btn__select:hover {
                        background-color: transparent;
                    }
                </style>

                <script>
                    let btnSelects = document.getElementsByClassName("btn__select")

                    for (let i = 0; i < btnSelects.length; i++) {
                        let btn = btnSelects[i]

                        btn.addEventListener('click', () => {
                            let par = btn.closest(".xtdcode")

                            let content = par.querySelector(".content")

                            let text = content.innerHTML
                            text = text.replace(/<br>/g, \"\\n\")

                            console.log(text)

                            const el = document.createElement('textarea');
                            el.value = text;
                            document.body.appendChild(el);
                            el.select();
                            document.execCommand('copy');
                            document.body.removeChild(el);
                        })
                    }
                </script>
        '''

    return data
