FUNCTION_TEMPLATE = """func <FUNC_NAME><GENERIC_PARAMETER_CLAUSE>(<FUNC_PARAMS>) <RETURN_TYPE>{
        switch MockManager.getOption(self, #function) {
        <CASES>
        default: break
        }
        <RETURN>originalInstance.<ORIGINAL_FUNC_CALL>
    }"""

TEMPLATE = """
// MARK: - Mock implementation init

class Mock<PROTOCOL>Impl: <PROTOCOL> {

    private let originalInstance: <PROTOCOL>

    init(originalInstance: <PROTOCOL>) {
        self.originalInstance = originalInstance
    }
}

extension Mock<PROTOCOL>Impl {

    <FUNCTIONS>
}

import Swinject
func registerMock<PROTOCOL>(to container: Container) {
    // swiftlint:disable force_unwrapping
<ORIGINAL_REGISTRATION>
    container.register(<PROTOCOL>.self) { r in
        Mock<PROTOCOL>Impl(
            originalInstance: r.resolve(<PROTOCOL>Impl.self)!
        )
    }
}
"""

SHAKABLE_NC = """
// MARK: - Debug mode helper classes
// WARNING: DO NOT ADD ANY PRODUCTION CODE BELLOW THIS LINE
class ShakableNavigationController: UINavigationController {

    override func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?) {
        if motion == .motionShake {
            present(MockManager(), animated: true, completion: nil)
        }
    }
}
"""

SHAKABLE_NC_INSTANCE = (
    "ShakableNavigationController() // !!! Don't edit this line while in debug mode !!!"
)

MOCK_MANAGER_TEMPLATE = """
// swiftlint:disable duplicate_imports
import Stevia

class MockManager: UITableViewController {

    static var cursor = [
        <MOCK_CURSORS>
    ]

    static var settings = [
        <MOCK_SETTINGS>
    ]

    var hiddenSections = Set<Int>()

    init() {
        super.init(nibName: nil, bundle: nil)
        hiddenSections = Set(0..<Self.settings.keys.count)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// MARK: - Boilerplate
// swiftlint:disable type_contents_order
extension MockManager {

    override func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        let keys = Array(Self.settings.keys)
        return keys[section]
    }

    override func numberOfSections(in tableView: UITableView) -> Int {
        Self.settings.keys.count
    }

    // swiftlint:disable force_unwrapping
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        if self.hiddenSections.contains(section) {
            return 0
        }

        let keys = Array(Self.settings.keys)
        return Self.settings[keys[section]]?.keys.count ?? 0
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = UITableViewCell()
        let currentKeySubkeyPair = getCurrentKeyAndSubKey(for: indexPath)
        let currentCursor = getCurrentCursor(for: indexPath)
        let functionVariant = Self.settings[currentKeySubkeyPair.key]![currentKeySubkeyPair.subKey]!
        cell.textLabel?.text = currentKeySubkeyPair.subKey + " - " + functionVariant[currentCursor]
        cell.textLabel?.numberOfLines = 0
        cell.textLabel?.lineBreakMode = .byWordWrapping
        return cell
    }

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let currentKeySubkeyPair = getCurrentKeyAndSubKey(for: indexPath)
        let options = Self.settings[currentKeySubkeyPair.key]![currentKeySubkeyPair.subKey]!
        present(
            SelectVariantViewController(
                header: Array(Self.settings[currentKeySubkeyPair.key]!.keys)[indexPath.row],
                options: options,
                onResult: { index in
                    Self.cursor[currentKeySubkeyPair.key]![currentKeySubkeyPair.subKey] = index
                    tableView.reloadData()
                }),
            animated: true,
            completion: nil
        )
    }

    func getCurrentCursor(for indexPath: IndexPath) -> Int {
        let keyAndSubkey = getCurrentKeyAndSubKey(for: indexPath)
        return Self.cursor[keyAndSubkey.key]![keyAndSubkey.subKey]!
    }

    func getCurrentKeyAndSubKey(for indexPath: IndexPath) -> (key: String, subKey: String) {
        let keys = Array(Self.settings.keys)
        let currentKey = keys[indexPath.section]
        return (key: currentKey, subKey: Array(Self.settings[currentKey]!.keys)[indexPath.row])
    }

    static func getOption(_ target: Any, _ functionName: String) -> String {
        let className = Mirror(reflecting: target).description.split(separator: " ").last!
        let cursor = MockManager.cursor[String(className)]![functionName]!
        let options = MockManager.settings[String(className)]![functionName]!
        return options[cursor]
    }

    override func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        let title = Array(Self.settings.keys)[section]
            .replacingOccurrences(of: "Mock", with: "")
            .replacingOccurrences(of: "Impl", with: "")
        let view = UIView()

        let btnSection = UIButton()
        btnSection.contentEdgeInsets = UIEdgeInsets(top: 20, left: 15, bottom: 20, right: 15)
        btnSection.setTitle(title,
                            for: .normal)
        btnSection.sizeToFit()
        btnSection.titleLabel?.numberOfLines = 0
        btnSection.tag = section
        btnSection.addTarget(self,
                             action: #selector(self.hideSection(sender:)),
                             for: .touchUpInside)
        btnSection.backgroundColor = UIColor.black.withAlphaComponent(0.1)
        btnSection.setTitleColor(.black, for: .normal)

        let viewSeparator = UIView()
        viewSeparator.backgroundColor = .black
        viewSeparator.height(1)

        view.subviews(btnSection, viewSeparator)
        view.layout(0,
                    |btnSection|,
                    0,
                    viewSeparator,
                    0)

        return view
    }

    @objc
    private func hideSection(sender: UIButton) {
        let section = sender.tag

        func indexPathsForSection() -> [IndexPath] {
            let keys = Array(Self.settings.keys)
            let optionsCount = Self.settings[keys[section]]!.count

            var indexPaths = [IndexPath]()

            for row in 0..<optionsCount {
                indexPaths.append(IndexPath(row: row,
                                            section: section))
            }

            return indexPaths
        }

        if self.hiddenSections.contains(section) {
            self.hiddenSections.remove(section)
            self.tableView.insertRows(at: indexPathsForSection(),
                                      with: .fade)
        } else {
            self.hiddenSections.insert(section)
            self.tableView.deleteRows(at: indexPathsForSection(),
                                      with: .fade)
        }
    }
}

class SelectVariantViewController: UITableViewController {

    private let header: String
    private let options: [String]
    private let onResult: (Int) -> Void

    init(header: String, options: [String], onResult: @escaping (Int) -> Void) {
        self.header = header
        self.options = options
        self.onResult = onResult
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func numberOfSections(in tableView: UITableView) -> Int {
        1
    }

    override func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        header
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return options.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = UITableViewCell()
        cell.textLabel?.text = options[indexPath.row]
        return cell
    }

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        onResult(indexPath.row)
        dismiss(animated: true, completion: nil)
    }
}
"""

MOCK_MANAGER_SETTINGS_TEMPLATE = """"<PROTOCOL>": [
    <FUNCTION_SETTINGS>
        ]"""

FUNCTION_SETTINGS_TEMPLATE = """        "<FUNCTION_ANNOTATION>": <SETTINGS_VALUES>"""
