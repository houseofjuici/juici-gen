from praisonai.agent import Agent
from tools import get_tools

def main():
    juici = Agent.from_yaml("agents.yaml", agent_name="juici_general_assistant")
    juici.load_tools(get_tools())
    juici.run()

if __name__ == "__main__":
    main()