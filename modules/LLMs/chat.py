import re
import html
from aiogram import types as aiogram_types

async def nvidia_AI_chatting(message: aiogram_types.Message, SYSTEM_INSTRUCTION, nvidia_chat_client_1):
    try:
        completion = await nvidia_chat_client_1.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user",   "content": message.text},
            ],
            temperature=1,
            top_p=1,
            max_tokens=18384,
            extra_body={"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}},
            stream=True,
        )

        full_response = ""
        async for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                full_response += delta.content

        if full_response.strip():
            formatted = markdown_to_telegram_html(full_response)
            await _send_formatted(message, formatted)
        else:
            await message.answer("I couldn't generate a response. Please try again.")

    except Exception as e:
        print(f"NVIDIA AI error: {e}")
        await message.answer("Sorry, I had trouble processing that. Could you try again?")

async def deepseek_AI_chatting(message: aiogram_types.Message, SYSTEM_INSTRUCTION, nvidia_chat_client_2):
    try:
        completion = await nvidia_chat_client_2.chat.completions.create(
            model="deepseek-ai/deepseek-v3.2",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user",   "content": message.text},
            ],
            temperature=1,
            top_p=0.95,
            max_tokens=18000, # Increased to allow room for content after reasoning
            extra_body={"reasoning_budget": 16000, "chat_template_kwargs": {"thinking": True}},
            stream=True,
        )

        full_response = ""
        reasoning_response = ""
        
        async for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            delta = chunk.choices[0].delta
            
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                reasoning_response += reasoning
                
            if delta.content is not None:
                full_response += delta.content

        final_text = ""
        if reasoning_response.strip():
            reasoning_lines = reasoning_response.strip().split('\n')
            reasoning_block = "\n".join([f"> {line}" for line in reasoning_lines])
            final_text += f"> 🤔 **Thinking:**\n{reasoning_block}\n\n"
        
        final_text += full_response

        if final_text.strip():
            formatted = markdown_to_telegram_html(final_text)
            await _send_formatted(message, formatted)
        else:
            await message.answer("I couldn't generate a response. Please try again.")

    except Exception as e:
        print(f"DeepSeek AI error: {e}")
        await message.answer("Sorry, I had trouble processing that. Could you try again?")