import tkinter as tk
import aiml
import pandas as pd
from nltk.sem import Expression
from nltk.inference import ResolutionProver

class Chatbot(tk.Frame):
    def __init__(self, parent, kern, kb, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.kern = kern
        self.response_agent = "aiml"
        self.kb = kb

        # setup aiml kernel
        kern.setTextEncoding(None)
        kern.bootstrap(learnFiles="chatbot-logic.xml")

        # create tkiner window
        parent.title("Movie Chatbot")
        parent.geometry("400x500")
        parent.resizable(width=False, height=False)

        self.chat_window = tk.Text(parent, bd=1, bg="black",  width="50", height="8", font=("Calibri", 12), foreground="#00ffff")
        self.chat_window.place(x=6,y=6, height=385, width=370)
        self.chat_window.tag_config('bot', foreground="white")

        # greet user
        self.chat_window.insert("end", "Chatbot: " + "Hi! I'm Chatbot, how are you today?"+ "\n", "bot")

        self.message_window = tk.Text(parent, bd=0, bg="black",width="30", height="4", font=("Calibri", 14), foreground="#00ffff")
        self.message_window.place(x=128, y=400, height=88, width=260)

        self.scrollbar = tk.Scrollbar(parent, command=self.chat_window.yview, cursor="star")
        self.scrollbar.place(x=375,y=5, height=385)

        self.send_button = tk.Button(parent, text="Send",  width="12", height=5, command=self.on_click_send_button, bd=0, bg="#0080ff", activebackground="#00bfff",foreground='#ffffff',font=("Arial", 12))
        self.send_button.place(x=6, y=400, height=88)

    def get_gui_input(self):
        msg = self.message_window.get("1.0", "end")
        self.message_window.delete("1.0", "end")
        return msg

    def display_message_usr(self, msg):
        self.chat_window.insert("end", "You: " + msg)

    def display_message_bot(self, msg):
        self.chat_window.insert("end", "Chatbot: " + msg + "\n", "bot")

    def set_response_agent(self, agent):
        self.response_agent = agent

    def already_exists(self, expr):
        match = False
        for row in self.kb:
            if row == expr:
                match = True
        return match

    def contradicts_positive(self, object_, subject_):
        contradicts = False
        expr = read_expr('-' + subject_ + '(' + object_ + ')')
        if self.already_exists(expr):
            contradicts = True
        return contradicts

    def contradicts_negative(self, object_, subject_):
        contradicts = False
        expr = read_expr(subject_ + '(' + object_ + ')')
        if self.already_exists(expr):
            contradicts = True
        return contradicts

    def post_process(self):
        msg = self.get_gui_input()
        if self.response_agent == 'aiml':
            answer = kern.respond(msg)
        self.display_message_usr(msg)

        if answer[0] == '#':
            params = answer[1:].split('$')
            cmd = int(params[0])
            if cmd == 0:
                print(params[1])
                self.display_message_bot(params[1])
            elif cmd == 31:
                # "i know that * is *"
                object, subject = params[1].split(' is ')
                expr = read_expr(subject + '(' + object + ')')
                # check if already exists
                if not self.already_exists(expr):
                # check if contradicts
                    if not self.contradicts_positive(object, subject):
                        kb.append(expr)
                        self.display_message_bot("OK, I will remember that {object} is {subject}.".format(object=object, subject=subject))
                    else:
                        self.display_message_bot("This statement contradicts what I already know.")
                else:
                    self.display_message_bot("Statement already exists.")

            elif cmd == 32:
                # "check that * is *"
                object,subject=params[1].split(' is ')
                expr = read_expr(subject + '(' + object + ')')
                res = ResolutionProver().prove(expr, kb, verbose=True)
                if res:
                    self.display_message_bot("Correct.")
                else:
                    self.display_message_bot("Incorrect.") 

            elif cmd == 33:
                # "i know that * is not *"
                object, subject = params[1].split(' is ')
                expr = read_expr('-' + subject + '(' + object + ')')
                # check if already exists
                if not self.already_exists(expr):
                # check if contradicts
                    if not self.contradicts_negative(object, subject):
                        kb.append(expr)
                        self.display_message_bot("OK, I will remember that {object} is {subject}.".format(object=object, subject=subject))
                    else:
                        self.display_message_bot("This statement contradicts what I already know.")
                else:
                    self.display_message_bot("Statement already exists.")

            elif cmd == 99:
                self.display_message_bot("Sorry, I did not get that.")
        else:
            self.display_message_bot(answer)

    def on_click_send_button(self):
        self.post_process()

class ChatbotLogic():
    def __init__(self, kern):
        self.kern = kern
        self.input = ""

    def set_input(self, input):
        self.input = input

    def get_input(self):
        return self.input

if __name__ == "__main__":
    # initialize tkinter
    root = tk.Tk()
    # initialize aiml
    kern = aiml.Kernel()
    # get data from csv
    read_expr = Expression.fromstring
    kb=[]
    data = pd.read_csv('kb.csv', header=None)
    [kb.append(read_expr(row)) for row in data[0]]
    Chatbot(root, kern, kb)
    root.mainloop()