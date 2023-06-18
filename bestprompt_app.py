import json
from flask import Flask, render_template, request, jsonify
import openai
from openai.error import RateLimitError
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gpt4', methods=['GET', 'POST'])
def gpt4():
    user_input = request.args.get('user_input') if request.method == 'GET' else request.form['user_input']
    messages = [{
        "role": "system", "content":
            """
            Principle 1: Write clear and specific instructions
            Clear: clear doesn’t equal to short. If the prompt needs to be longer to be clear, do so. However being too verbose isn’t useful either.
            Tactic 1: Use delimiters
            Put the content you want the model to summarize / ingest into delimiters such as triple backticks.
            This also helps to avoid prompt injections, where users insert texts that go against our prompt and the model follows the user's prompt instead of our prompt.

            Tactic 2: Ask for structured output
            Specify the format and the length you want the output to be in, such as ‘JSON’, ‘250 characters’, ‘2 sentences’. For example:

            Generate a list of highest rated movies along with their director and lead actors. Provide this in JSON format with the following keys: movie, director, lead_actor.

            Tactic 3: Check whether conditions are satisfied
            Ask the model to check whether certain conditions or assumptions are met before taking actions. For example:

            You will be provided with some text. If it has a sequence of instructions, rewrite these instructions in step-by-step format.

            Tactic 4: Give the model some good examples (aka. Few Shot Learning)


            Principle 2: Give the model time to ‘think’
            Giving the model time does not only strictly mean physical time. It also includes:
            Breaking the task into smaller steps
            More iterations and giving model follow-up instructions
            Ask the model to spend more actual GPU time

            Tactic 1: specify steps to complete a task
            Tactic 2: Instruct the model to work out its own solution first before rushing to a conclusion
            """,
        "role": "user", "content": f"""
            Start a new conversation. Clear previous context.
            Step1: Improve the prompt below
            Step2: return chatgpt output from the improved prompt
            Provide your answer in JSON formwith keys named 'improved_prompt' and 'improved_output'. 
            Reply with only the answer in JSON form and include no other commentary.
            \n```json

            {user_input} """
        }]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        full_content = response.choices[0].message["content"]
        print(full_content)
        json_content = json.loads(full_content)
        content = json_content['improved_output']
    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."

    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True)