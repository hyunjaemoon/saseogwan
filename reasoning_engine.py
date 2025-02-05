from typing import Dict, List, Union

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
import vertexai
from vertexai.preview import reasoning_engines

from utils import SaSeoGwanConfigs

PROJECT_ID = SaSeoGwanConfigs.project_id
STAGING_BUCKET = SaSeoGwanConfigs.staging_bucket
GEMINI_MODEL = SaSeoGwanConfigs.gemini_model
LOCATION = SaSeoGwanConfigs.location

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)


class SaSeoGwanParams:
    company_name: str
    description: str
    industry: str
    website: str
    contact_email: str

    def __init__(
        self,
        company_name: str,
        description: str,
        industry: str,
        website: str,
        contact_email: str,
    ):
        self.company_name = company_name
        self.description = description
        self.industry = industry
        self.website = website
        self.contact_email = contact_email


class SaSeoGwanLangGraphApp:
    def __init__(
        self, project: str, location: str, company_params: SaSeoGwanParams
    ) -> None:
        self.project_id = project
        self.location = location
        self.company_params = company_params

    def set_up(self) -> None:
        system = (
            "You are a helpful assistant that answers questions "
            f"about {self.company_params.company_name}, with description, '{self.company_params.description}', "
            f"with industry, '{self.company_params.industry}', with website, '{self.company_params.website}', "
            f"with contact email, '{self.company_params.contact_email}'."
        )
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages(
            [("system", system), ("human", human)]
        )
        chat = ChatVertexAI(
            model=GEMINI_MODEL, project=self.project_id, location=self.location
        )
        self.chain = prompt | chat

    def query(self, question: str) -> Union[str, List[Union[str, Dict]]]:
        """Query the application.
        Args:
            question: The user prompt.
        Returns:
            str: The LLM response.
        """
        return self.chain.invoke({"text": question}).content


def query_local_reasoning_engine(query: str):
    # Locally test
    params = SaSeoGwanParams(
        company_name="SaSeoGwan",
        description="SaSeoGwan is a company that provides AI-powered business framework.",
        industry="Software",
        website="https://saseogwan.com",
        contact_email="calhyunjaemoon@gmail.com",
    )
    app = SaSeoGwanLangGraphApp(
        project=PROJECT_ID, location=LOCATION, company_params=params
    )
    app.set_up()
    return app.query(query)


def deploy_reasoning_engine():
    # Create a remote app with reasoning engine
    # This may take 1-2 minutes to finish because it builds a container and turn up HTTP servers.
    reasoning_engine = reasoning_engines.ReasoningEngine.create(
        SaSeoGwanLangGraphApp(project=PROJECT_ID, location=LOCATION),
        requirements=[
            "google-cloud-aiplatform",
            "langchain-google-vertexai",
            "langchain-core",
            "cloudpickle",
        ],
        display_name="Demo LangChain App",
        description="This is a simple LangChain app.",
        sys_version="3.11",
        extra_packages=[],
    )
    return reasoning_engine


if __name__ == "__main__":
    # deploy_reasoning_engine()
    print(query_local_reasoning_engine("Tell me about SaSeoGwan."))
