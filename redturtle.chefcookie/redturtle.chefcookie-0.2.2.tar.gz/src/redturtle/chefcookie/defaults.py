# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from redturtle.chefcookie import _
from zope.globalrequest import getRequest
from zope.i18n import translate

import json
import six

PANEL_HEADER = {
    "en": '<h2>We use cookies</h2><p>This site uses technical cookies necessary for the proper functioning of the pages, and third-party profiling cookies. By selecting <b>Allow all</b> you are consenting to the use of analytics and profiling cookies. By closing the banner, only the technical cookies necessary for navigation will be used and some contents may not be available. Your preferences can be changed at any time from the "Manage cookie settings" side menu. For more information, please read our <a href="{policy_url}" target="_blank">Cookie Policy</a>.</p>',
    "it": '<h2>Usiamo i cookies</h2><p>Questo sito utilizza cookie tecnici necessari al corretto funzionamento delle pagine, e cookie di profilazione di terze parti. Selezionando <b>Accetta tutto</b> si acconsente all’utilizzo dei cookie analytics e di profilazione. Chiudendo il banner verranno utilizzati solo i cookie tecnici necessari alla navigazione e alcuni contenuti potrebbero non essere disponibili. Le preferenze possono essere modificate in qualsiasi momento dal menu laterale "Gestisci impostazioni cookie".</p><p>Per maggiori informazioni, ti invitiamo a consultare la nostra <a href="{policy_url}" target="_blank">Cookie Policy</a>.</p>',
}

