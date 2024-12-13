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
   conda create -n ai-chatbot python=3.9
   conda activate ai-chatbot
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
- **Data Processing**:
  * Pandas DataFrame for structured data management
  * Efficient text chunk organization and processing
- **Embeddings**: OpenAI's text embedding model with batch processing
  * Batch size: 5 chunks per request
  * Automatic retry with exponential backoff
  * Progress tracking for embedding creation
- **Text Splitting**: 
  * RecursiveCharacterTextSplitter
  * Chunk size: 1000 tokens
  * Chunk overlap: 200 tokens
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

   **Base Model Response:**
   ```
   I'm sorry, but I cannot provide real-time or future information as I do not have access to the internet to look up current events. However, as of my last update, I can tell you that the Nobel Prizes do not have a specific category for artificial intelligence. The closest related category would be the Nobel Prize in Economic Sciences, which has not been awarded specifically for contributions to AI as of my last update. I recommend checking the official Nobel Prize website or other reliable sources for the most up-to-date information on Nobel Prize winners.
   ```

   **RAG-Enhanced Response:**
   ```
   In 2024, the Nobel Prizes in recognition of groundbreaking contributions to artificial intelligence were awarded to the following individuals:

   1. In physics: John Hopfield for his work on physics-inspired Hopfield networks, and Geoffrey Hinton for foundational contributions to Boltzmann machines and deep learning.
   2. In chemistry: David Baker, Demis Hassabis, and John Jumper for their advancements in protein folding predictions, particularly with AlphaFold.
   ```

2. "Who were the recipients of the '2024 Nobel Prizes'?"

   **Base Model Response:**
   ```
   I'm sorry, but as of now, I do not have real-time information on the recipients of the 2024 Nobel Prizes. I recommend checking the official Nobel Prize website or reputable news sources for the most up-to-date information on the winners.
   ```

   **RAG-Enhanced Response:**
   ```
   In 2024, the recipients of the Nobel Prizes for their contributions to artificial intelligence were:

   1. Physics: John Hopfield for his work on physics-inspired Hopfield networks, and Geoffrey Hinton for foundational contributions to Boltzmann machines and deep learning.
   
   2. Chemistry: David Baker, Demis Hassabis, and John Jumper for their advancements in protein folding predictions, particularly with AlphaFold.

   These individuals were recognized for their groundbreaking work in their respective fields related to artificial intelligence.
   ```

These examples demonstrate how RAG enables the chatbot to provide specific, up-to-date information about recent events that occurred after the base model's training cutoff date.

## Dependencies

- **openai**: Core API interface for GPT-3.5-turbo model and embeddings generation
- **langchain**: Framework for building RAG applications and chaining AI components
- **langchain-openai**: OpenAI-specific components for LangChain (embeddings and chat models)
- **langchain-community**: Community-maintained components including FAISS integration
- **faiss-cpu**: Facebook AI Similarity Search for efficient vector storage and retrieval
- **numpy**: Numerical computations (version <2, >=1.26.4 for compatibility)
- **pandas**: Data manipulation and analysis for structured text processing
- **python-dotenv**: Environment variable management for secure API key storage
- **wikipedia**: Python library for fetching and parsing Wikipedia articles
- **tiktoken**: OpenAI's tokenizer for text splitting and token counting
- **beautifulsoup4**: HTML parsing for cleaning Wikipedia content

## Attribution

- [How_to_handle_rate_limits.ipynb](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb)
- [retrying-and-exponential-backoff-smart-strategies-for-robust-software](https://www.pullrequest.com/blog/retrying-and-exponential-backoff-smart-strategies-for-robust-software/)
- [exponential-backoff-decorator-in-python](https://medium.com/@suryasekhar/exponential-backoff-decorator-in-python-26ddf783aea0)
