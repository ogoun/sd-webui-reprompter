import launch

if not launch.is_installed("openai"):
    launch.run_pip("install openai", "requirements for Reprompt")