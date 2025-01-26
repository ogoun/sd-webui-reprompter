# sd-webui-reprompter
Translates and augments text to create a prompt using ollama api. (Perhaps other api's will be added as well)

In the txt2img and img2img tabs, a tab appears in the accordion with the name Remprompter. 
In the tab there will be a text field where you can enter a description of the picture in any language. 
And Reprompt button, when clicked, the extension will request through ollama API to process the text from the text field. 
The result of the processing will be inserted into the prompt field for generation.

- Use context - if this flag is set, the history of requests will be saved, which will allow you to change the prompt by specifying the details. At the moment it does not work and is under development. To reset the context, all you need to do is clear the flag.
- Use improvement - when this flag is set, the system prompt is used to append the specified text. When the flag is unchecked, there will only be a translation.

![Reprompter extension](https://github.com/ogoun/ogoun/blob/main/images/reprompter/App.png)


#### Settings
On the settings page, on the Reprompter tab you can find the following settings:
- OpenAI API Host - api address, e.g. http://127.0.0.1:11434/v1.
- OpenAI API Model - model for text processing, e.g. phi4:14b.
- OpenAI API Key - authorization key, can be obtained in ollama web ui in your profile settings.

![Reprompter settings](https://github.com/ogoun/ogoun/blob/main/images/reprompter/settings.png)
