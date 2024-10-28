import speech_recognition as sr
from gtts import gTTS
import winsound
from pydub import AudioSegment
import pyautogui
from selenium import webdriver

def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        return None
    except sr.RequestError:
        print("Unable to access the Google Speech Recognition API.")
        return None

def respond(response_text):
    print(response_text)
    tts = gTTS(text=response_text, lang='en')
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)

tasks = []
listeningToTask = False

def main():
    global tasks
    global listeningToTask

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH
    driver.get("http://127.0.0.1:8000")

    while True:
        command = listen_for_command()

        if command:
            print(f"Command received: {command}")

 
            if "help me" in command:
                listeningToTask = True
                respond("Sure, How can i help you ?")
            elif "how are you" in command:
                listeningToTask = True
                respond("Im fine, Im here to to redirect you anywhere you want")
            
            elif "list tasks" in command:
                respond("Sure. Your tasks are:")
                for task in tasks:
                    respond(task)
            elif "take a screenshot" in command:
                pyautogui.screenshot("screenshot.png")
                respond("I took a screenshot for you.")
            elif "shop" in command:
                respond("Redirecting to shop.")
                driver.get("http://127.0.0.1:8000/shop")
            elif "cart" in command:
                respond("Redirecting to cart.")
                driver.get("http://127.0.0.1:8000/cart")
            elif "home" in command:
                respond("Redirecting to Home.")
                driver.get("http://127.0.0.1:8000")
            elif "previous page" in command:
                respond("Going back to the previous page.")
                driver.back()
            elif "exit" in command or "stop" in command or "goodbye" in command:
                respond("Goodbye!")
                break
            else:
                respond("Sorry, I'm not sure how to handle that command.")


if __name__ == "__main__":
    main()