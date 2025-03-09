import os
import json
import contextlib
import gradio as gr

from openai import OpenAI
from modules import scripts, script_callbacks, shared
from modules.shared import opts, state

REPROMPTER = "Remprompter"
BASE_DIR = scripts.basedir()

LAST_STATE_FILE_NAME = "last_state.json"
LAST_STATE_FILE_PATH = os.path.join(BASE_DIR, LAST_STATE_FILE_NAME)

def write_json_to_file(json_data, file_path: str):
    try:
        with open(file_path, "w") as file:
            file.write(json.dumps(json_data, indent=4))

    except Exception as e: 
        print("[{}] Error write to file: {}. {}.".format(REPROMPTER, file_path, repr(e)))

def load_json_to_file(file_path: str):
    data = None
    try:
        with open(file_path) as file:
            data = json.load(file)

    except Exception as e:
        print("[{}] Error load from to file: {}. {}.".format(REPROMPTER, file_path, repr(e)))
    
    if data is None:
        data = {
            "prefix": "",
            "postfix": "",
            "text": "",
            "prompt": ""
        }
    if "prefix" not in data:
        data["prefix"] = ""
    if "postfix" not in data:
        data["postfix"] = ""
    if "text" not in data:
        data["text"] = ""
    if "prompt" not in data:
        data["prompt"] = ""

    return data

class LLMOpenAIProvider():
    """A `LLMOpenAIProvider` is OpenAI API connector."""

    def __init__(self, host, model, key):
        self.host = host
        self.model = model
        self.key = key

    def call_llm(self, content):
        """"Call LLM model."""

        try:

            client = OpenAI( base_url = self.host, api_key=self.key, )
            response = client.chat.completions.create(model=self.model, messages=content)
            return response.choices[0].message.content

        except Exception as e:

            print("[{}] Error call openai api: {}".format(REPROMPTER, repr(e)))

        return None    

class PromptBuilder():
    """A `PromptBuilder` Creates a promt from user input text in any language."""

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.__read_prompts()
        self.use_context_enabled = False
        self.use_improvements_enabled = True
        self.reset_context()

    def __read_prompts(self):
        """Read system prompts from files."""
        sys_prompt_file_path = os.path.join(BASE_DIR, 'sys_prompt.txt')
        with open(sys_prompt_file_path, 'r', encoding='UTF-8') as sys_prompt_file:
            self.sys_prompt = sys_prompt_file.read()
        
        translate_sys_prompt_file_path = os.path.join(BASE_DIR, 'translate_sys_prompt.txt')
        with open(translate_sys_prompt_file_path, 'r', encoding='UTF-8') as translate_sys_prompt_file:
            self.translate_sys_prompt = translate_sys_prompt_file.read()

    def use_context(self, enable):
        """Enables or disables the use of context for LLMs."""

        self.use_context_enabled = enable
        if not self.use_context_enabled:
            self.reset_context()

    def use_improvement(self, enable):
        """Enables or disables the reworking and enhancement of promt text."""

        self.use_improvements_enabled = enable

    def reprompt(self, prefix, text, postfix):
        """Creating a promt. If the service is unavailable from the LLM, the input text will be returned."""
        print("[{}] REPROMPT OPTIONS: Context: {}. Improvement: {}".format(REPROMPTER, self.use_context_enabled, self.use_improvements_enabled))

        if not self.use_context_enabled:
            self.reset_context()

        self.content.append({ 'role': 'user', 'content': text })        

        print("[{}] REPROMPT CONTENT: {}".format(REPROMPTER, self.content))

        responce = self.llm_provider.call_llm(self.content)

        prompt = text

        if responce is not None:
            if self.use_context_enabled:
                self.content.append({ 'role': 'assistant', 'content': responce })
            prompt = responce

        last_state = {
            "prefix": prefix,
            "postfix": postfix,
            "text": text,
            "prompt": prefix + prompt + postfix
        }

        write_json_to_file(last_state, LAST_STATE_FILE_PATH)

        return prefix + prompt + postfix

    def reset_context(self):
        """Resetting the LLM context."""

        self.content = []
        
        # append system prompt
        if self.use_improvements_enabled:
            self.content.append({ 'role': 'system', 'content': self.sys_prompt })
        else:
            self.content.append({ 'role': 'system', 'content': self.translate_sys_prompt })

class RemprompterScript(scripts.Script):
    """A `RemprompterScript` main extension script for WebUI."""

    def __init__(self) -> None:
        super().__init__()

        reprompter_openai_host = shared.opts.data.get("reprompter_openai_host", "")
        self.reprompter_openai_model = shared.opts.data.get("reprompter_openai_model", "")
        reprompter_openai_key = shared.opts.data.get("reprompter_openai_key", "")

        llm_provider = LLMOpenAIProvider(reprompter_openai_host, self.reprompter_openai_model, reprompter_openai_key)
        self.prompt = PromptBuilder(llm_provider)        

    def __update_parameters(self, checkboxGroup):
        """Updates the flags responsible for using context for LLM and for text enhancement."""
        use_context = False
        use_improvement = False
        for p in checkboxGroup:
            if "context" in p:
                use_context = True
            if "improvement" in p:
                use_improvement = True
        self.prompt.use_context(use_context)
        self.prompt.use_improvement(use_improvement)

    def title(self): return REPROMPTER

    def show(self, is_img2img): return scripts.AlwaysVisible
    
    def make_reprompt(self, text, prefix, postfix): 
        print("[{}][{}] Process text: {}".format(REPROMPTER, self.reprompter_openai_model, text))
        return self.prompt.reprompt(prefix, text, postfix)

    def ui(self, is_img2img):

        choices = ["Use context", "Use improvement"]
        state = load_json_to_file(LAST_STATE_FILE_PATH)
        print("[{}] State: {}".format(REPROMPTER, state))
        with gr.Group():
            with gr.Accordion(REPROMPTER, open=False):                

                prompt_prefix = gr.Textbox(value = lambda: state["prefix"])
                prompt_prefix.label = "Prompt prefix"
                gr.HTML("<br style='margin-top: 10px;'>")

                prompt_postfix = gr.Textbox(value = lambda: state["postfix"])
                prompt_postfix.label = "Prompt postfix"
                gr.HTML("<br style='margin-top: 10px;'>")

                text_to_reprompt = gr.Textbox(value = lambda: state["text"])
                text_to_reprompt.label = "Prompt description, any language"
                gr.HTML("<br style='margin-top: 10px;'>")

                parameters = gr.CheckboxGroup(choices=choices, label="Query parameters", interactive = True, value = lambda: [choices[1]])
                gr.HTML("<br style='margin-top: 20px;'>")
                send_text_button = gr.Button(value='Reprompt', variant='primary')
       
        with contextlib.suppress(AttributeError):  # Ignore the error if the attribute is not present
            parameters.change(fn=self.__update_parameters, inputs=[parameters])
            if is_img2img:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt, prompt_prefix, prompt_postfix], outputs=[self.img2img])
            else:
                send_text_button.click(fn=self.make_reprompt, inputs=[text_to_reprompt, prompt_prefix, prompt_postfix], outputs=[self.text2img])

        return [prompt_prefix, prompt_postfix, text_to_reprompt, parameters, send_text_button]

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