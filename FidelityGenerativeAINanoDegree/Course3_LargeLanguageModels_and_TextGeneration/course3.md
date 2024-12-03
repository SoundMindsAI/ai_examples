Decoding Parameters
Rather than the single next token, an LLM’s output is actually a probability distribution across tokens. In order to choose the single next token to generate, a decoding mechanism must be specified. Many LLM inference APIs expose the same decoding parameters:

temperature
top_p or top_k
*_penalty (often repetition_ penalty, or frequency_penalty and presence_penalty)

Hugging Face has a wonderful blog(opens in a new tab) further explaining these decoding parameters. Also, see documentation details for OpenAI's API(opens in a new tab) and Together AI's API(opens in a new tab).
    - https://huggingface.co/blog/how-to-generate
    
Sampling vs Greedy Decoding
Many of the decoding parameters serve to augment the LLM's next token probability distribution. For example, increasing the temperature flattens the probability distribution, making it far more likely to sample a token that is not at the very top of the distribution and resulting in more "creative" LLM responses.

However, to ensure a more reproducible and deterministic response, you likely want to set temperature=0 and possibly top_p=1 (depending on the inference implementation) to request greedy decoding.