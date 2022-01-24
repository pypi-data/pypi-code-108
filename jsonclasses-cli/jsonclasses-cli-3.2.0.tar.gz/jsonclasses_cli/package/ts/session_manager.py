

def session_manager(items: dict[str, str]) -> str:
    session_items: list[str] = []
    for (_, c) in items.items():
        session_items.append(c + 'Session')
    sessions = ' | '.join(session_items)
    return f"""
class SessionManager {'{'}

    #sessionKey = '_jsonclasses_session'
    #session: {sessions} | undefined

    static share = new SessionManager()

    constructor() {'{'}
        const item = localStorage.getItem(this.#sessionKey)
        if (item && item !== null && item !== '') {'{'}
            this.#session = JSON.parse(item)
        {'}'} else {'{'}
            this.#session = undefined
        {'}'}
    {'}'}

    setSession(session: {sessions} | undefined | null) {'{'}
        if (session) {'{'}
            this.#session = session
            localStorage.setItem(this.#sessionKey, JSON.stringify(session))
        {'}'} else {'{'}
            this.#session = undefined
            localStorage.removeItem(this.#sessionKey)
        {'}'}
    {'}'}

    hasSession(): boolean {'{'}
        return this.#session !== undefined
    {'}'}

    getToken(): string | undefined {'{'}
        return this.#session?.token
    {'}'}

    getSession(): {sessions} | undefined {'{'}
        return this.#session
    {'}'}

    clearSession() {'{'}
        this.#session = undefined
        localStorage.removeItem(this.#sessionKey)
    {'}'}
{'}'}
    """.strip() + "\n"
