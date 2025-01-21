# sd-webui-reprompter
Translates and augments text to create a prompt.

In the txt2img and img2img tabs, a tab appears in the accordion with the name Remprompter. 
In the tab there will be a text field where you can enter a description of the picture in any language. 
And Reprompt button, when clicked, the extension will request through ollama API to process the text from the text field. 
The result of the processing will be inserted into the reprompt field for generation.


#### Settings
On the settings page, on the Reprompter tab you can find the following settings:
- Ollama url - ollama api address, e.g. http://localhost:11434.
- Ollama Model - model for text processing, e.g. phi4:14b.
- Ollama API Key - authorization key, can be obtained in ollama web ui in your profile settings.
- Use context to edit a prompt on the fly - if this flag is set, the history of requests will be saved, which will allow you to change the prompt by specifying the details. At the moment it does not work and is under development.
- Utilize positive improvements - when this flag is set, the system prompt is used to append the specified text. When the flag is unchecked, there will only be a translation. It is currently not working and is under development. For now, a variant with source text completion is used.
