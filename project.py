from flask import Flask, request, render_template, jsonify, Response
import requests
import base64
import config
import openai
import os

app = Flask(__name__)

# OpenAI API Key
openai.api_key = config.API_KEY

conversation_history = []  # Define the conversation history variable

@app.route("/")
def home():
    return render_template("EduAi.html")

# Define other routes and functions here...


@app.route('/generate-image', methods=['POST'])
def generate_image():
    description = request.form['description']
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=description,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        print("after response")
        image_url = response.data[0].url
        #print(image_url)
        
        # Getting the image content from the URL
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            return Response(image_response.content, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Failed to fetch the generated image.'}), 500
			
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/get")
def get_bot_response():
    global conversation_history
    
    userText = request.args.get('msg')
    
    # Add user's message to conversation history
    conversation_history.append({
        "role": "user",
        "content": userText
    })
    
    # Generate response using ChatGPT with conversation history
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation_history,
    )
    
    # Get the response from ChatGPT
    answer = response.choices[0].message.content
    
    # Add ChatGPT's response to conversation history
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })
    
    return str(answer)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    audio = request.files['audio']
    filename = "user_audio.webm"
    audio_path = os.path.join(filename)
    audio.save(audio_path)

    with open(audio_path, "rb") as file:
        transcript = openai.audio.transcriptions.create(
          model="whisper-1",
          file=file,
          response_format="text"
        )
    print(transcript)
    #os.remove(audio_path)  # Optional: remove the file after processing

    return jsonify({"transcript": transcript}), 200

@app.route("/")
def index():
    return render_template("speech.html")

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data['text']
    voice = data.get('voice', 'alloy')  # Default voice is alloy

    # Experiment with different voices (alloy, echo, fable, onyx, nova, and shimmer)
    response = openai.Audio.create_speech(
        engine="tts-1",
        text=text,
        voice=voice
    )
    
    # Save the synthesized speech to file
    with open("synthesized.mp3", "wb") as f:
        f.write(response.audio)
    
	# just returns something to satisfy the call
	# from the web page. The page will just
	# retrive the file synthesized.mp3

    return jsonify("Success")

    

# flask --app project run --debug --host=0.0.0.0
# Go to Project -> Box Info -> Dynamic Content
# Change the next line to match your Dynamic Content
# https://togaballad-pinballruby-5000.codio.io/


if __name__ == "__main__":
    app.run(debug=True)
