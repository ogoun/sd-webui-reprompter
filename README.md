# sd-webui-reprompter
Translates and augments text to create a prompt using ollama api. (Perhaps other api's will be added as well)

In the txt2img and img2img tabs, a tab appears in the accordion with the name Remprompter. 
In the tab there will be a text field where you can enter a description of the picture in any language. 
And Reprompt button, when clicked, the extension will request through ollama API to process the text from the text field. 
The result of the processing will be inserted into the reprompt field for generation.

![Reprompter extension](https://github.com/ogoun/ogoun/blob/main/images/reprompter/App.png)


#### Settings
On the settings page, on the Reprompter tab you can find the following settings:
- Ollama url - ollama api address, e.g. http://localhost:11434.
- Ollama Model - model for text processing, e.g. phi4:14b.
- Ollama API Key - authorization key, can be obtained in ollama web ui in your profile settings.
- Use context to edit a prompt on the fly - if this flag is set, the history of requests will be saved, which will allow you to change the prompt by specifying the details. At the moment it does not work and is under development.
- Utilize positive improvements - when this flag is set, the system prompt is used to append the specified text. When the flag is unchecked, there will only be a translation.

![Reprompter settings](https://github.com/ogoun/ogoun/blob/main/images/reprompter/settings.png)


#### Plans
1. Add support for other APIs.
2. Move checkboxes from settings to the main tab.
3. Finalize the use of query context.
