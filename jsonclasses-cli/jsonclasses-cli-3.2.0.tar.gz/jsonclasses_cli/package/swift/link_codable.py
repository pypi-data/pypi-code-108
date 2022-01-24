def link_codable() -> str:
    return """
public class Link: Codable {
    public var _add: String
    public init(link: String) {
        self._add = link
    }
}

public class UnLink: Codable {
    public var _del: String
    public init(unLink: String) {
        self._del = unLink
    }
}

public enum CreateOrLink<T: Codable>: Codable{
    case createInput(T)
    case link(Link)
}

public enum UpdateOrLink<T: Codable>: Codable{
    case updateInput(T)
    case link(Link)
    case unLink(UnLink)
}
    """.strip() + '\n'
