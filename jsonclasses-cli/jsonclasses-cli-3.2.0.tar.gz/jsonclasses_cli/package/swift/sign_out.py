def sign_out() -> str:
    return """
public func signOut() {
    SessionManager.shared.session = nil
}
    """.strip() + '\n'
