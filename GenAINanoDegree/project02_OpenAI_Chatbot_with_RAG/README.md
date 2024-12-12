# AI History Chatbot with RAG

A conversational AI chatbot that uses Retrieval Augmented Generation (RAG) to answer questions about the history of artificial intelligence, using Wikipedia as its knowledge source.

## Dataset and Use Case

This chatbot specializes in the history of artificial intelligence by leveraging Wikipedia's comprehensive article on the subject. This specialization is particularly valuable for students, researchers, and technology enthusiasts who want to understand AI's historical development, key milestones, and influential figures. The RAG implementation ensures that responses include the most current information about AI history, including recent developments and awards that traditional language models might not cover. By focusing on a specific, well-documented topic, the chatbot can provide more accurate and detailed responses than a general-purpose AI system.

## Features

- Uses FAISS for efficient similarity search and vector storage
- Powered by OpenAI's GPT-3.5-turbo for natural language generation
- Wikipedia-based knowledge source focused on AI history
- Interactive command-line interface
- Advanced rate limit handling with exponential backoff
- Batch processing for embeddings
- Comprehensive error handling and recovery

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone the repository
2. Create and activate a conda environment:
   ```bash
   conda create -n ai-history-chatbot python=3.9
   conda activate ai-history-chatbot
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Run the chatbot:
```bash
python chatbot.py
```

Type your questions about AI history and press Enter. Type 'quit' to exit the program.

## Technical Details

- **Vector Store**: FAISS (Facebook AI Similarity Search) for efficient similarity search
- **Embeddings**: OpenAI's text embedding model with batch processing
  * Batch size: 5 chunks per request
  * Automatic retry with exponential backoff
  * Progress tracking for embedding creation
- **Text Splitting**: 
  * RecursiveCharacterTextSplitter
  * Chunk size: 1000 tokens
  * Chunk overlap: 100 tokens
- **Question Answering**: 
  * ConversationalRetrievalChain for context-aware responses
  * Retrieves 3 most relevant documents per query
  * 60-second timeout with 5 retries

## Error Handling

- Exponential backoff retry mechanism
  * Maximum 10 retries
  * Initial 10-second delay
  * Doubles delay for rate limit errors
- Batch processing to prevent rate limits
- Detailed error reporting and progress updates
- Graceful error recovery and continuation

## Recent Event Questions

Here are questions about events that occurred after GPT-3.5-turbo's training cutoff date (post-2021), which can only be accurately answered using our RAG system:

1. "Who won the 2024 Nobel Prizes for their contributions to artificial intelligence, and what specific achievements were recognized?"

2. "who were the recipients of the '2024 Nobel Prizes'"

3. "Who awarded the Nobel Prizes in AI in 2024?"

These questions demonstrate how RAG keeps the model's knowledge current by incorporating recent information from the Wikipedia article.

## Dependencies

- **openai**: Core API interface for GPT-3.5-turbo model and embeddings generation
- **langchain**: Framework for building RAG applications and chaining AI components
- **langchain-openai**: OpenAI-specific components for LangChain (embeddings and chat models)
- **langchain-community**: Community-maintained components including FAISS integration
- **faiss-cpu**: Facebook AI Similarity Search for efficient vector storage and retrieval
- **python-dotenv**: Environment variable management for secure API key storage
- **wikipedia**: Python library for fetching and parsing Wikipedia articles
- **tiktoken**: OpenAI's tokenizer for text splitting and token counting
- **beautifulsoup4**: HTML parsing for cleaning Wikipedia content

## Attribution

- [How_to_handle_rate_limits.ipynb](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb)
- [retrying-and-exponential-backoff-smart-strategies-for-robust-software](https://www.pullrequest.com/blog/retrying-and-exponential-backoff-smart-strategies-for-robust-software/)
- [exponential-backoff-decorator-in-python](https://medium.com/@suryasekhar/exponential-backoff-decorator-in-python-26ddf783aea0)
