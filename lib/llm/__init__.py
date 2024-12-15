from langchain_ollama import ChatOllama
from langchain.schema import BaseMessage, HumanMessage

class LLMAgent:
    """
    LLM Agent interface
    """

    def __init__(self, model = "llama3.2"):
        """
        Initialize LLM Agent

        Parameters
        -----------
        model: str
            Model name 
        """
        self.model = ChatOllama(model=model)
        self.session: dict[str, list[BaseMessage]] = {}

    def _get_session(self, session_id: str) -> list[BaseMessage]:
        """
        Get session
        """
        return self.session.get(session_id, [])
    
    def delete_session(self, session_id: str):
        """
        Delete session

        Parameters
        -----------
        session_id: str
            Unique user session
        """
        if session_id in self.session:
            del self.session[session_id]

    def chat(self, session_id: str, prompt: str):
        """
        Chat interaction

        Parameters
        -----------
        session_id: str
            Unique user session
        prompt: str
            User prompt
        """
        session = self._get_session(session_id)
        session.append(HumanMessage(content=prompt))
        response = self.model.invoke(session)
        session.append(response)
        self.session[session_id] = session
        return response.content


if __name__ == "__main__":
    llm = LLMAgent()
    print(llm.chat("123", "Hello, how are you?"))
