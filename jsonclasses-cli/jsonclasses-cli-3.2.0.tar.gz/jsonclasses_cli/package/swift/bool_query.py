def bool_query():
    return """
public enum BoolQuery: Codable {
    case eq(_ value: Bool)
    case neq(_ value: Bool)
    case null(_ value: Bool)
    case or(_ values: [BoolQuery])
    case and(_ values: [BoolQuery])

    public enum CodingKeys: String, CodingKey {
        case eq = "_eq"
        case neq = "_neq"
        case null = "_null"
        case or = "_or"
        case and = "_and"
    }

    public init(from decoder: Decoder) throws {
        let container = try! decoder.container(keyedBy: CodingKeys.self)
        if container.contains(.eq) {
            self = .eq(try! container.decode(Bool.self, forKey: .eq))
        } else if container.contains(.neq) {
            self = .neq(try! container.decode(Bool.self, forKey: .neq))
        } else if container.contains(.null) {
            self = .null(try! container.decode(Bool.self, forKey: .null))
        } else if container.contains(.or) {
            self = .or(try! container.decode([BoolQuery].self, forKey: .or))
        } else if container.contains(.and) {
            self = .and(try! container.decode([BoolQuery].self, forKey: .and))
        } else {
            self = .eq(true)
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
        case .or(let value):
            try! container.encode(value, forKey: .or)
        case .and(let value):
            try! container.encode(value, forKey: .and)
        }
    }
}

    """.strip() + "\n"
