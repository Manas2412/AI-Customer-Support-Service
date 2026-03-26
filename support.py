from langchain_core.documents import Document
from langchain_classic.chains import LLMChain
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional

class EmailProperties(BaseModel):
    category: str = Field(description="The type of email this is.", enum=["complaint", "refund_request", "product_feedback", "customer_service", "other"])
    mentioned_product: str = Field(description="The product mentioned in this email.")
    issue_description: str = Field(description="A brief explanation of the problem encountered with the product")
    name: Optional[str] = Field(description="Name of the person who wrote this email", default="Dear customer")

class AICustomerSupprt:
    def __init__(self, ollama_model="llama3.1"):
        self.llm = ChatOllama(model=ollama_model)

    def interpret_and_evaluate(self, extracted_properties):
        name = extracted_properties.get('name') or 'Dear customer'
        template = f"""
        You are an AI Customer Support that writes friendly emails back to customers. Address the user with his or her name {name}.
        The customer's email was categorized as {extracted_properties.get('category')}, and mentioned the product {extracted_properties.get('mentioned_product')}. 
        They described an issue: {extracted_properties.get('issue_description')}. 
        Please reply to this email in a friendly and helpful manner.

        Write a response that includes an understanding of the problem, a proposed solution, and a polite sign-off.
        Your sign-off name in the email is Manas Sisodia
        """
        
        prompt_template = PromptTemplate.from_template(template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        result = chain.predict(input="")
        return result

    def get_email_content(self, email_message):
        if not email_message.is_multipart():
            return email_message.get_payload()
        
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload()
        return ""

    async def process_email(self, email_message):
        email_content = self.get_email_content(email_message)
        
        # Use modern structured output instead of doctran
        structured_llm = self.llm.with_structured_output(EmailProperties)
        extracted_data = await structured_llm.ainvoke(email_content)
        
        extracted_properties = extracted_data.dict()
        evaluation_result = self.interpret_and_evaluate(extracted_properties)

        return extracted_properties, evaluation_result