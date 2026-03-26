# AI Customer Support Service 🤖📧

An intelligent, automated email response system that uses **Ollama (Llama 3.1)** to categorize, extract information from, and reply to customer support emails.

## 🚀 Key Features

- **Automated Email Monitoring**: Periodically checks your Gmail inbox for new, unread messages.
- **AI-Powered Analysis**: Uses local LLMs (via Ollama) to categorize emails (refunds, complaints, etc.) and extract key details like product names and issues.
- **Personalized Replies**: Generates friendly, context-aware responses and sends them back to the customer.
- **Smart Whitelisting**: Processes only emails from authorized senders to prevent spam or unintentional replies.
- **High Efficiency**: Optimized to fetch only the newest emails and filter by headers first, saving bandwidth and compute time.

## 🛠️ Tech Stack

- **Python 3.11+**
- **Ollama** (Llama 3.1)
- **LangChain** (for LLM orchestration)
- **IMAPLib/SMTP** (for email handling)
- **uv** (for fast dependency management)

## 📋 Prerequisites

1.  **Ollama**: Install [Ollama](https://ollama.com/) and pull the model:
    ```bash
    ollama run llama3.1
    ```
2.  **Gmail Settings**: 
    - Enable **IMAP** in your Gmail settings.
    - Generate an **App-Specific Password** (if using 2FA).

## ⚙️ Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Manas2412/AI-Customer-Support-Service.git
    cd AI-Customer-Support-Service
    ```

2.  **Configure Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    EMAIL_USER=your-email@gmail.com
    EMAIL_PASSWORD=your-app-specific-password
    IMAP_HOST=imap.gmail.com
    SMTP_SERVER=smtp.gmail.com
    ```

3.  **Manage the Whitelist**:
    Edit `whitelist.yaml` to include addresses that the AI is allowed to reply to:
    ```yaml
    whitelist:
      - customer-email@example.com
      - colleague@work.com
    ```

## 🏃 Running the Service

Start the service using `uv`:
```bash
uv run python main.py
```

The service will check for new emails every 10 seconds. You will see detailed logs in your terminal about login status, unread counts, and which emails are being skipped or processed.

## 🧠 Optimization Notes

Unlike simple implementations that download every unread email, this service is designed for speed:
- **Header-Only Filtering**: It checks the sender's address via the `From` header *before* downloading the full email body.
- **Batch Processing**: It processes the 10 most recent unread emails in each loop, ensuring fast response times even for busy inboxes.
- **Newest First**: Always prioritizes the most recent incoming requests.


