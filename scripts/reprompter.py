import os
import contextlib
import gradio as gr

from openai import OpenAI

from modules import scripts, script_callbacks, shared
from modules.shared import opts, state

REPROMPTER = "Remprompter"

sys_prompt_file_path = os.path.join(scripts.basedir(), 'sys_prompt.txt')
with open(sys_prompt_file_path, 'r', encoding='UTF-8') as sys_prompt_file:
    sys_prompt = sys_prompt_file.read()

translate_sys_prompt_file_path = os.path.join(scripts.basedir(), 'translate_sys_prompt.txt')
with open(translate_sys_prompt_file_path, 'r', encoding='UTF-8') as translate_sys_prompt_file:
    translate_sys_prompt = translate_sys_prompt_file.read()

class RemprompterScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

        self.reprompter_ollama_host = shared.opts.data.get("reprompter_ollama_host", "")
        self.reprompter_ollama_model = shared.opts.data.get("reprompter_ollama_model", "")
        self.reprompter_ollama_key = shared.opts.data.get("reprompter_ollama_key", "")
        self.reprompter_ollama_use_history = shared.opts.data.get("reprompter_ollama_use_history", True)
        self.reprompter_use_positive_improvements = shared.opts.data.get("reprompter_use_positive_improvements", False)
        
    def title(self):
        return REPROMPTER

    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def make_reprompt(self, text):
        print("[{}][{}] Process text: {}".format(REPROMPTER, self.reprompter_ollama_model, text))
        try:
            client = OpenAI(
                base_url = self.reprompter_ollama_host,
                api_key=self.reprompter_ollama_key,
            )

            query_sys_prompt = sys_prompt if self.reprompter_use_positive_improvements else translate_sys_prompt

            request_content = [
            {
                'role': 'system',
                'content': query_sys_prompt,
            },
            {
                'role': 'user',
                'content': text,
            }]

            response = client.chat.completions.create(model=self.reprompter_ollama_model, messages=request_content)
            return response.choices[0].message.content
        
        except Exception as e:
            print("[{}] Error call ollama api: {}".format(REPROMPTER, repr(e)))
        return text    
    
    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion(REPROMPTER, open=False):
                text_to_reprompt = gr.Textbox(label="Prompt description, any language")
                send_text_button = gr.Button(value='Reprompt', variant='primary')
        
        with contextlib.suppress(AttributeError):  # Ignore the error if the attribute is not present
            if is_img2img:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt], outputs=[self.img2img])
            else:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt], outputs=[self.text2img])                

        return [text_to_reprompt, send_text_button]

    def on_ui_settings():
        section = ("reprompter", REPROMPTER)
        shared.opts.add_option("reprompter_ollama_host", shared.OptionInfo(
            "", "Ollama url", section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_ollama_model", shared.OptionInfo(
            "", "Ollama Model", section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_ollama_key", shared.OptionInfo(
            "", "Ollama API Key", section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_ollama_use_history", shared.OptionInfo(
            False, "Use context to edit a prompt on the fly",
            gr.Checkbox, {"interactive": True}, section=section).needs_reload_ui())
        shared.opts.add_option("reprompter_use_positive_improvements", shared.OptionInfo(
            True, "Utilize positive improvements",
            gr.Checkbox, {"interactive": True}, section=section).needs_reload_ui())

    script_callbacks.on_ui_settings(on_ui_settings)   
    
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.text2img = component

        if kwargs.get("elem_id") == "img2img_prompt":
            self.img2img = component