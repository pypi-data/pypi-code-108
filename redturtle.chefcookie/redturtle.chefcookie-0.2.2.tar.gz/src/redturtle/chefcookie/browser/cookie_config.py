# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from redturtle.chefcookie import _
from redturtle.chefcookie.interfaces import IChefCookieSettings
from plone import api
from plone.memoize import view
from zope.i18n import translate

import logging
import json
import six

logger = logging.getLogger(__name__)

TEMPLATE = """

var iframeCookies = {iframe_cookies_ids_placeholder};
var anchorCookies = {anchor_cookies_ids_placeholder};
var profiling_cookies_config = {profiling_cookies_config_placeholder};

function accept_anchor_based_provider(cc, placeholder_identifier){
    $("div." + placeholder_identifier).each(function(){
        var placeholder = $(this);
        var anchor = placeholder.next();
        var twitter = anchor.next();
        var anchor_href = anchor.data().ccHref;
        var twitter_src = twitter.data().ccSrc;
        var name = anchor.data().ccName;
        if(cc.isAccepted(name)){
            anchor.attr('href', anchor_href);
            anchor.attr('hidden', false);
            twitter.attr('hidden', false);
            twitter.attr('src', twitter_src);
            placeholder.attr('hidden', true);
        }// else {
        //   anchor.attr('href', '');
        //   anchor.attr('hidden', true);
        //   twitter.attr('hidden', true);
           // we need to identify the iframe
        //   debugger;
        //   twitter.attr('src', );
        //   placeholder.attr('hidden', false);
        // }
    });
}

function decline_anchor_based_provider(cc, placeholder_identifier){
    debugger;
}

function accept_twitter_timeline(cc){
    var placeholder_identifier = 'twittertimeline-placeholder';
    accept_anchor_based_provider(cc, placeholder_identifier);
}

function decline_twitter_timeline(cc){
    var placeholder_identifier = 'twittertimeline-placeholder';
    decline_anchor_based_provider(cc, placeholder_identifier);

}

function accept_iframe(cc) {
    $("iframe").each(function() {
        var iframe = $(this);
        var src = iframe.data().ccSrc;
        var name = iframe.data().ccName;
        var placeholder = $(this).prev('.iframe-placeholder');
        if (placeholder.length && src) {
            if(cc.isAccepted(name)){
                iframe.attr('src', src);
                iframe.attr('hidden', false);
                placeholder.attr('hidden', true);
            } else {
                iframe.attr('src', '');
                iframe.attr('hidden', true);
                placeholder.attr('hidden', false);
            }
        }
    });
}

if (Object.keys(profiling_cookies_config).length > 0) {
    var has_hotjar = {has_hotjar_placeholder};

    iframeCookies.forEach(function(name) {
        if (profiling_cookies_config.scripts[name] !== undefined) {
            profiling_cookies_config.scripts[name].accept = (cc, resolve, isInit) => {
                accept_iframe(cc);
                if (name === 'facebook' && profiling_cookies_config.scripts[name].id) {
                    let script = document.createElement('script');
                    script.innerHTML =
                        "!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init', '" +
                        profiling_cookies_config.scripts[name].id +
                        "');fbq('track', 'PageView');fbq('track', 'ViewContent');";
                    document.head.appendChild(script);
                    window.chefcookie_loaded.push(name);
                }
            };
        }
    });

    anchorCookies.forEach(function(name) {
        if (profiling_cookies_config.scripts[name] !== undefined) {
            profiling_cookies_config.scripts[name].accept = (cc, resolve, isInit) => {
                if (name === 'twittertimeline'){
                    accept_twitter_timeline(cc);
                }
            };
            profiling_cookies_config.scripts[name].decline = (provider) =>{
                decline_twitter_timeline(cc);
            };
        }
    });

    if (has_hotjar) {
        var hjLabels = {hotjar_labels_placeholder};
        profiling_cookies_config.scripts.hotjar = {
            id: "{hotjar_id_placeholder}",
            title: hjLabels.title,
            description: hjLabels.description,
            accept: function(cc, resolve, isInit) {
                var id = cc.config.settings[1].scripts.hotjar.id;
                var script = document.createElement("script");
                script.innerHTML =
                    "(function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};h._hjSettings={hjid:" +
                    id +
                    ",hjsv:6};a=o.getElementsByTagName('head')[0];r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;a.appendChild(r);})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=')";
                document.head.appendChild(script);
                cc.setLoaded("hotjar");
            },
        }
    }
}

var cookies_settings = [];
var technical_cookies = {technical_cookies_placeholder};

if (Object.keys(technical_cookies).length > 0) {
    cookies_settings.push(technical_cookies);
}

if (Object.keys(profiling_cookies_config).length > 0) {
    cookies_settings.push(profiling_cookies_config);
}

var cc = new redturtlechefcookie({
  message: {message_labels_placeholder},
  accept_all_if_settings_closed: false,
  show_decline_button: true,
  scripts_selection: "true", // false|true|'collapse'
  debug_log: true,
  consent_tracking: null, // '/wp-json/v1/track-consent.php'
  expiration: 180, // in days
  exclude_google_pagespeed: false,
  style: {
    layout: "bottombar", //"overlay", // overlay|bottombar|topbar
    size: 1, // 1|2|3|4|5
    color_text: "#4d4d4d",
    color_highlight: "",
    color_background: "#eeeeee",
    highlight_accept: true,
    show_disabled_checkbox: true,
    noscroll: false,
    fade: true,
    blur: true,
    css_add: "",
  },
  labels: {labels_placeholder},
  exclude: [
    // exclude privacy site if needed
    // exclude wordpress users
    () => {
      return (
        document.cookie !== undefined &&
        document.cookie.indexOf("wp-settings-time") > -1
      );
    }
  ],
  settings: cookies_settings,
});
document.addEventListener("DOMContentLoaded", () => {
  cc.init();
  accept_iframe(cc);
  document.querySelectorAll(".pat-tiles-management").forEach(el => {
    el.addEventListener("rtTilesLoaded", e => {
      accept_iframe(cc);
    });
  });

  cc.registerEventListener(document, "click", e => {
    if (
      e.target.hasAttribute("data-cc-open-settings") ||
      (e.target.tagName !== "A" && e.target.closest("[data-cc-open-settings]"))
    ) {
      cc.open();
      cc.showSettings();
      cc.switchSettingsLabelsOpen();
      e.preventDefault();
    }
  });

  cc.registerEventListener(document, "click", e => {
    if (e.target.classList.contains("data-cc-open")) {
      cc.open();
      cc.showSettings();
      cc.switchSettingsLabelsOpen();
      e.preventDefault();
    }
    if (
      e.target.hasAttribute("data-cc-destroy") ||
      (e.target.tagName !== "A" && e.target.closest("[data-cc-destroy]"))
    ) {
      cc.setCookieToHideOverlay();
      cc.close();
      e.preventDefault();
    }
    if (e.target.hasAttribute("data-cc-accept-all")) {
      cc.acceptAllScripts();
      cc.setCookieToHideOverlay();
      cc.close();
      e.preventDefault();
    }
  });

  $('body').append('<a title="{open_settings_placeholder}" id="cookie-settings-open" {data_cc_open_placeholder}=“” href=“/”><svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="user-lock" class="svg-inline--fa fa-user-lock fa-w-20" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="currentColor" d="M224 256A128 128 0 1 0 96 128a128 128 0 0 0 128 128zm96 64a63.08 63.08 0 0 1 8.1-30.5c-4.8-.5-9.5-1.5-14.5-1.5h-16.7a174.08 174.08 0 0 1-145.8 0h-16.7A134.43 134.43 0 0 0 0 422.4V464a48 48 0 0 0 48 48h280.9a63.54 63.54 0 0 1-8.9-32zm288-32h-32v-80a80 80 0 0 0-160 0v80h-32a32 32 0 0 0-32 32v160a32 32 0 0 0 32 32h224a32 32 0 0 0 32-32V320a32 32 0 0 0-32-32zM496 432a32 32 0 1 1 32-32 32 32 0 0 1-32 32zm32-144h-64v-80a32 32 0 0 1 64 0z"></path></svg></a>');

});
"""