LABELS = {
    "general": {
        "accept": {"en": "Save and continue", "it": "Salva e continua"},
        "accept_all": {"en": "Allow all", "it": "Accetta tutto"},
        "settings_open": {"en": "Personalizza", "it": "Personalizza"},
        "settings_close": {
            "en": "Close settings",
            "it": "Chiudi impostazioni",
        },
        "group_open": {
            "en": "Show more information",
            "it": "Mostra altre informazioni",
        },
        "group_close": {
            "en": "Close more information",
            "it": "Chiudi altre informazioni",
        },
        "decline": {
            "en": "Technical cookies only",
            "it": "Solo cookie tecnici",
        },
        "details_open": {"en": "Show details", "it": "Mostra dettagli"},
        "details_close": {"en": "Close details", "it": "Chiudi dettagli"},
    },
    "technical_cookies": {
        "title": {"en": "Technical Cookies", "it": "Cookie tecnici"},
        "description": {
            "en": "These cookies are strictly necessary for the website to work or for you to use requested services.",
            "it": "Il sito utilizza cookie tecnici per analizzare il traffico da e verso il sito. I cookie tecnici consento anche di fornire un migliore servizio di navigazione sul sito, e raccolgono informazioni di navigazione a questo scopo.",
        },
    },
    "functional_cookies": {
        "title": {"en": "Functional Cookies", "it": "Cookie funzionali"},
        "description": {
            "en": "<p>We use functionality cookies to enable specific website functions and to configure the Website depending on your choices.</p>",
            "it": "<p>Utilizziamo cookie funzionali per abilitare specifiche funzionalità del sito e per configurarlo a seconda delle tue scelte.</p>",
        },
    },
    "analytics_cookies": {
        "title": {
            "en": "Analytics and Site Statistics",
            "it": "Cookie analytics e statistiche",
        },
        "description": {
            "en": "<p>We use analytics cookies to track user navigation and make some analysis. We don't track any personal information about the user.</p>",
            "it": "<p>I cookie di Analytics sono usati per analizzare la navigazione sul sito al fine di migliorarla e fornire all'utente un'esperienza di navigazione migliore possibile.</p>",
        },
    },
    "profiling_cookies": {
        "title": {"en": "Profiling Cookies", "it": "Cookie di profilazione"},
        "description": {
            "en": "<p>The site uses profiling cookies to analyze user behavior and choices in order to propose targeted content corresponding to the user's profile. These cookies can only be installed upon your prior consent. Disallowing these cookies, some contents may not be available.</p>",
            "it": "<p>Il sito utilizza cookie di profilazione per analizzare il comportamento e le scelte degli utenti al fine di proporre contenuti mirati corrispondenti al profilo dell'utente. Questi cookie possono essere installati solamente dietro tuo consenso. Il blocco di questi cookie potrebbe impedire la visualizzazione di particolari contenuti del sito.</p>",
        },
    },
    "profiling_cookies_specific": {
        "facebook": {
            "title": {"en": "Facebook", "it": "Facebook"},
            "description": {
                "en": "<p>This cookie is used by Facebook to show relevant advertising when navigating Facebook products.</p>",
                "it": "<p>Questo cookie viene utilizzato da Facebook per mostrare pubblicità pertinente durante la navigazione dei prodotti Facebook.</p>",
            },
        },
        "hotjar": {
            "title": {"en": "HotJar", "it": "Hotjar"},
            "description": {
                "en": "<p>Hotjar is a technology service that helps us better understand our users' navigation (e.g. how much time users  spend on which pages, which links users choose to click, etc.) and this enables us to build and maintain our service with user feedback.</p>",
                "it": "<p>Hotjar è un servizio che ci aiuta a comprendere meglio la navigazione dei nostri utenti (ad es. quanto tempo gli utenti trascorrono su quali pagine, su quali collegamenti gli utenti scelgono di fare clic, ecc.) e questo ci consente di creare e mantenere il nostro servizio con il feedback degli utenti.</p>",
            },
        },
        "youtube": {
            "title": {"en": "YouTube", "it": "YouTube"},
            "description": {
                "en": "<p>YouTube cookies are installed only if you play one of our embedded videos. The cookies are used to store information about the videos played and other information related to the player.</p>",
                "it": "<p>I cookie di YouTube vengono installati solo se riproduci uno dei nostri video incorporati. I cookie vengono utilizzati per memorizzare informazioni sui video riprodotti e altre informazioni relative al lettore.</p>",
            },
        },
        "linkedin": {
            "title": {"en": "LinkedIn", "it": "LinkedIn"},
            "description": {
                "en": "<p>LinkedIn cookies are installed by the LinkedIn Insight tag to enable retargeting, in-depth campaign reporting and to help us unlock insights about our website visitors.</p>",
                "it": "<p>I cookie di LinkedIn vengono installati dal tag LinkedIn Insight per consentire il retargeting, rapporti approfonditi sulle campagne e per aiutarci a ottenere informazioni dettagliate sui visitatori del nostro sito Web.</p>",
            },
        },
    },
}

IFRAMES_MAPPING = [
    u"youtube|youtube.com,youtube-nocookie.com, youtu.be",
    u"facebook|facebook.com",
]
ANCHOR_MAPPING = [u"twitter|twitter-timeline"]

if six.PY2:
    HEADER_LABELS = json.dumps(PANEL_HEADER, indent=4).decode("utf-8")
    GENERAL_LABELS = json.dumps(LABELS["general"], indent=4).decode("utf-8")
    TECHNICAL_COOKIES_LABELS = json.dumps(LABELS["technical_cookies"], indent=4).decode(
        "utf-8"
    )
    FUNCTIONAL_COOKIES_LABELS = json.dumps(
        LABELS["functional_cookies"], indent=4
    ).decode("utf-8")
    ANALYTICS_COOKIES_LABELS = json.dumps(LABELS["analytics_cookies"], indent=4).decode(
        "utf-8"
    )
    PROFILING_COOKIES_LABELS = json.dumps(LABELS["profiling_cookies"], indent=4).decode(
        "utf-8"
    )
    PROFILING_COOKIES_SPECIFIC_LABELS = json.dumps(
        LABELS["profiling_cookies_specific"], indent=4
    ).decode("utf-8")
