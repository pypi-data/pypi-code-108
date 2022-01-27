from tcell_agent.rust.native_callers import NativeCaller
from tcell_agent.rust.models.agent_config import AgentConfig


def test_agent():
    caller = NativeCaller(native_method_name="test_agent",
                          bytes_to_allocate=1028 * 8)
    caller.append_parameter(AgentConfig({}))
    caller.execute()
