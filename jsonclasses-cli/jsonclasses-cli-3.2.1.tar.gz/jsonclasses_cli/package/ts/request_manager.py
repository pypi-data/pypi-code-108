def request_manager(base_url: str,use_session:bool) -> str:
    return f"""
class RequestManager {"{"}

    static share = new RequestManager()

    #baseURL: string = "{base_url}"


    get headers() {"{"}
        const token = {'SessionManager.share.hasSession() ? SessionManager.share.getToken() : ' if use_session else ''} undefined 
        return token ? {"{"}
            headers: {"{"}
                'Authorization': `Bearer ${"{"}token{"}"}`
            {"}"}
        {"}"} : undefined
    {"}"}

    qs(val: any): string {"{"}
        if (!val) {"{"}
            return ''
        {"}"}
        if (Object.keys(val).length === 0) {"{"}
            return ''
        {"}"}
        return '?' + stringify(val)
    {"}"}

    async post<T, U, V>(url: string, input: T, query: V | undefined = undefined): Promise<U> {"{"}
        const response = await axios.post(this.#baseURL + url + this.qs(query), input, this.headers)
        return response.data.data
    {"}"}

    async patch<T, U, V>(url: string, input: T, query: V | undefined = undefined): Promise<U> {"{"}
        const response = await axios.patch(this.#baseURL + url + this.qs(query), input, this.headers)
        return response.data.data
    {"}"}

    async delete<V>(url: string, query: V | undefined = undefined): Promise<void> {"{"}
        await axios.delete(this.#baseURL + url + this.qs(query), this.headers)
        return
    {"}"}

    async get<U, V>(url: string, query: V | undefined = undefined): Promise<U> {"{"}
        const response = await axios.get(this.#baseURL + url + this.qs(query), this.headers)
        return response.data.data
    {"}"}
{"}"}
    """.strip() + '\n'
