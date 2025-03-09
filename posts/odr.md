---
title: Using OpenAI's Deep Research to save Time and Money
categories: [chatgpt, llms]
summary: An overview and guide on how to use OpenAI's Deep Research (ODR)
date: 2025-03-09
draft: False
---

# Using OpenAI's Deep Research to save Time and Money
[OpenAI's Deep Research](https://openai.com/index/introducing-deep-research/) (ODR), which was released a bit over a month ago, has become a valuable tool for me.
Initially, I wanted to compare it against the countless competitors, but none of them[^1] come close to the quality of OpenAI's offering; most of them are either shallow listicle-fests or contain countless mistakes.

## The versatility of ODR

My most common use case is to use it as a research assistant to get into a new topic quickly.
This is the most obvious and most advertised use case for Deep Research, which will [only increase in quality and usage over time](https://www.interconnects.ai/p/deep-research-information-vs-insight-in-science).

At least right now, the outputs cannot replace a full literature review, but they are good enough to get a good intro into a new topic, spanning around 3–6 papers usually, which saves around a day of finding and reading relevant papers.
Aside from the summaries of those papers, ODR can also compare the approaches and findings and transfer them onto other domains.

Apart from that, ODR is also good for finding fixes for obscure bugs and niche libraries when tasked to scout GitHub issues and obscure StackOverflow posts for the solution. The underlying model behind ODR is trained to generate reports, so it will not fix the code for you, but instead give you a detailed rundown of the possible solutions.

A totally different use case, which I've not seen mentioned elsewhere, is using it as a shopping assistant for extremely niche products. As an example, I needed a heavy-duty rack which very specific and non-standard measurements to fit in a recess of my apartment. I have to admit, I was unable to find anything myself with some hours of searching, whereas ODR was able to find the single option satisfying the given constraints.

ODR is also capable of finding the cheapest option for a given product, which not even Idealo, the biggest price comparison website in Germany, could do. It is also capable of finding valid replacement parts for a given product when supplied with the product's name, something I expected competitors (like Perplexity) to accomplish, but they could not.

## Getting the most out of ODR

That said, ODR is not perfect and not as straightforward to use as other, LLM-based tools, despite the seeming simplicity of clicking the "Deep Research" button in ChatGPT and then typing in your prompt and answering the follow-up questions. One thing which isn't obvious: The model chosen when clicking the button doesn't matter, Deep Research will always use o3 behind the scenes, even when the selected model is 4o-mini.

The most important aspect of using ODR is that **prompting matters (again)**. Whereas other products and LLMs these days are good enough for the majority of prompts, the difference in the outputs of ODR is night and day depending on the prompt.

Good prompts are highly specific and detailed, describing the goal, possible constraints and the desired output format. A viable approach is to use LLMs to generate a prompt for ODR, I've been using [this prompt template](https://www.florianbrand.de/posts/odr-prompt) from [this tweet](https://x.com/buccocapital/status/1890745551995424987) with o1-pro to generate a prompt for ODR. In my tests, using this template compared to prompting directly resulted in >40% longer reports, which go into more detail and are more structured.

Good prompts also specify the (sub)set of websites to use for the research. The default set of websites ODR chooses is a bit better than the usual, SEO-sloptimized first page of Google results, but this is far from perfect. 

As examples: Adding to the prompt that the research should only use ArXiv (and similar sites) leads to better results for literature reviews; asking it to only use primary sources from NVIDIA leads to a correct comparison of GPU specs; asking it to use only Chinese-language sites like Weixin gives you better insights into the Chinese community than any third-party English-language site could give. 

### Limitations

When using ODR for comparisons, e.g. to compare different papers or models, I found that the limit seems to be 2-3 comparisons max, i.e., comparing two models (like Qwen against GPT-4o) is fine, but adding more models to the comparison leads to numerous mistakes. I found this to be also true for other tasks: When you prompt it for too many things at once, the output will degrade quickly.

Aside from that, ODR has some technical limitations. It cannot access gated content, which will [become an increasing part of the internet in the near future](https://stratechery.com/2025/deep-research-and-knowledge-value/). It also cannot access YouTube nor the transcripts of YouTube videos. I also was unable to prompt it to use a transcription service to get the content of videos. It can, however, read PDFs, access images and execute Python code, although I haven't seen that for my queries yet. 

[^1]: And I've tried quite a few, including some open-source projects, [Gemini Deep Research](https://gemini.google/overview/deep-research/?hl=en), [Perplexity Deep Research](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research), [Grok Deep Search](https://x.ai/blog/grok-3), [You ARI](https://you.com/ari), even the recently released and hyped [Manus](https://manus.im/).