class View(BrowserView):
    @property
    @view.memoize
    def youtube_enabled(self):
        return self.get_registry_settings(name="youtube")

    def __call__(self):
        self.request.response.setHeader(
            "Content-type", " application/javascript; charset=utf-8"
        )
        # i can't use format method because there are a lot of brackets
        manage_cookie_label = translate(
            _(
                "manage_cookie_settings_label",
                default=u"Manage cookie settings",
            ),
            context=self.request,
        )

        manage_cc_open = "data-cc-open-settings"
        if self.get_only_technical_cookies_values():
            manage_cc_open = "data-cc-open"

        if six.PY2:
            manage_cookie_label = manage_cookie_label.encode("utf-8")
        return (
            TEMPLATE.replace(
                "{iframe_cookies_ids_placeholder}",
                json.dumps(self.get_iframe_cookies_ids()),
            )
            .replace(
                "{anchor_cookies_ids_placeholder}",
                json.dumps(self.get_anchor_cookies_ids()),
            )
            .replace(
                "{profiling_cookies_config_placeholder}",
                self.get_profiling_cookies_config(),
            )
            .replace("{has_hotjar_placeholder}", json.dumps(self.has_hotjar()))
            # .replace("{youtube_labels_placeholder}", self.get_youtube_labels())
            .replace("{hotjar_labels_placeholder}", self.get_hotjar_labels())
            .replace(
                "{hotjar_id_placeholder}",
                self.get_registry_settings(name="hotjar_id") or "''",
            )
            .replace("{message_labels_placeholder}", self.get_message_labels())
            .replace("{labels_placeholder}", self.get_labels())
            .replace(
                "{technical_cookies_placeholder}",
                self.get_tech_cookies_config(),
            )
            .replace("{settings_placeholder}", self.get_settings())
            .replace(
                "{open_settings_placeholder}",
                manage_cookie_label,
            )
            .replace(
                "{data_cc_open_placeholder}",
                manage_cc_open,
            )
        )

    @view.memoize
    def get_registry_settings(self, name, load_json=False):
        try:
            value = api.portal.get_registry_record(name, interface=IChefCookieSettings)
            if load_json:
                value = json.loads(value)
            if isinstance(value, six.string_types) and six.PY2:
                value = value.encode("utf-8")
            return value
        except Exception as e:
            logger.exception(e)
            return ""

    def get_message_labels(self):
        labels = self.get_registry_settings("header_labels") or "{}"
        policy_url = self.get_registry_settings("policy_url")
        if policy_url:
            labels = labels.replace("{policy_url}", policy_url)
        return labels

    def get_labels(self):
        labels = self.get_registry_settings(name="general_labels") or "{}"
        return labels

    def get_settings(self):
        tech_cookies = self.get_tech_cookies_config()
        profiling_cookies = self.get_profiling_cookies_config()

        res = []
        if tech_cookies:
            res.append(tech_cookies)
        if profiling_cookies:
            res.append(profiling_cookies)
        return json.dumps(res)

    def get_only_technical_cookies_values(self):
        value = self.get_registry_settings(name="only_technical_cookies")
        if not value:
            return False
        return True

    def get_tech_cookies_config(self):

        res = {
            "checked_by_default": True,
            "cannot_be_modified": True,
            "initial_tracking": True,
        }

        labels = self.get_registry_settings(name="technical_cookies_labels")
        analytics_cookies_labels = self.get_registry_settings(
            name="analytics_cookies_labels"
        )
        functional_cookies_labels = self.get_registry_settings(
            name="functional_cookies_labels"
        )
        analytics_id = self.get_registry_settings(name="analytics_id")

        if labels:
            res.update(json.loads(labels))

        scripts = {}
        if functional_cookies_labels:
            scripts["techcookies"] = json.loads(functional_cookies_labels)
        if analytics_id and analytics_cookies_labels:
            analytics_data = {"id": analytics_id}
            analytics_data.update(json.loads(analytics_cookies_labels))
            scripts["analytics"] = analytics_data

        if scripts:
            res.update({"scripts": scripts})
        return json.dumps(res)

    def get_profiling_cookies_config(self):

        facebook_id = self.get_registry_settings(name="facebook_id")
        iframe_cookies_ids = self.get_iframe_cookies_ids()
        anchor_cookies_ids = self.get_anchor_cookies_ids()
        hotjar_id = self.get_registry_settings(name="hotjar_id")
        linkedin_id = self.get_registry_settings(name="linkedin_id")
        profiling_cookies_labels = self.get_registry_settings(
            name="profiling_cookies_labels", load_json=True
        )
        profiling_cookies_specific_labels = self.get_registry_settings(
            name="profiling_cookies_specific_labels", load_json=True
        )

        if (
            not hotjar_id  # noqa
            and not linkedin_id  # noqa
            and not iframe_cookies_ids  # noqa
            and not anchor_cookies_ids  # noqa
        ):
            return "{}"

        scripts = {}

        for iframe_id in iframe_cookies_ids:
            labels = profiling_cookies_specific_labels.get(iframe_id, {})
            if labels:
                scripts[iframe_id] = labels

        # handle provider base on anchor like twitter timeline
        for anchor_id in anchor_cookies_ids:
            labels = profiling_cookies_specific_labels.get(anchor_id, {})
            if labels:
                scripts[anchor_id] = labels

        if facebook_id:
            if "facebook" not in scripts:
                labels = profiling_cookies_specific_labels.get("facebook", {})
                if labels:
                    scripts["facebook"] = labels
            scripts["facebook"]["id"] = facebook_id

        if linkedin_id and "linkedin" in profiling_cookies_specific_labels:
            scripts["linkedin"] = {"id": linkedin_id}
            scripts["linkedin"].update(profiling_cookies_specific_labels["linkedin"])

        res = {
            "checked_by_default": False,
            "cannot_be_modified": False,
            "initial_tracking": False,
        }
        res.update(profiling_cookies_labels)
        res["scripts"] = scripts

        return json.dumps(res)

    def get_profiling_labels_by_name(self, name):
        labels = self.get_registry_settings(
            name="profiling_cookies_specific_labels", load_json=True
        )
        if not labels:
            return {}

        return labels.get(name, {})

    def has_hotjar(self):
        id = self.get_registry_settings(name="hotjar_id")
        labels = self.get_profiling_labels_by_name(name="hotjar")

        if id and labels:
            return True
        return False

    def get_hotjar_labels(self):
        return json.dumps(self.get_profiling_labels_by_name(name="hotjar"))

    def get_iframe_cookies_ids(self):
        data = self.get_registry_settings(name="iframes_mapping")

        res = []
        for mapping in data:
            id, domains = mapping.split("|")
            res.append(id)
        return res

    def get_anchor_cookies_ids(self):
        data = self.get_registry_settings(name="links_mapping")

        res = []
        for mapping in data:
            id, domains = mapping.split("|")
            res.append(id)
        return res
