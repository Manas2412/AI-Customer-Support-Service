from extraction import EmailFetcher
from support import AICustomerSupprt
from dotenv import load_dotenv
import asyncio

async def fetch_and_process_emails(fetcher, ai_support):
    while True:
        print("Checking for the new email...")
        new_emails = await fetcher.fetch_new_emails()
        for email_message, sender_name, sender_addr in new_emails:
            extracted_properties, evaluation_result = await ai_support.process_email(
                email_message
            )
            print(f"Email from : {sender_name} ({sender_addr})")

            subject = "AI Customer Service reply"
            fetcher.send_email(sender_addr, subject, evaluation_result)

        print("Sleeping for 10 seconds...")
        await asyncio.sleep(10)



async def main():
    load_dotenv()
    fetcher = EmailFetcher()
    ai_support = AICustomerSupprt(ollama_model = "llama3.1")
    await fetch_and_process_emails(fetcher, ai_support)



if __name__ == "__main__":
    asyncio.run(main())