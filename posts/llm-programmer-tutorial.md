---
title: A Guide to LLMs for Programmers
categories: [llms, prompting, applied ai]
summary: An overview of LLMs and prompting techniques for coders
date: 2024-11-04
draft: False
---

# A Guide to LLMs for Programmers

Although LLMs are all the rage these days, I found that a surprising amount of developers is still dismissing them and their potential. 
Part of this might be due to the limited amount of information aimed at developers, as most tutorials and guides are aimed at the NLP community or developers building LLM applications. This post provides an overview to the world of LLMs, the applications to access them and some prompting tips aimed at people who code. Most of these are based on my personal experiences from the past years of using them.

## A short technical Introduction to LLMs

While there are a lot of technical details differentiating LLMs, most of them are not that interesting from a users perspective or are intentionally withheld by the makers of the models to protect their IP. For programmers, two aspects are important: The **context window size** and the **knowledge cutoff** date.

The context window is the amount of tokens (words/parts of words) a model can process at a time, with one token representing roughly 3-4 characters. This is similar to the RAM of computers: Text which is bigger than the context window simply cannot be processed. To calculate the amount of tokens for a given text, [ttok](https://github.com/simonw/ttok) is a simple to use utility for all OpenAI models, but every model uses their own tokenizer, therefore the actual amount of tokens for the same text differs from model to model. However, modern tokenizers are rather similar to each other in terms of the amount of tokens they produce. As a rule of thumb you can use the tokenizer for `GPT-4o` from OpenAI (`o200k_base`) and use this number as an educated guess, the others are usually within 10-20% of that number.

Another aspect mostly overlooked in literature, but crucial for software development is the knowledge cutoff date. This marks the end date of the used training data and, as the name applies, the most recent data the model will have knowledge of. For software development this impacts the latest versions of libraries the model can have knowledge of. If you work with cutting-edge libraries with frequent or recent API changes, you will notice this limitation. As an example, I use [polars](https://pola.rs/) over pandas for dealing with all kinds of data, which just recently got its first stable release. Models with an old cutoff date, such as GPT-4o (October 2023 cutoff), are unable to generate valid polars code, and often use pandas syntax or outdated APIs, while models with a more recent cutoff date, such as Claude 3.5 Sonnet (April 2024 cutoff) can generate valid polars code.
Training data of LLMs can be understood as a snapshot of the internet at the time of the knowledge cutoff data. Therefore, LLMs mirror the usage of libraries and APIs, including their most-used versions/iterations at this time. As an example, they will be able to generate better `matplotlib` code than `plotly` code, as the former library is more popular. But it also means that they might generate code which is outdated, as the training data contains more old code than new code with the updated API usage. On the one hand, this reinforces the "winner takes all" aspect of libraries, as switching to an alternative library becomes harder. On the other hand, this means that LLMs can generate code for hard-to-use libraries such as `ffmpeg`, as it is so prevalent in the training data[^jq].

## Selecting the appropriate LLM for a Task

While the LLM space is as active as ever with promising LLMs releasing almost every week, the frontier has largely settled among the giants of OpenAI, Anthropic and Google. However, not all models are equal and every model has its own strength.
Currently, these patterns emerged in my daily usage:

- **Claude 3.5 Sonnet** for everyday tasks/coding. It has the most recent knowledge cutoff with April 2024 and a rather big context window of 200k tokens. It is an exceptional strong coding model and I use it for the vast majority of tasks.
- **o1(-preview)** for the planning of codebases / complex algorithms. As this model is vastly different from other models, I have a section dedicated to it later.
- **Mistral Large 2** for everything related to the (bash) shell and common commands. While other LLMs often come up with convoluted solutions for rather easy problems (which then don't work most of the time), Mistral Large 2 is a master in the shell and gives just the commands you need. However, for other coding tasks, it is not as good as Sonnet.
- **Gemini (Flash)** for tedious tasks and data cleanup. It is really fast, is able to handle text, images, audio and video as inputs and it is really cheap[^gemini]. [This](https://simonwillison.net/2024/Oct/17/video-scraping/) post from Simon Willison is a perfect example of easy data cleaning possible by such models.

As an honorable mention, **DeepSeek Coder v2** is a strong, open model which is just behind the frontier[^deepseek].
The default model in ChatGPT, **GPT-4o**,  is not as strong as the competition, especially when compared against Sonnet. It also has a year-old knowledge cutoff date (October 2023), which makes it even less useful when compared to the model by Anthropic.

While these are my impressions, which seems to be largely the impressions by the general community, they are mostly backed by _vibes_, i.e., the usage of said models, as benchmarks like [LM Arena](https://lmarena.ai/) or [HumanEval](https://evalplus.github.io/leaderboard.html) can be gamed and might not catch nuances or your individual use case. That said, some benchmarks to keep an eye on are [LiveCodeBench](https://livecodebench.github.io/leaderboard.html), which use Python coding problems from sites like Leetcode published after a certain date (to avoid testing LLMs on data they have already seen), and [SEAL](https://scale.com/leaderboard/coding), which is a non-public benchmark of various programming problems and languages.

## Applications to access LLMs

To access the models, there are two different categories of applications relevant for developers: Websites and IDEs/Extensions for existing editors.

### Websites

This is probably the first contact anyone has with LLMs, with the most used site being ChatGPT. Every model maker has its own chat website, Anthropic has [Claude.ai](https://claude.ai/) for their models, Mistral has [Le Chat](https://chat.mistral.ai/chat), while Google has [Gemini](https://gemini.google.com/) for consumers and [Google AI Studio](https://aistudio.google.com/) aimed at developers. Both ChatGPT and Claude offer a premium subscription for \$20/mo, which lets you access better models or increase the rate limit of certain features. As we move from simple LLM chat frontends to applications, these sites are starting to offer features to differentiate them to the rest, such as image generation, code execution or the generation of [small websites](https://support.anthropic.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them). However, the models deployed on the websites might offer a different experience compared to access through the API. As an example, the 4o models in ChatGPT are restricted to 32K context length, despite the models being capable of working with 128K context. Also, models have a “system prompt”, a prompt which tells them what they can do and how they should behave[^system-prompt], which influences how the model behaves and thus could give you a different experience compared to accessing the same model through the API.

If you want to access multiple models for one subscription price at once, you can also use services which aggregate these subscriptions, such as [Kagi](https://kagi.com/pricing), which offers it alongside their search engine in the $25/mo tier or [Poe](https://poe.com/), which offers access to all LLMs and a lot of image and video generation models for \$20/mo. These services access the models through the respective APIs, but may set their own restrictions and system prompts.

### IDEs & Extensions

As the most development happens inside IDEs and editors, it comes to no surprise that a lot of different extensions are available to boost the productivity of coders. The oldest feature, which most developers should be familiar with, is the full line completion offered by extensions like GitHub Copilot, where specialized models try to complete the current line/function and offers suggestions. In my personal usage, I found both Copilot and the local models in the [JetBrains suite](https://plugins.jetbrains.com/plugin/14823-full-line-code-completion) rather lacking, with suggestions being rather subpar or unreliable. This might change with the introduction of new models; GitHub Copilot will offer access to [different models, including Sonnet](https://github.blog/news-insights/product-news/bringing-developer-choice-to-copilot/), while JetBrains has developed their own model, [Mellum](https://blog.jetbrains.com/blog/2024/10/22/introducing-mellum-jetbrains-new-llm-built-for-developers/). At the moment, I use [Supermaven](https://supermaven.com/) in my IDEs, which is way faster than Copilot, while being *accurate enough* to be a help and not a distraction.

All mentioned extensions also offer a chat window inside the respective IDEs, which allow you to use the leading models inside the IDE and are more convenient than using the chat sites directly. A notable exception is [Cursor](https://www.cursor.com/), which is a fork of VSCode and offers a lot of functionality to access LLMs for refactoring or adding functions. The AI functions are more deeply integrated into the editor compared to other solutions, so it has a bit of a learning code. I found the [post](https://www.arguingwithalgorithms.com/posts/cursor-review.html) from Tom Yedwab a good overview of Cursors' functions.

There are also tools for the command line, such as [aider](https://aider.chat/), which uses your API keys to edit files directly or [llm](https://github.com/simonw/llm), which allows the usage of LLMs directly in the shell. The latter is especially powerful when used with other utilities, such as [jq](https://simonwillison.net/2024/Oct/27/llm-jq/). As `llm` is written in Python, it can be used as a tool in uv, which I outlined in [my post](https://florianbrand.de/posts/uv-intro) with `uv tool install llm`.

## Prompting Methods for LLMs

Like mentioned previously, I found that most online tutorials / courses for prompting are aimed at people which developed AI applications and use LLMs as part of the software or scientists which want to leverage different techniques to get better results for the problems they are targeting and thus are not really applicable to the everyday problems programmers face. Here are some of the methods and tips I found the most useful when using LLMs for coding.

### Be specific and clear

This is probably the most important thing when prompting LLMs. You get better responses by being (overly) specific to what you want in what way. Some questions to ask yourself:

- What should the code to be generated accomplish?
- What is my input, what are the types of the variables? Can you provide some representative inputs? The same applies to outputs.
- What is the coding style I want? Should it be object-oriented or rather functional? Should it follow PEP strictly? Do I want type hints?

Also, you should describe _how_ the problem should be solved. This can be done with generic instructions, like the following[^espanso]:

```
<YOUR PROBLEM DESCRIPTION HERE>

First, I want you to think about the requirements of the function.
Then, plan out the steps you need to take to solve the problem.
Finally, write the code using clean, pythonic code by leveraging the language's latest features.
```

This is known as _(zero-shot) chain-of-thought prompting_, with the most "implementations" using "Let's think step by step." instead of the prompt above. Here is an excerpt of Claude's system prompt (emphasis mine):

```
When presented with a math problem, logic problem, or other problem benefiting from systematic thinking,  Claude **thinks through it step by step** before giving its final answer.
```

This yields better results compared to just asking for a solution. If you can be more specific about the problems and specific steps to solve the problem, this improves the quality of the solution even more. In general, you want _longer_ outputs from the model for most coding problems. Problems which require not a lot of "thinking" can be solved without such long prompts. Examples for such problems are the formatting of code, adding type hints or porting from well-known APIs to another one (e.g. from `requests` to `urllib` to get rid of external dependencies).

You also want to remove any ambiguity in the prompt, as the LLM then needs to make an assumption what you meant.
For example, this prompt is ambiguous:

```
Generate a GUI with a colored background and a big button in the center. 
It should be green.
```

In this prompt, the _coreference_ "it" is ambiguous, as it could refer to either the background or the button.
A better prompt would be to resolve this reference, removing the ambiguity and making the prompt clearer:

```
Generate a GUI with a colored background and a big button in the center. 
The button should be green.
```


### Formatting

Another crucial technique is the formatting of prompts.  In practice, you want to format your prompts close to StackOverflow questions and GitHub discussion, i.e., written in English, with the content being formatted as markdown, with code being inside triple backticks and **the context/code being first, followed by the question**.  Use headlines (`# Headline`) to show the model what is of importance and add structure to the prompt.  When prompting Claude, [use XML tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) to structure your prompt.  You can also mix XML tags with markdown formatting, for example like this:

````
I have this polars code which I want to rewrite using the Lazy API:
```python
(
	df
	.read_csv("data.csv")
	.select(  
            [  
                pl.col("Name").str.to_lowercase(),  
                pl.col("Age").round(2)  
            ]  
        )
)
```

Here are the docs for the Lazy API:
<docs>
# Usage

With the lazy API, Polars doesn't run each query line-by-line but instead processes the full query end-to-end. 
To get the most out of Polars it is important that you use the lazy API because:

- the lazy API allows Polars to apply automatic query optimization with the query optimizer
- the lazy API allows you to work with larger than memory datasets using streaming
- the lazy API can catch schema errors before processing the data

Here we see how to use the lazy API starting from either a file or an existing DataFrame.
[Rest of the docs]
</docs>

Rewrite the code into the lazy style given the docs.
````

### Limit the size of your prompt

While context lengths are improving continuously, they still struggle to effectively use the whole context. Therefore, you want to limit the information you use as input in your prompts. Avoid pasting a whole log file, the complete code base or the giant stack trace and instead focus on the relevant parts to your problem. That also applies to your chat session: The longer it goes on, the less accurate the model becomes. If the model is stuck with an error, you should start a new chat, summarize the problem and start from scratch. I do this after the model produces two errors in a row, i.e., when my chat looks like this:
```
Me: <Initial Prompt>
LLM: <Code with Bug>
Me: <Error/Stack Trace>
LLM: <"Fixed" Code with the same Bug>
Me: <Error/Stack Trace>
LLM: <"Fixed" Code with the same Bug>
```
At this point, I'd start a new chat session with either the initial prompt.


### LRMs need to be prompted different

Large Reasoning Models (LRMs) like o1 work differently from other LLMs, therefore they need to be prompting differently. They are using more compute resources after you have typed your prompt to come up with an answer. Therefore, you need to wait longer for a response by the model. You still want to be specific in your prompt, but you want to avoid _how_ the model should tackle the prompting. So while this is crucial for "normal" LLMs as mentioned previously, it actually [hurts the performance of o1](https://leehanchung.github.io/blogs/2024/10/08/reasoning-understanding-o1/). In my experience, o1 is not as a strong coder as Claude, but it can tackle coding problems which need a high-level overview and a deep dive into the problem. This sounds rather vague, so let me give you an example: We have a small GUI which displays some information in a panel and is also able to set some values.  This GUI is written in Tkinter and is around 600 LOC pure Python. o1 was able to rewrite the entire GUI into a streamlit application after some back and forth, with the end result improving upon the original GUI. All other LLMs, including 3.5 Sonnet, failed in various ways, even when pouring a lot of time into prompting and debugging.  However, o1 made some minor coding mistakes and also shares the knowledge cutoff with 4o of October 2023, so I needed to fix some small bugs manually or together with Claude. As a rule of thumb: When you give o1 a problem, and you need to wait >40s for a response, the problem is probably more suited for o1. Everything else is probably better suited for Claude. In my experience, LLMs like Claude can generate 300-500 LOC code with few to zero bugs from scratch, which is plenty for _a lot of scripts_, while o1 is able to generate 800-1000 LOC code within a chat session.

Another area where I prefer o1 over other LLMs is the explanation of code. This is purely subjective, but I prefer the deep dives and high-level overviews of o1 over explanations by other models. Again the knowledge cutoff of o1 will bite you if you work with cutting-edge libraries and you need to fall back to other models.

Overall, o1 is a very _strange_ model, which is harder to use than other LLMs in my experience. Therefore, you need to play around with the model even more to get a feeling when to use it and how to prompt it properly.

Right now, we are in the _GPT-3_ era of reasoning models in my opinion: A powerful model which works for a handful of domains, but is hard to use and remains niche for most people. This _could_ change with the release of the full o1, but it remains to be seen.

## Final Remarks

Like every other skill, you can only improve in using LLMs by actually using them and developing an intuition how to use them and their limitations. While doing this, I encourage you to collect prompts and problems which LLMs were unable to solve in a text file. When a new LLM releases, use these prompts to assess whether the new LLM improves on problems you care about.
Since the release of 3.5 Sonnet, I found myself writing a lot of simple scripts for automating things, be it python or small browser extensions in the form of Userscripts. Normally, these scripts would be a weekend project, but with LLMs, I finish them in an evening. I wouldn't want to miss them anymore.


[^jq]: See [llm-jq](https://github.com/simonw/llm-jq) for generating jq syntax
[^gemini]: If you use the easy-to-use API from [Google AI Studio](https://aistudio.google.com), you can use the API for free, but the data from the [free usage is used to train the models](https://ai.google.dev/pricing).
[^deepseek]: The newer DeepSeek v2.5 shows some regressions against the previous version.
[^system-prompt]: The system prompt for Claude can be accessed [here](https://docs.anthropic.com/en/release-notes/system-prompts#oct-22nd-2024)
[^espanso]: For this, a text expander like the inbuilt functionality in macOS or [espanso](https://espanso.org/) for every OS comes in handy. Save some of your most-used prompts with text shortcuts and re-use them easily.