def date_query():
    return """
public enum DateQuery: Codable {
    case eq(_ value: Date)
    case neq(_ value: Date)
    case null(_ value: Bool)
    case gt(_ value: Date)
    case gte(_ value: Date)
    case lt(_ value: Date)
    case lte(_ value: Date)
    case after(_ value: Date)
    case before(_ value: Date)
    case or(_ values: [DateQuery])
    case and(_ values: [DateQuery])

    public enum CodingKeys: String, CodingKey {
        case eq = "_eq"
        case neq = "_neq"
        case null = "_null"
        case gt = "_gt"
        case gte = "_gte"
        case lt = "_lt"
        case lte = "_lte"
        case after = "_after"
        case before = "_before"
        case or = "_or"
        case and = "_and"
    }

    public init(from decoder: Decoder) throws {
        let container = try! decoder.container(keyedBy: CodingKeys.self)
        if container.contains(.eq) {
            self = .eq(try! container.decode(Date.self, forKey: .eq))
        } else if container.contains(.neq) {
            self = .neq(try! container.decode(Date.self, forKey: .neq))
        } else if container.contains(.null) {
            self = .null(try! container.decode(Bool.self, forKey: .null))
        } else if container.contains(.gt) {
            self = .gt(try! container.decode(Date.self, forKey: .gt))
        } else if container.contains(.gte) {
            self = .gte(try! container.decode(Date.self, forKey: .gte))
        } else if container.contains(.lt) {
            self = .lt(try! container.decode(Date.self, forKey: .lt))
        } else if container.contains(.lte) {
            self = .lte(try! container.decode(Date.self, forKey: .lte))
        } else if container.contains(.after) {
            self = .after(try! container.decode(Date.self, forKey: .after))
        } else if container.contains(.before) {
            self = .before(try! container.decode(Date.self, forKey: .before))
        } else if container.contains(.or) {
            self = .or(try! container.decode([DateQuery].self, forKey: .or))
        } else if container.contains(.and) {
            self = .and(try! container.decode([DateQuery].self, forKey: .and))
        } else {
            self = .eq(Date())
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
            case .after(let value):
                try! container.encode(value, forKey: .after)
            case .before(let value):
                try! container.encode(value, forKey: .before)
            case .or(let value):
                try! container.encode(value, forKey: .or)
            case .and(let value):
                try! container.encode(value, forKey: .and)
            }
        }
}
    """.strip() + "\n"
