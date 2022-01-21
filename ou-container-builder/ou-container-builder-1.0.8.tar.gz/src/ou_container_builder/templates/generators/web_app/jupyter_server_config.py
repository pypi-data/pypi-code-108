{% if web_apps %}
    {% for app in web_apps %}
        {% if app.default %}
c.ServerApp.default_url = '{{ app.path }}'
        {% endif %}
    {% endfor %}

c.ServerProxy.servers = {
    {% for app in web_apps %}
    '{{ app.path }}': {
        'command': {{ app.cmdline }},
        {% if app.port %}
        'port': app.port,
        {% endif %}
        {% if app.timeout %}
        'timeout': {{ app.timeout }},
        {% endif %}
        {% if app.absolute_url %}
        'absolute_url': True,
        {% endif %}
    },
    {% endfor %}
}
{% endif %}
