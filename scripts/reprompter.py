import os
import contextlib
import gradio as gr

from openai import OpenAI
from modules import scripts, script_callbacks, shared
from modules.shared import opts, state

REPROMPTER = "Remprompter"
BASE_DIR = scripts.basedir()

# OpenAPI connector
class LLMOpenAIProvider():
    def __init__(self, host, model, key):
        self.host = host
        self.model = model
        self.key = key

    def call_llm(self, content):
        client = OpenAI( base_url = self.host, api_key=self.key, )
        response = client.chat.completions.create(model=self.model, messages=content)
        return response.choices[0].message.content

class PromptBuilder():

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.__read_prompts()
        self.use_context_enabled = False
        self.use_improvements_enabled = True
        self.reset_context()

    def __read_prompts(self):

        sys_prompt_file_path = os.path.join(BASE_DIR, 'sys_prompt.txt')
        with open(sys_prompt_file_path, 'r', encoding='UTF-8') as sys_prompt_file:
            self.sys_prompt = sys_prompt_file.read()
        
        translate_sys_prompt_file_path = os.path.join(BASE_DIR, 'translate_sys_prompt.txt')
        with open(translate_sys_prompt_file_path, 'r', encoding='UTF-8') as translate_sys_prompt_file:
            self.translate_sys_prompt = translate_sys_prompt_file.read()

    def use_context(self, enable):
        self.use_context_enabled = enable
        if not self.use_context_enabled:
            self.reset_context()

    def use_improvement(self, enable):
        self.use_improvements_enabled = enable

    def reprompt(self, text):
        if not self.use_context_enabled:
            self.reset_context()
        self.content.append({ 'role': 'user', 'content': text, })
        
        return self.llm_provider.call_llm(self.content)

    def reset_context(self):
        self.content = []
        # append system prompt
        if self.use_improvements_enabled:
            self.content.append({ 'role': 'system', 'content': self.sys_prompt, })
        else:
            self.content.append({ 'role': 'system', 'content': self.translate_sys_prompt, })

class RemprompterScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

        reprompter_openai_host = shared.opts.data.get("reprompter_openai_host", "")
        self.reprompter_openai_model = shared.opts.data.get("reprompter_openai_model", "")
        reprompter_openai_key = shared.opts.data.get("reprompter_openai_key", "")

        llm_provider = LLMOpenAIProvider(reprompter_openai_host, self.reprompter_openai_model, reprompter_openai_key)
        self.prompt = PromptBuilder(llm_provider)        
        
    def title(self):
        return REPROMPTER

    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def make_reprompt(self, text):
        print("[{}][{}] Process text: {}".format(REPROMPTER, self.reprompter_openai_model, text))
        try:

            result = self.prompt.reprompt(text)
            return result
        
        except Exception as e:
            print("[{}] Error call openai api: {}".format(REPROMPTER, repr(e)))
        return text    
    
    def __update_use_context(self, checkbox):
        self.prompt.use_context(checkbox)

    def __update_use_improvement(self, checkbox):
        self.prompt.use_improvement(checkbox)

    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion(REPROMPTER, open=False):
                text_to_reprompt = gr.Textbox(label="Prompt description, any language")
                checkbox_use_context =  gr.Checkbox(label="Use context")
                checkbox_use_improvement =  gr.Checkbox(label="Use improvement", value=True,visible=True,)
                send_text_button = gr.Button(value='Reprompt', variant='primary')
        
        with contextlib.suppress(AttributeError):  # Ignore the error if the attribute is not present
            checkbox_use_context.change(fn=self.__update_use_context, inputs=[checkbox_use_context])
            checkbox_use_improvement.change(fn=self.__update_use_improvement, inputs=[checkbox_use_improvement])
            if is_img2img:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt], outputs=[self.img2img])
            else:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt], outputs=[self.text2img])                

        return [text_to_reprompt, checkbox_use_context, send_text_button]

    def on_ui_settings():
        section = ("reprompter", REPROMPTER)
        shared.opts.add_option("reprompter_openai_host", shared.OptionInfo(
            "", "OpenAI API Host", section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_openai_model", shared.OptionInfo(
            "", "OpenAI API Model", section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_openai_key", shared.OptionInfo(
            "", "OpenAI API Key", section=section).needs_reload_ui())

    script_callbacks.on_ui_settings(on_ui_settings)   
    
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.text2img = component

        if kwargs.get("elem_id") == "img2img_prompt":
            self.img2img = component