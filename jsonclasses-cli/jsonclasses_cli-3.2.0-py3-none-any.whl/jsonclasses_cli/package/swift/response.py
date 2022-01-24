def response_struct() -> str:
    return """
public struct Response<T: Codable>: Codable {
    let data: T
}
    """.strip() + '\n'