else:
    HEADER_LABELS = json.dumps(PANEL_HEADER, indent=4)
    GENERAL_LABELS = json.dumps(LABELS["general"], indent=4)
    TECHNICAL_COOKIES_LABELS = json.dumps(LABELS["technical_cookies"], indent=4)
    FUNCTIONAL_COOKIES_LABELS = json.dumps(LABELS["functional_cookies"], indent=4)
    ANALYTICS_COOKIES_LABELS = json.dumps(LABELS["analytics_cookies"], indent=4)
    PROFILING_COOKIES_LABELS = json.dumps(LABELS["profiling_cookies"], indent=4)
    PROFILING_COOKIES_SPECIFIC_LABELS = json.dumps(
        LABELS["profiling_cookies_specific"], indent=4
    )


def iframe_placeholder(name, soup=None):
    request = getRequest()
    if not soup:
        soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag("div")
    tag["class"] = "iframe-placeholder"
    tag[
        "style"
    ] = "padding: 10px; background-color: #eee; border:1px solid #ccc;width:98%; max-width:500px"
    p_tag = soup.new_tag("p")
    p_tag.string = translate(
        _(
            "iframe_placeholder_text_1",
            default=u"You need to enable ${name} cookies to see this content.",
            mapping={"name": name},
        ),
        context=request,
    )
    tag.append(p_tag)

    span_tag = soup.new_tag("span")
    span_tag.string = translate(
        _(
            "iframe_placeholder_text_2",
            default=u"Please",
        ),
        context=request,
    )
    tag.append(span_tag)

    a_tag_enable_yt = soup.new_tag("a", href="#")
    a_tag_enable_yt["data-cc-enable"] = name
    a_tag_enable_yt.string = translate(
        _(
            "iframe_placeholder_text_3",
            default=u"enable them",
        ),
        context=request,
    )
    tag.append(a_tag_enable_yt)

    span_tag = soup.new_tag("span")
    span_tag.string = translate(
        _(
            "iframe_placeholder_text_4",
            default=u" or ",
        ),
        context=request,
    )
    tag.append(span_tag)

    a_tag_open_cc = soup.new_tag("a", href="#")
    a_tag_open_cc["data-cc-open"] = ""
    a_tag_open_cc.string = translate(
        _(
            "iframe_placeholder_text_5",
            default=u"manage your preferences",
        ),
        context=request,
    )
    tag.append(a_tag_open_cc)
    return tag


def anchor_placeholder(provider_name):
    request = getRequest()
    soup = BeautifulSoup("", "html.parser")
    tag = soup.new_tag("div")
    tag["class"] = "{}-placeholder".format(provider_name)
    tag[
        "style"
    ] = "padding: 10px; background-color: #eee; border:1px solid #ccc;width:98%; max-width:500px"
    p_tag = soup.new_tag("p")

    human_readable_provider_name = translate(
        _(provider_name), domain="redturtle.chefcookie", context=request
    )
    p_tag.string = translate(
        _(
            "iframe_placeholder_text_1",
            default=u"You need to enable ${name} cookies to see this content.",
            mapping={"name": human_readable_provider_name},
        ),
        context=request,
    )
    tag.append(p_tag)

    span_tag = soup.new_tag("span")
    span_tag.string = translate(
        _(
            "iframe_placeholder_text_2",
            default=u"Please",
        ),
        context=request,
    )
    tag.append(span_tag)

    a_tag_enable_yt = soup.new_tag("a", href="#")
    a_tag_enable_yt["data-cc-enable"] = provider_name
    a_tag_enable_yt.string = translate(
        _(
            "iframe_placeholder_text_3",
            default=u"enable them",
        ),
        context=request,
    )
    tag.append(a_tag_enable_yt)

    span_tag = soup.new_tag("span")
    span_tag.string = translate(
        _(
            "iframe_placeholder_text_4",
            default=u" or ",
        ),
        context=request,
    )
    tag.append(span_tag)

    a_tag_open_cc = soup.new_tag("a", href="#")
    a_tag_open_cc["data-cc-open"] = ""
    a_tag_open_cc.string = translate(
        _(
            "iframe_placeholder_text_5",
            default=u"manage your preferences",
        ),
        context=request,
    )
    tag.append(a_tag_open_cc)
    return tag
