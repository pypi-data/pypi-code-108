def string_query():
    return """
public enum StringQuery: Codable {
    case eq(_ value: String)
    case neq(_ value: String)
    case null(_ value: Bool)
    case gt(_ value: String)
    case gte(_ value: String)
    case lt(_ value: String)
    case lte(_ value: String)
    case contains(_ value: String, mode: Mode = .default)
    case prefix(_ value: String, mode: Mode = .default)
    case suffix(_ value: String, mode: Mode = .default)
    case match(_ value: String, mode: Mode = .default)
    case or(_ values: [StringQuery])
    case and(_ values: [StringQuery])

    public enum Mode: String, Codable {
        case `default` = "default"
        case caseInsensitive = "insensitive"
    }

    public enum CodingKeys: String, CodingKey {
        case eq = "_eq"
        case neq = "_neq"
        case null = "_null"
        case gt = "_gt"
        case gte = "_gte"
        case lt = "_lt"
        case lte = "_lte"
        case contains = "_contains"
        case prefix = "_prefix"
        case suffix = "_suffix"
        case match = "_match"
        case mode = "_mode"
        case or = "_or"
        case and = "_and"
    }

    public init(from decoder: Decoder) throws {
        let container = try! decoder.container(keyedBy: CodingKeys.self)
        if container.contains(.eq) {
            self = .eq(try! container.decode(String.self, forKey: .eq))
        } else if container.contains(.neq) {
            self = .neq(try! container.decode(String.self, forKey: .neq))
        }else if container.contains(.null) {
            self = .null(try! container.decode(Bool.self, forKey: .null))
        }  else if container.contains(.gt) {
            self = .gt(try! container.decode(String.self, forKey: .gt))
        } else if container.contains(.gte) {
            self = .gte(try! container.decode(String.self, forKey: .gte))
        } else if container.contains(.lt) {
            self = .lt(try! container.decode(String.self, forKey: .lt))
        } else if container.contains(.lte) {
            self = .lte(try! container.decode(String.self, forKey: .lte))
        } else if container.contains(.contains) {
            self = .contains(
                try! container.decode(String.self, forKey: .contains),
                mode: (try? container.decode(Mode.self, forKey: .mode)) ?? .default
            )
        } else if container.contains(.prefix) {
            self = .prefix(
                try! container.decode(String.self, forKey: .prefix),
                mode: (try? container.decode(Mode.self, forKey: .mode)) ?? .default
            )
        } else if container.contains(.suffix) {
            self = .suffix(
                try! container.decode(String.self, forKey: .suffix),
                mode: (try? container.decode(Mode.self, forKey: .mode)) ?? .default
            )
        } else if container.contains(.match) {
            self = .match(
                try! container.decode(String.self, forKey: .match),
                mode: (try? container.decode(Mode.self, forKey: .mode)) ?? .default
            )
        } else if container.contains(.or) {
            self = .or(try! container.decode([StringQuery].self, forKey: .or))
        } else if container.contains(.and) {
            self = .and(try! container.decode([StringQuery].self, forKey: .and))
        } else {
            self = .eq("")
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
        case .contains(let value, let mode):
            try! container.encode(value, forKey: .contains)
            if mode != .default {
                try! container.encode(mode, forKey: .mode)
            }
        case .prefix(let value, let mode):
            try! container.encode(value, forKey: .prefix)
            if mode != .default {
                try! container.encode(mode, forKey: .mode)
            }
        case .suffix(let value, let mode):
            try! container.encode(value, forKey: .suffix)
            if mode != .default {
                try! container.encode(mode, forKey: .mode)
            }
        case .match(let value, let mode):
            try! container.encode(value, forKey: .match)
            if mode != .default {
                try! container.encode(mode, forKey: .mode)
            }
        case .or(let value):
            try! container.encode(value, forKey: .or)
        case .and(let value):
            try! container.encode(value, forKey: .and)
        }
    }
}
    """.strip() + "\n"
