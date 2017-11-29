SLACK_BOT_TOKEN='XXXXXXX'

from slackclient import SlackClient
import time
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer



BOT_NAME = 'gloria'
BOT_ID='Xxxxxxxxx'
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ": do"

slack_client = SlackClient(SLACK_BOT_TOKEN)

def pregunta( texto,chatbot):
    """
        Receives the question and send to the chatbot recieved as parameter 
        returns back the reply from the bot.
    """
    print("This is the question" +  texto)
    reply = chatbot.get_response(texto)
    return reply



def handle_command(command, channel,chatbot):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print("handleing")
    response = pregunta(command,chatbot)
    respuesta= response.serialize()
    print respuesta['text']
    slack_client.api_call("chat.postMessage", channel=channel, text=respuesta['text'], as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.1  # 1 second delay between reading from firehose
    chatbot = ChatBot("Papa Noel"
                      , trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
                      , preprocessors=['chatterbot.preprocessors.clean_whitespace'],
                      logic_adapters=[
                          {
                              "import_path": "chatterbot.logic.BestMatch",
                              "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                              "response_selection_method": "chatterbot.response_selection.get_first_response"
                          },
                          {
                              'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                              'threshold': 0.65,
                              'default_response': 'I am sorry, but I do not understand.'
                          }
                      ]

                      )
    chatbot.train("chatterbot.corpus.english")
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,chatbot)
                print(command)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
