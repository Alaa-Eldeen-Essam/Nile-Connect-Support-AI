from __future__ import annotations

import datetime
import secrets
from typing import Callable

from app.config import AppConfig
from app.models.schemas import Ticket, UserProfile
from app.repositories.mongo import MongoGateway
from app.repositories.profiles import ProfileRepository
from app.services.rag_service import RagService

SYSTEM_PROMPT = """You are Nile Connect Support AI, an independent customer-support portfolio
demonstration. You are not affiliated with, endorsed by, or operated by Telecom Egypt, WE, or
another telecom provider. You must be professional and concise, and never claim to be an official
company representative.

Protocol:
1. Before answering technical or billing questions, collect name, 11-digit Egyptian phone number,
   age, and city. Ask only for the fields that are missing.
2. Once all fields are provided, immediately call save_user_profile. Do not provide technical or
   billing help until it succeeds.
3. Use search_we_knowledge_base for public telecom source material, router configuration,
   troubleshooting, and billing. Do not invent policies or claim provider affiliation.
4. For complaints needing human follow-up, call submit_support_ticket. Return its friendly
   confirmation exactly: never expose database IDs or call the request a ticket number.
"""


class AgentService:
    def __init__(
        self,
        get_config: Callable[[], AppConfig],
        get_profile_repository: Callable[[], ProfileRepository],
        mongo: MongoGateway,
    ) -> None:
        self.get_config = get_config
        self.get_profile_repository = get_profile_repository
        self.mongo = mongo
        self._agent = None

    def reload(self) -> None:
        self._agent = None

    def reply(self, message: str, session_id: str) -> str:
        if self._agent is None:
            self._agent = self._build_agent()
        response = self._agent.invoke(
            {"input": message}, config={"configurable": {"session_id": session_id}}
        )
        for action, observation in response.get("intermediate_steps", []):
            if action.tool == "submit_support_ticket" and str(observation).startswith(
                "### Support request received"
            ):
                return str(observation)
        output = response["output"]
        if isinstance(output, list):
            return "".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in output
            )
        return str(output)

    def _build_agent(self):
        config = self.get_config()
        if not config.google_api_key:
            raise RuntimeError("The administrator has not configured GOOGLE_API_KEY yet.")

        from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_mongodb import MongoDBChatMessageHistory

        rag = RagService(config)
        rag.ensure_index()
        profile_repository = self.get_profile_repository()
        tickets = self.mongo.database["tickets"]

        from langchain.tools import tool

        @tool("search_we_knowledge_base")
        def search_we_knowledge_base(query: str) -> str:
            """Search public telecom source material for support, router, billing, and plans."""
            documents = rag.vector_store().similarity_search(query, k=3)
            if not documents:
                return "No relevant source material was found."
            return "\n\n".join(document.page_content for document in documents)

        @tool("save_user_profile", args_schema=UserProfile)
        def save_user_profile(name: str, phone: str, age: int, city: str) -> str:
            """Save the customer profile before providing technical or billing help."""
            try:
                profile_repository.save(UserProfile(name=name, phone=phone, age=age, city=city))
                return (
                    f"Successfully saved user profile for {name}. You may now proceed to help them."
                )
            except Exception:  # Tool failures need a user-safe message for the agent.
                return "Database error: the profile could not be saved. Ask the user to try again."

        @tool("submit_support_ticket", args_schema=Ticket)
        def submit_support_ticket(phone: str, issue_type: str, description: str) -> str:
            """Save a detailed customer support ticket after a known profile is available."""
            if not profile_repository.exists(phone):
                return "Error: save and validate the customer's profile before submitting a ticket."
            created_at = datetime.datetime.now(datetime.UTC)
            ticket = {
                "reference": f"NC-{created_at:%Y%m%d}-{secrets.token_hex(3).upper()}",
                "phone": phone,
                "issue_type": issue_type,
                "description": description,
                "status": "Open",
                "created_at": created_at,
            }
            tickets.insert_one(ticket)
            return (
                "### Support request received\n\n"
                f"Your reference is **{ticket['reference']}**. Our demo support team will respond "
                "within **2-3 working days**.\n\n"
                "Keep this reference for follow-up. For this demonstration, contact "
                "**support@nileconnect.example** or the demo hotline +20 000 000 0000**."
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        executor = AgentExecutor(
            agent=create_tool_calling_agent(
                ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2),
                [search_we_knowledge_base, save_user_profile, submit_support_ticket],
                prompt,
            ),
            tools=[search_we_knowledge_base, save_user_profile, submit_support_ticket],
            verbose=not config.is_production,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        def history(session_id: str):
            return MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=config.mongo_uri,
                database_name=config.mongo_db,
                collection_name="chat_history",
            )

        return RunnableWithMessageHistory(
            executor,
            history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
