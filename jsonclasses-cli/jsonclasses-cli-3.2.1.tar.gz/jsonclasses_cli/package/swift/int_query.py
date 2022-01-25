def int_query():
    return """
public enum IntQuery: Codable {
    case eq(_ value: Int)
    case neq(_ value: Int)
    case null(_ value: Bool)
    case gt(_ value: Int)
    case gte(_ value: Int)
    case lt(_ value: Int)
    case lte(_ value: Int)
    case or(_ values: [IntQuery])
    case and(_ values: [IntQuery])

    public enum CodingKeys: String, CodingKey {
        case eq = "_eq"
        case neq = "_neq"
        case null = "_null"
        case gt = "_gt"
        case gte = "_gte"
        case lt = "_lt"
        case lte = "_lte"
        case or = "_or"
        case and = "_and"
    }

    public init(from decoder: Decoder) throws {
        let container = try! decoder.container(keyedBy: CodingKeys.self)
        if container.contains(.eq) {
            self = .eq(try! container.decode(Int.self, forKey: .eq))
        } else if container.contains(.neq) {
            self = .neq(try! container.decode(Int.self, forKey: .neq))
        } else if container.contains(.null) {
            self = .null(try! container.decode(Bool.self, forKey: .null))
        } else if container.contains(.gt) {
            self = .gt(try! container.decode(Int.self, forKey: .gt))
        } else if container.contains(.gte) {
            self = .gte(try! container.decode(Int.self, forKey: .gte))
        } else if container.contains(.lt) {
            self = .lt(try! container.decode(Int.self, forKey: .lt))
        } else if container.contains(.lte) {
            self = .lte(try! container.decode(Int.self, forKey: .lte))
        } else if container.contains(.or) {
            self = .or(try! container.decode([IntQuery].self, forKey: .or))
        } else if container.contains(.and) {
            self = .and(try! container.decode([IntQuery].self, forKey: .and))
        } else {
            self = .eq(0)
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
        case .gt(let value):
            try! container.encode(value, forKey: .gt)
        case .gte(let value):
            try! container.encode(value, forKey: .gte)
        case .lt(let value):
            try! container.encode(value, forKey: .lt)
        case .lte(let value):
            try! container.encode(value, forKey: .lte)
        case .or(let value):
            try! container.encode(value, forKey: .or)
        case .and(let value):
            try! container.encode(value, forKey: .and)
        }
    }
}
    """.strip() + "\n"
