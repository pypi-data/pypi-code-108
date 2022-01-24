def id_query():
    return """
public enum IDQuery: Codable {
    case eq(_ value: String)
    case neq(_ value: String)
    case null(_ value: Bool)

    public enum CodingKeys: String, CodingKey {
        case eq = "_eq"
        case neq = "_neq"
        case null = "_null"
    }

    public init(from decoder: Decoder) throws {
        let container = try! decoder.container(keyedBy: CodingKeys.self)
        if container.contains(.eq) {
            self = .eq(try! container.decode(String.self, forKey: .eq))
        } else if container.contains(.neq) {
            self = .neq(try! container.decode(String.self, forKey: .neq))
        } else if container.contains(.null) {
            self = .null(try! container.decode(Bool.self, forKey: .null))
        } else {
            throw NSError()
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .eq(let value):
            try! container.encode(value, forKey: .eq)
        case .neq(let value):
            try! container.encode(value, forKey: .neq)
        case .null(let value):
            try! container.encode(value, forKey: .null)
        }
    }
}
    """.strip() + "\n"
