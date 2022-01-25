def user_default() -> str:
    return """
@propertyWrapper
public struct UserDefault<T: Codable> {

    private var key: String

    public var wrappedValue: T? {
        didSet {
            if let wrappedValue = wrappedValue {
                let data = try! JSONEncoder().encode(wrappedValue)
                let string = String(data: data, encoding: .utf8)
                UserDefaults.standard.setValue(string, forKey: key)
            } else {
                UserDefaults.standard.removeObject(forKey: key)
            }
        }
    }

    fileprivate init(key: String) {
        self.key = key
        if let string = UserDefaults.standard.value(forKey: key) as? String {
            let data = string.data(using: .utf8)!
            self.wrappedValue = try! JSONDecoder().decode(T.self, from: data)
        } else {
            self.wrappedValue = nil
        }
    }
}
    """.strip() + '\n'
