# Example: the master prompt, filled in

````text
MAKE MY VIDEO

Use the script-to-video skill. You are my producer; I am the creative director.
Follow the skill's workflow exactly: correct anything below that breaks its rules (and tell me what you changed),
ask me only the questions I left blank, show me the full cost and a spending cap before anything is paid for,
and stop at every approval gate until I say "approved".

=== MY SCRIPT ===
Ever wondered why the sky is blue and not green or pink?
Sunlight looks white, but it is really every colour mixed together.
When it hits the air, tiny bits of air bounce the colours around.
Blue light is bounced the most, so blue reaches your eyes from every direction.
At sunset, light travels through much more air, so the reds and oranges win.
Now you know. Look up, and tell someone why!

=== MY ANSWERS (leave blank to be asked) ===
Length:                 30 s
Shape:                  vertical
Style:                  flat vector explainer
Still or animated:      still
Pictures:               I'll make them myself — give me a prompt for each
On screen:              nobody (scenes only)
Who speaks:             unseen narrator
Voice:                  AI voice, suggest one · English · normal pace
Music:                  new music — light, curious, soft synth and pizzicato
On-screen text:         subtitles
Audience & platforms:   general, ages 8+, TikTok + YouTube Shorts
Budget limit:           $0.50
Series:                 one-off
````

Expected quote (`plan_costs.py --seconds 30 --motion still --pictures own`): about **$0.12**
(voice about $0.04 + one music track $0.08); pictures made by you cost nothing here.
