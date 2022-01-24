def session_manager() -> str:
    return """
public struct SessionManager {

    public static var shared = SessionManager()

    @UserDefault(key: "session") public fileprivate(set) var session: Session?

    private init() { }
}
    """.strip() + '\n'
